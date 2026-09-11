import json


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def verify(invoice, purchase_order, grn, all_invoices=None):
    issues = []
    checks = []

    vendor_ok = invoice["vendor_id"] == purchase_order["vendor_id"] == grn["vendor_id"]
    checks.append(("Vendor consistency", vendor_ok, f"Invoice={invoice['vendor_id']}, PO={purchase_order['vendor_id']}, GRN={grn['vendor_id']}"))
    if not vendor_ok:
        issues.append("Vendor mismatch across invoice, PO and GRN.")

    po_qty = purchase_order["quantity"]
    grn_qty = grn["received_quantity"]
    inv_qty = invoice["quantity"]
    qty_ok = inv_qty <= po_qty and inv_qty <= grn_qty
    checks.append(("Quantity match", qty_ok, f"Invoice={inv_qty}, PO={po_qty}, GRN received={grn_qty}"))
    if inv_qty > po_qty:
        issues.append(f"Invoice quantity ({inv_qty}) exceeds PO quantity ({po_qty}).")
    if inv_qty > grn_qty:
        issues.append(f"Invoice quantity ({inv_qty}) exceeds received quantity ({grn_qty}).")

    price_ok = invoice["unit_price"] <= purchase_order["unit_price"]
    checks.append(("Unit price match", price_ok, f"Invoice=₹{invoice['unit_price']:,.2f}, PO=₹{purchase_order['unit_price']:,.2f}"))
    if not price_ok:
        issues.append(f"Invoice unit price is ₹{invoice['unit_price'] - purchase_order['unit_price']:,.2f} above the PO price.")

    expected_total = round(inv_qty * invoice["unit_price"], 2)
    total_ok = abs(expected_total - invoice["subtotal"]) <= 1
    checks.append(("Subtotal arithmetic", total_ok, f"Expected=₹{expected_total:,.2f}, Invoice=₹{invoice['subtotal']:,.2f}"))
    if not total_ok:
        issues.append("Invoice subtotal does not match quantity × unit price.")

    duplicate = False
    if all_invoices:
        duplicate = sum(x.get("invoice_number") == invoice.get("invoice_number") for x in all_invoices) > 1
    checks.append(("Duplicate invoice", not duplicate, f"Invoice number={invoice['invoice_number']}"))
    if duplicate:
        issues.append(f"Duplicate invoice number detected: {invoice['invoice_number']}.")

    excess = max(0, inv_qty - min(po_qty, grn_qty)) * invoice["unit_price"]
    price_excess = max(0, invoice["unit_price"] - purchase_order["unit_price"]) * inv_qty
    estimated_exposure = round(excess + price_excess, 2)

    if not issues:
        risk = "LOW"
        action = "Approve subject to normal business controls."
    elif estimated_exposure >= 100000 or duplicate:
        risk = "HIGH"
        action = "Hold invoice and require manual procurement review."
    else:
        risk = "MEDIUM"
        action = "Route for manual review before payment."

    return {
        "risk": risk,
        "action": action,
        "issues": issues,
        "checks": checks,
        "estimated_exposure": estimated_exposure,
    }
