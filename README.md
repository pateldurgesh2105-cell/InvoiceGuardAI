# InvoiceGuard AI

**3-Way Invoice Verification & Risk Analysis using RAG + Gemini**

InvoiceGuard AI is a practical procurement verification system that compares an invoice with its Purchase Order (PO) and Goods Receipt Note (GRN), retrieves relevant procurement policies, and uses Gemini to explain mismatches and risk.

## What it does

- Extracts text from invoice PDFs.
- Reads invoice, PO and GRN records from structured JSON files.
- Performs deterministic 3-way matching for vendor, quantities and prices.
- Checks duplicate invoice numbers.
- Retrieves relevant procurement policy using sentence embeddings.
- Uses Gemini to produce a grounded risk explanation and recommended action.
- Shows results in a Streamlit dashboard.

## Workflow

`Invoice PDF -> Text Extraction -> Invoice Fields -> Invoice + PO + GRN Matching -> Policy Retrieval -> Gemini Risk Explanation -> Dashboard`

## Tech Stack

Python, Streamlit, PyMuPDF, Sentence Transformers, scikit-learn, Google Gemini API, Pytest

## Run locally

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

Set your Gemini key when you want AI explanations:

```bash
GEMINI_API_KEY=your_key_here
```

Without an API key, the deterministic verification still runs and the dashboard shows a clear fallback explanation.

## Project structure

```text
InvoiceGuardAI/
├── dashboard.py
├── requirements.txt
├── .env.example
├── README.md
├── src/
│   ├── extraction.py
│   ├── matching.py
│   ├── rag.py
│   └── gemini.py
├── data/
│   ├── invoices/
│   ├── purchase_orders/
│   ├── grn/
│   └── policies/
└── tests/
    └── test_matching.py
```

## Demo scenario

The included demo data intentionally contains a mismatch: the invoice quantity is higher than the received quantity and the unit price is above the PO price. InvoiceGuard flags the issue and recommends human review.

> Demo documents are synthetic and created for portfolio/testing purposes.
