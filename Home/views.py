from django.shortcuts import render
from django.utils.timezone import now
from django.db.models import Sum
from django.shortcuts import render
from Product.models import *
# Create your views here.
def Home(request):
    today = now().date()  # Get today's date
    low_stock_products = Product.objects.filter(stock_quantity__lt=10)
    # Total Sold Quantity Today
    total_qty_today = SalesItem.objects.filter(invoice__invoice_date__date=today).aggregate(total_qty=Sum('qty'))['total_qty'] or 0

    # Total Cash Received Today
    total_cash_today = SalesInvoice.objects.filter(invoice_date__date=today).aggregate(total_cash=Sum('items__total_amount'))['total_cash'] or 0

    # Top 5 Medicines Sold Today
    top_medicines = (
        SalesItem.objects.filter(invoice__invoice_date__date=today)
        .values('item_name')
        .annotate(total_sold=Sum('qty'))
        .order_by('-total_sold')[:5]
    )

    # Customer with the Highest Billed Amount Today
    top_customer = (
        SalesInvoice.objects.filter(invoice_date__date=today, customer__isnull=False)
        .values('customer__name')
        .annotate(total_billed=Sum('items__total_amount'))
        .order_by('-total_billed')
        .first()
    )

    context = {
        'total_qty_today': total_qty_today,
        'total_cash_today': total_cash_today,
        'top_medicines': top_medicines,
        'top_customer': top_customer,
        "low_stock_products": low_stock_products
    }
    return render(request,'index.html',context)