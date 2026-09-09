from myapp.models import Customer, Invoice


def calculate_totals():
    totals = {}
    # N+1 query pattern
    for customer in Customer.objects.all():
        invoices = Invoice.objects.filter(customer=customer)
        totals[customer.id] = sum(invoice.total for invoice in invoices)
    return totals


def quadratic_match(items_a, items_b):
    output = []
    # O(n^2) nested loops
    for a in items_a:
        for b in items_b:
            if a["id"] == b["id"]:
                output.append((a, b))
    return output
