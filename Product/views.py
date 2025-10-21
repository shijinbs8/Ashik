from django.shortcuts import render,redirect
from Product.models import *
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import SalesInvoice
from django.db.models import Sum

from django.contrib import messages
from .models import Product, Category, Unit, Supplier, HSNCode


def Add_Category(request):
    
    if request.method == 'POST':
        category_name = request.POST.get('category')

        # Check if the category already exists
        if Category.objects.filter(name=category_name).exists():
            print('Already Exists')
        else:
            Category.objects.create(name=category_name)
        
    return redirect('Product_Settings')

def Add_hsn_code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        description = request.POST.get('description')

        # Check if the HSN code already exists
        if HSNCode.objects.filter(code=code).exists():
            print('HSN Code Already Exists')
        else:
            HSNCode.objects.create(code=code, description=description)

    return redirect('Product_Settings')  


def Add_Casheir(request):
    if request.method=="POST":
        name= request.POST.get('name')
        contact_info=request.POST.get('contact_info')

        if name and contact_info:
            Casheir.objects.create(name=name,ph_number=contact_info)
        else:
            print('NO Data')
    return redirect('Product_Settings')  


def Add_Supplier(request):
    if request.method=="POST":
        name= request.POST.get('name')
        contact_info=request.POST.get('contact_info')
        address=request.POST.get('address')
        if name and contact_info:
            Supplier.objects.create(name=name,contact_info=contact_info,address=address)
        else:
            print('NO Data')
    return redirect('Product_Settings')  
def Add_Tax(request):
    if request.method == "POST":
        tax_name = request.POST.get("tax_name")
        tax_percentage = request.POST.get("tax_percentage")
        wholesale_margin = request.POST.get("wholesale_margin")
        retail_margin = request.POST.get("retail_margin")

        if tax_name and tax_percentage:
            Tax.objects.update_or_create(
                id=1,  # Keep a single global Tax record
                defaults={
                    "name": tax_name,
                    "percentage": tax_percentage,
                    "wholesale_margin": wholesale_margin or 70,  # default fallback
                    "retail_margin": retail_margin or 80,        # default fallback
                }
            )
            messages.success(request, "Tax settings updated successfully!")
        else:
            messages.error(request, "Please fill in all required fields.")

    return redirect("Product_Settings")

def Delete_Category(request,id):
    data=get_object_or_404(Category,id=id)
    data.delete()
    return redirect('Product_Settings')

def Delete_Hsn(request,id):
    data=get_object_or_404(HSNCode,id=id)
    data.delete()
    return redirect('Product_Settings')




from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Category, Unit, Supplier, HSNCode, Tax


@transaction.atomic
def Add_Product(request):
    if request.method == "POST":
        try:
            # Extract raw data
            name = request.POST.get("name")
            medicine_type_id = request.POST.get("medicine_type")
            unit_id = request.POST.get("unit")
            tax_rate_input = request.POST.get("tax_rate")
            cess_input = request.POST.get("cess") or None
            mrp_input = request.POST.get("mrp")
            wholesale_price_input = request.POST.get("wholesale_price")
            retail_price_input = request.POST.get("retail_price")
            supplier_id = request.POST.get("supplier")
            hsn_code_id = request.POST.get("hsn_code")
            manufacturer_code = request.POST.get("manufacturer_code")
            bar_code = request.POST.get("bar_code")
            location = request.POST.get("location")
            stock_quantity_input = request.POST.get("stock_quantity")
            supplier_rate_input = request.POST.get("supplier_rate")

            # Convert decimals safely
            try:
                tax_rate = Decimal(tax_rate_input or "0.00")
                cess = Decimal(cess_input) if cess_input else None
                mrp = Decimal(mrp_input or "0.00")
                wholesale_price = Decimal(wholesale_price_input or "0.00")
                retail_price = Decimal(retail_price_input or "0.00")
                supplier_rate = Decimal(supplier_rate_input or "0.00")
            except InvalidOperation:
                messages.error(request, "Invalid number format in prices or tax fields.")
                return redirect("Add_Product")

            # Convert stock safely
            try:
                stock_quantity = int(stock_quantity_input or 0)
            except ValueError:
                messages.error(request, "Stock quantity must be an integer.")
                return redirect("Add_Product")

            # Fetch related objects safely
            medicine_type = get_object_or_404(Category, id=medicine_type_id)
            unit = get_object_or_404(Unit, id=unit_id)
            supplier = get_object_or_404(Supplier, id=supplier_id)
            hsn_code = get_object_or_404(HSNCode, id=hsn_code_id)

            # Create product inside atomic transaction
            Product.objects.create(
                name=name,
                medicine_type=medicine_type,
                unit=unit,
                tax_rate=tax_rate,   # Stored as percentage
                cess=cess,
                mrp=mrp,
                wholesale_price=wholesale_price,
                retail_price=retail_price,
                supplier=supplier,
                hsn_code=hsn_code,
                manufacturer_code=manufacturer_code,
                bar_code=bar_code,
                location=location,
                stock_quantity=stock_quantity,
                supplier_rate=supplier_rate,
                total_stock_added=stock_quantity,
                total_stock_cost=supplier_rate * stock_quantity,
            )

            messages.success(request, f"Product '{name}' added successfully!")
            return redirect("Add_Product")

        except Exception as e:
            # Rollback will happen automatically due to @transaction.atomic
            messages.error(request, f"Error adding product: {str(e)}")
            return redirect("Add_Product")

    # GET request → load form
    categories = Category.objects.all()
    units = Unit.objects.all()
    suppliers = Supplier.objects.all()
    hsn_codes = HSNCode.objects.all()
    tax = Tax.objects.first()  # fallback if you have only one tax setup

    return render(
        request,
        "Add_Product.html",
        {
            "categories": categories,
            "units": units,
            "suppliers": suppliers,
            "hsn_codes": hsn_codes,
            "tax": tax,
        },
    )


def Product_List(request):
    data=Product.objects.all()
    suppliers = Supplier.objects.all()  # Fetch all suppliers

    context={
        "data":data,
         "suppliers": suppliers
    }
    return render(request,'Product_List.html',context)




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from decimal import Decimal
from django.contrib.auth.decorators import login_required

@login_required
@csrf_exempt
def restock_medicine(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            medicine_id = data.get("medicine_id")
            restock_quantity = int(data.get("restock_quantity"))
            restock_cost = Decimal(data.get("restock_cost"))  
            restocked_by_id = data.get("restocked_by")  
            supplier_id = data.get("supplier_id")  # Supplier ID from frontend

            # Fetch restocker (User)
            restocked_by = request.user

            # Fetch supplier
            supplier = Supplier.objects.get(id=supplier_id)

            # Fetch product
            medicine = Product.objects.get(id=medicine_id)

            # Update stock
            medicine.stock_quantity += restock_quantity
            medicine.total_stock_added += restock_quantity
            medicine.total_stock_cost += restock_cost
            medicine.save()

            # Save restock history
            RestockHistory.objects.create(
                product=medicine,
                quantity_added=restock_quantity,
                total_cost=restock_cost,
                restocked_by=restocked_by,
                supplier=supplier  # Save supplier
            )

            return JsonResponse({"success": True, "new_stock": medicine.stock_quantity})

        except Product.DoesNotExist:
            return JsonResponse({"success": False, "error": "Medicine not found"})
        except Supplier.DoesNotExist:
            return JsonResponse({"success": False, "error": "Supplier not found"})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "Invalid user ID"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})

def Product_Settings(request):
    hsn=HSNCode.objects.all()
    cat=Category.objects.all()
    tax=Tax.objects.get(id=1)

    context={
            "hsn":hsn,
        "cat":cat,
        "tax":tax,
    }
    return render(request,'Product_settings.html',context)


from django.shortcuts import render, redirect
from .models import Customer, Salesman

def add_customer(request):
    if request.method == "POST":
        print(request.POST) 
        name = request.POST.get("name")
        pin_code = request.POST.get("pin_code")
        credit_limit = request.POST.get("credit_limit")
        credit_period = request.POST.get("credit_period")

        area = request.POST.get("area")
        route = request.POST.get("route")
        district = request.POST.get("district")
        state = request.POST.get("state")
        tin_no = request.POST.get("tin_no", "")
        gstin = request.POST.get("gstin", "")
        contact = request.POST.get("contact")
        email = request.POST.get("email", "")
        contact_person = request.POST.get("contact_person", "")
        active = request.POST.get("active") == "true"
        dl_no = request.POST.get("dl_no", "")
        address=request.POST.get("address","")
        bank_account_id = request.POST.get("bank_account")
     
        
        # Get bank account
        bank_account = BankAccount.objects.get(id=bank_account_id)
        print(bank_account)
        # Get bank account
  
   

        # Create and save the customer
        Customer.objects.create(
            name=name,
            pin_code=pin_code,
            credit_limit=credit_limit,
            credit_period=credit_period,

            area=area,
            route=route,
            district=district,
            state=state,
            country="India",
            tin_no=tin_no,
            gstin=gstin,
            contact=contact,
            email=email,
            contact_person=contact_person,
            active=active,
            dl_no=dl_no,
            address=address,
            bank_account=bank_account,
        )

        return redirect("add_customer")  # Redirect to customer list after adding

    salesmen = Salesman.objects.all()
    bank_accounts = BankAccount.objects.all()
    return render(request, "customer_add.html", {"salesmen": salesmen,"bank_accounts": bank_accounts})





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import BankAccount
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import BankAccount  # Import your model
from django.views.decorators.csrf import csrf_exempt  # If needed

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import BankAccount
from django.db.utils import IntegrityError  # Import for handling unique constraint error
from django.shortcuts import redirect
from django.contrib import messages
from .models import BankAccount
from django.db.utils import IntegrityError

def add_bank_account(request):
    if request.method == "POST":
        messages.get_messages(request).used = True  # Clears previous messages

        bank_name = request.POST.get("bank_name")
        account_number = request.POST.get("account_number")
        beneficiary_name = request.POST.get("beneficiary_name")
        ifsc_code = request.POST.get("ifsc_code")

        if bank_name and account_number and beneficiary_name and ifsc_code:
            try:
                BankAccount.objects.create(
                    bank_name=bank_name,
                    account_number=account_number,
                    beneficiary_name=beneficiary_name,
                    ifsc_code=ifsc_code
                )
                messages.success(request, "✅ Bank account added successfully!")
                return redirect("add_customer")  

            except IntegrityError:
                messages.error(request, "❌ This account number already exists. Please use a unique account number.")

        else:
            messages.error(request, "⚠️ All fields are required!")

    return redirect('add_customer')



def Customer_List(request):
    customer=Customer.objects.all()
    return render(request,'Customer_List.html',{'customer':customer})

def get_product_details(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        
        # Convert model objects to serializable format
        data = {
            "id": product.id,
            "name": product.name,
            "medicine_type": product.medicine_type.name,  # Convert to string
            "unit": product.unit.name,  # Convert to string
            "tax_rate": float(product.tax_rate),
            "cess": float(product.cess) if product.cess else None,
            "mrp": float(product.mrp),
            "wholesale_price": float(product.wholesale_price),
            "retail_price": float(product.retail_price),
            "supplier": product.supplier.name,  # Convert to string
            "hsn_code": product.hsn_code.code,  # Convert to string
            "stock_quantity": product.stock_quantity,
            "location": product.location,
            "created_at": product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": product.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

from django.shortcuts import render, redirect
from .models import SalesInvoice, SalesItem, Supplier
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import SalesInvoice, SalesItem, Product, Customer, Supplier
from decimal import Decimal, ROUND_HALF_UP
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction


@transaction.atomic
def add_sales_invoice(request):
    products = Product.objects.all()
    customers = Customer.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == "POST":
        try:
            customer_id = request.POST.get("customer")
            supplier_id = request.POST.get("supplier")
            billing_type = request.POST.get("billingType")

            customer = get_object_or_404(Customer, id=customer_id) if customer_id else None
            supplier = get_object_or_404(Supplier, id=supplier_id) if supplier_id else None

            if customer and supplier:
                messages.error(request, "Select either a Customer or a Supplier, not both.")
                return redirect("add_sales_invoice")
            if not customer and not supplier:
                messages.error(request, "Please select either a Customer or a Supplier.")
                return redirect("add_sales_invoice")
            if not billing_type:
                messages.error(request, "Please select a billing type (Wholesale, Retail, MRP).")
                return redirect("add_sales_invoice")

            # Create invoice object first
            invoice = SalesInvoice.objects.create(
                customer=customer if customer else None,
                supplier=supplier if supplier else None,
                cashier=request.POST.get("cashier"),
                is_local="local" in request.POST,
                is_interstate="interstate" in request.POST,
                billing_type=billing_type,
            )

            items = []
            subtotal = Decimal("0.00")
            gst_total = Decimal("0.00")

            item_ids = request.POST.getlist("item_name[]")
            qty_list = request.POST.getlist("qty[]")
            unit_list = request.POST.getlist("unit[]")
            discount_percentage_list = request.POST.getlist("discount_percentage[]")
            discount_amount_list = request.POST.getlist("discount_amount[]")

            # Take tax from Tax model
            tax = Tax.objects.first()
            tax_percentage = tax.percentage if tax else Decimal("0.00")

            for i in range(len(item_ids)):
                product = get_object_or_404(Product, id=item_ids[i])
                qty = int(qty_list[i]) if qty_list[i] else 0

                if product.stock_quantity < qty:
                    messages.error(request, f"Not enough stock for {product.name}. Available: {product.stock_quantity}, Requested: {qty}")
                    return redirect("add_sales_invoice")

                # ✅ Take price from Product model depending on billing type
                if billing_type.lower() == "mrp":
                    price = product.mrp
                elif billing_type.lower() == "wholesale":
                    price = product.wholesale_price
                else:
                    price = product.retail_price

                gross_total = price * qty

                # Discount
                discount_percentage = Decimal(discount_percentage_list[i]) if discount_percentage_list and discount_percentage_list[i] else Decimal("0.00")
                discount_amount = Decimal(discount_amount_list[i]) if discount_amount_list and discount_amount_list[i] else Decimal("0.00")

                if discount_percentage > 0:
                    discount_amount = (gross_total * discount_percentage / 100).quantize(Decimal("0.01"))

                net_total = gross_total - discount_amount

                # ✅ Tax calculation (no back calculation)
                taxable_amount = net_total
                gst_amount = (taxable_amount * tax_percentage / 100).quantize(Decimal("0.01"))
                cess_percentage = product.cess or Decimal("0.00")
                cess_amount = (taxable_amount * cess_percentage / 100).quantize(Decimal("0.01")) if cess_percentage > 0 else Decimal("0.00")

                total_tax_amount = gst_amount + cess_amount
                total_amount = taxable_amount + total_tax_amount

                subtotal += taxable_amount
                gst_total += total_tax_amount

                items.append(SalesItem(
                    invoice=invoice,
                    item_name=product.name,
                    hsn_code=product.hsn_code,
                    batch=request.POST.getlist("batch[]")[i] if "batch[]" in request.POST else None,
                    exp_date=request.POST.getlist("exp_date[]")[i] if "exp_date[]" in request.POST else None,
                    unit=unit_list[i] if i < len(unit_list) else "",
                    qty=qty,
                    free=int(request.POST.getlist("free[]")[i]) if "free[]" in request.POST and request.POST.getlist("free[]")[i] else 0,
                    price=price,
                    discount_percentage=discount_percentage,
                    discount_amount=discount_amount,
                    taxable_amount=taxable_amount,
                    tax_percentage=tax_percentage,
                    tax_amount=total_tax_amount,
                    total_amount=total_amount,
                    mrp=product.mrp,
                ))

                # Reduce stock
                product.sell_stock(qty)

            SalesItem.objects.bulk_create(items)

            # ✅ Totals
            grand_total = subtotal + gst_total
            rounded_grand_total = grand_total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            round_off = rounded_grand_total - grand_total

            invoice.subtotal = subtotal
            invoice.gst_total = gst_total
            invoice.round_off = round_off
            invoice.grand_total = rounded_grand_total
            invoice.save()

            messages.success(request, "Sales invoice added successfully!")
            return redirect("invoice_list")

        except Exception as e:
            messages.error(request, f"Error adding invoice: {e}")
            return redirect("add_sales_invoice")

    return render(request, "sales_invoice.html", {
        "products": products,
        "customers": customers,
        "suppliers": suppliers,
    })


def get_product_price(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    print('here')
    billing_type = request.GET.get("billingType")

    if billing_type == "wholesale":
        price = product.wholesale_price
    elif billing_type == "retail":
        price = product.retail_price
    else:
        price = product.mrp

    return JsonResponse({"price": price})


def invoice_list(request):
    # Fetch invoices with related items and precompute total_amount using annotate()
    invoices = SalesInvoice.objects.prefetch_related("items").annotate(
        total_amount=Sum("items__total_amount")
    ).order_by("-bill_no")

    # Pagination (Show 10 invoices per page)
    paginator = Paginator(invoices, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "invoice_list.html", {"page_obj": page_obj})

from django.shortcuts import render
from django.http import JsonResponse
from .models import SalesInvoice

def invoice_detail(request, bill_no):
    invoice = SalesInvoice.objects.filter(bill_no=bill_no).first()  # Avoids 404 error

    if not invoice:
        return JsonResponse({"error": "Invoice not found"}, status=404)

    items = invoice.items.all()

    # Calculate totals
    total_tax = sum(item.tax_amount for item in items)
    grand_total = sum(item.total_amount for item in items)
    total_without_tax = sum(item.total_amount - item.tax_amount for item in items)

    context = {
        "invoice": invoice,
        "items": items,
        "total_tax": total_tax,
        "grand_total": grand_total,
        "total_without_tax": total_without_tax,
    }
    return render(request, "invoice_detail.html", context)

from django.db.models import Sum
from datetime import datetime
def sales_report(request):
    start_date = request.GET.get('start_date', datetime.today().replace(day=1).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', datetime.today().strftime('%Y-%m-%d'))
    supplier_id = request.GET.get('supplier')
    customer_id = request.GET.get('customer')

    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

    filtered_invoices = SalesInvoice.objects.filter(bill_date__range=[start_date_obj, end_date_obj])

    # Apply filtering for either supplier or customer (but not both)
    if supplier_id and customer_id:
        return render(request, 'sales_report.html', {
            'error': "Please filter by either Supplier or Customer, not both."
        })
    elif supplier_id:
        filtered_invoices = filtered_invoices.filter(supplier_id=supplier_id)
    elif customer_id:
        filtered_invoices = filtered_invoices.filter(customer_id=customer_id)

    # Filter sales data from invoices
    sales_data = SalesItem.objects.filter(invoice__in=filtered_invoices).values(
        'item_name', 'unit'
    ).annotate(
        total_qty=Sum('qty'),
        total_amount=Sum('total_amount')
    ).filter(total_qty__gt=0).order_by('item_name', 'unit')

    context = {
        'sales_data': sales_data,
        'start_date': start_date,
        'end_date': end_date,
        'suppliers': Supplier.objects.all(),
        'customers': Customer.objects.all(),
        'selected_supplier': supplier_id,
        'selected_customer': customer_id
    }
    return render(request, 'sales_report.html', context)


import requests
from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.shortcuts import render
from django.http import JsonResponse

def drug_search(request):
    query = request.GET.get('q', '')
    drug_info = None

    if query:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            drug_info = {
                "title": data.get("title"),
                "description": data.get("description"),
                "extract": data.get("extract"),
                "thumbnail": data.get("thumbnail", {}).get("source")
            }

    return render(request, "drug_search.html", {
        "query": query,
        "drug_info": drug_info
    })


def drug_suggestions(request):
    term = request.GET.get("term", "")
    suggestions = []
    if term:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "opensearch",
            "search": term,
            "limit": 10,
            "namespace": 0,
            "format": "json"
        }
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            suggestions = data[1]  # list of suggested titles
    return JsonResponse(suggestions, safe=False)


def print_invoice(request, bill_no):
    invoice = get_object_or_404(SalesInvoice, bill_no=bill_no)
    items = SalesItem.objects.filter(invoice=invoice)

    context = {
        "invoice": invoice,
        "items": items,
    }
    return render(request, "invoice_print.html", context)


def Restoke_History(request):
    history = RestockHistory.objects.select_related('product', 'restocked_by', 'supplier').all().order_by('-restock_date')


    paginator = Paginator(history, 10)  # Show 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'restock_history.html', {'page_obj': page_obj})