from src.matching import verify


def test_high_risk_mismatch():
    invoice = {"invoice_number":"INV-1","vendor_id":"V1","quantity":15,"unit_price":52000,"subtotal":780000}
    po = {"vendor_id":"V1","quantity":12,"unit_price":50000}
    grn = {"vendor_id":"V1","received_quantity":12}
    result = verify(invoice, po, grn, [invoice])
    assert result["risk"] == "HIGH"
    assert any("exceeds PO" in issue for issue in result["issues"])


def test_clean_invoice():
    invoice = {"invoice_number":"INV-2","vendor_id":"V1","quantity":10,"unit_price":12000,"subtotal":120000}
    po = {"vendor_id":"V1","quantity":10,"unit_price":12000}
    grn = {"vendor_id":"V1","received_quantity":10}
    result = verify(invoice, po, grn, [invoice])
    assert result["risk"] == "LOW"
    assert result["issues"] == []
