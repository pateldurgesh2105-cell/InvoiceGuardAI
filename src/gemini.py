import os
from google import genai


def explain_with_gemini(verification, invoice, purchase_order, grn, policies):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return fallback_explanation(verification)

    client = genai.Client(api_key=api_key)
    policy_text = "\n".join(f"[{p['source']}] {p['text']}" for p in policies)
    prompt = f"""
You are an accounts-payable risk analyst. Explain the verification result using ONLY the supplied facts and policy context.
Do not invent missing information. Be concise and practical.

VERIFICATION:
{verification}

INVOICE:
{invoice}

PURCHASE ORDER:
{purchase_order}

GOODS RECEIPT NOTE:
{grn}

RETRIEVED POLICY:
{policy_text}

Return four sections:
1. Decision
2. Why it was flagged
3. Evidence
4. Recommended next action
"""
    response = client.models.generate_content(model="gemini-3.7-flash", contents=prompt)
    return response.text


def fallback_explanation(verification):
    if verification["risk"] == "LOW":
        return "Decision: LOW RISK\n\nThe deterministic checks passed. No material mismatch was detected.\n\nRecommended next action: Approve subject to normal business controls."
    issues = "\n".join(f"- {x}" for x in verification["issues"])
    return f"Decision: {verification['risk']} RISK\n\nWhy it was flagged:\n{issues}\n\nEstimated exposure: ₹{verification['estimated_exposure']:,.2f}\n\nRecommended next action: {verification['action']}\n\nGemini explanation is disabled until GEMINI_API_KEY is configured."
