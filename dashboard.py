import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

from src.extraction import extract_pdf_text
from src.matching import load_json, verify
from src.rag import retrieve_policy
from src.gemini import explain_with_gemini

load_dotenv()

st.set_page_config(page_title="InvoiceGuard AI", page_icon="🛡️", layout="wide")
st.title("🛡️ InvoiceGuard AI")
st.caption("3-way invoice verification: Invoice + Purchase Order + Goods Receipt + Policy RAG")

invoice_files = sorted(Path("data/invoices").glob("*.json"))
selected = st.selectbox("Choose a demo invoice", [p.name for p in invoice_files])

invoice_path = Path("data/invoices") / selected
invoice = load_json(str(invoice_path))
po = load_json(str(Path("data/purchase_orders") / f"{invoice['po_number']}.json"))
all_grns = [load_json(str(p)) for p in Path("data/grn").glob("*.json")]
grns = [g for g in all_grns if g.get("po_number") == invoice.get("po_number")]
if not grns:
    st.error("No matching GRN found for this purchase order.")
    st.stop()
grns = grns[0]
all_invoices = [load_json(str(p)) for p in invoice_files]

uploaded = st.file_uploader("Optional: upload an invoice PDF", type=["pdf"])
if uploaded:
    temp = Path("/tmp/invoiceguard_upload.pdf")
    temp.write_bytes(uploaded.read())
    text = extract_pdf_text(str(temp))
    st.subheader("Extracted invoice text")
    st.code(text)

result = verify(invoice, po, grns, all_invoices)
query = "invoice quantity unit price duplicate vendor purchase order goods receipt approval"
policies = retrieve_policy(query)

c1, c2, c3 = st.columns(3)
c1.metric("Risk", result["risk"])
c2.metric("Estimated exposure", f"₹{result['estimated_exposure']:,.0f}")
c3.metric("Policy matches", len(policies))

st.subheader("Verification checks")
for name, ok, detail in result["checks"]:
    st.write(("✅" if ok else "❌") + f" **{name}** — {detail}")

if result["issues"]:
    st.subheader("Risk flags")
    for issue in result["issues"]:
        st.error(issue)
else:
    st.success("No material mismatch detected.")

with st.expander("Retrieved procurement policy"):
    for p in policies:
        st.write(f"**{p['source']}** · similarity {p['score']:.3f}")
        st.write(p["text"])

st.subheader("AI risk explanation")
if st.button("Analyze with Gemini"):
    with st.spinner("Generating grounded explanation..."):
        explanation = explain_with_gemini(result, invoice, po, grns, policies)
    st.write(explanation)
else:
    st.info("Click **Analyze with Gemini** to generate the natural-language risk explanation. Add GEMINI_API_KEY for live AI output.")
