from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Category model for grouping medicines
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Unit model for measurement units (e.g., "Box," "Strip," "Bottle")
class Unit(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# Supplier model for storing supplier details
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)

    contact_info = models.TextField(blank=True, null=True)  # Address or contact details

    def __str__(self):
        return self.name


# HSN Code model for tax classification
class HSNCode(models.Model):
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.code
    

from django.db import models

# Salesman Model (if required)
class Salesman(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name
from django.db import models

# Bank Account Model
class BankAccount(models.Model):
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50, unique=True)
    beneficiary_name = models.CharField(max_length=255)
    ifsc_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

# Customer Model (Customer Master)
class Customer(models.Model):
    name = models.CharField(max_length=255, db_index=True)  # Indexed for fast search
    pin_code = models.CharField(max_length=6, db_index=True)  # Indexed PIN Code
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    credit_period = models.IntegerField(help_text="Credit period in days", default=30)  # Default 30 days

    # Foreign Key Relations
    salesman = models.ForeignKey(
        "Salesman", on_delete=models.SET_NULL, null=True, blank=True
    )
    bank_account = models.ForeignKey(
        BankAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name="customers"
    )

    address = models.TextField(null=True, blank=True)
    area = models.CharField(max_length=255, blank=True)  # Area of the customer
    route = models.CharField(max_length=255, blank=True)  # Route information
    district = models.CharField(max_length=255, blank=True)  # District
    state = models.CharField(max_length=255, blank=True)  # State
    country = models.CharField(max_length=50, default="India")  # Default India

    # GST and Business Information
    tin_no = models.CharField(max_length=15, blank=True, null=True, unique=True)  # Unique TIN
    gstin = models.CharField(max_length=15, blank=True, null=True, unique=True, db_index=True)  # Indexed
    dl_no = models.CharField(max_length=20, blank=True, null=True, unique=True)  # Unique DL Number

    # Contact Information
    contact = models.CharField(max_length=20, db_index=True)  # Indexed Contact Number
    email = models.EmailField(blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)

    active = models.BooleanField(default=True)  # Active Status

    def __str__(self):
        return self.name

# Product model (Medicine details)
class Product(models.Model):
    name = models.CharField(max_length=255)  # Medicine name
    medicine_type = models.ForeignKey(Category, on_delete=models.CASCADE)  # Medicine category
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)  # Unit of measurement
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Tax rate (CGST + SGST)
    cess = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Additional cess
    mrp = models.DecimalField(max_digits=10, decimal_places=2)  # Maximum Retail Price
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)  # Wholesale price
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)  # Retail price
    c_and_a_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # C and A price
    reorder_level = models.IntegerField(null=True)  # Threshold for reordering
    reorder_quantity = models.IntegerField(null=True)  # Quantity to reorder
    supplier_rate = models.DecimalField(max_digits=10, decimal_places=2)  # Rate from supplier
    location = models.CharField(max_length=255)  # Rack or location number
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)  # Supplier reference
    hsn_code = models.ForeignKey(HSNCode, on_delete=models.CASCADE)  # HSN code reference
    manufacturer_code = models.CharField(max_length=50, blank=True, null=True)  # Manufacturer code
    bar_code = models.CharField(max_length=50, blank=True, null=True)  # Bar code
    update_unit_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Updated unit cost

    # Stock-related fields
    stock_quantity = models.PositiveIntegerField(default=0)  # Available stock
    total_stock_added = models.PositiveIntegerField(default=0)  # Total stock ever added
    total_stock_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total money spent on restocking
    sold_quantity = models.PositiveIntegerField(default=0)  # Total quantity sold

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # Record creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Record update timestamp

    def __str__(self):
        return self.name

    def add_stock(self, quantity, cost_per_unit):
        """ Method to add stock and update relevant fields """
        self.stock_quantity += quantity
        self.total_stock_added += quantity
        self.total_stock_cost += quantity * cost_per_unit
        self.save()

    def sell_stock(self, quantity):
        """ Method to sell stock and update relevant fields """
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.sold_quantity += quantity
            self.save()
        else:
            raise ValueError(f"Not enough stock available for {self.name}.")


# Stock Restocking Model (Purchase Entry)
class StockEntry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_added = models.PositiveIntegerField()
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    restocked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # User who restocked
    restocked_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity_added * self.cost_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity_added} units restocked"


# Sale Model (For tracking product sales)
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    selling_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_sale_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    sold_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_sale_price = self.quantity_sold * self.selling_price_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity_sold} units sold"


# Signal to automatically update stock when restocking
@receiver(post_save, sender=StockEntry)
def update_stock_on_restock(sender, instance, created, **kwargs):
    if created:
        instance.product.add_stock(instance.quantity_added, instance.cost_per_unit)


# Signal to automatically update stock when selling
@receiver(post_save, sender=Sale)
def update_stock_on_sale(sender, instance, created, **kwargs):
    if created:
        instance.product.sell_stock(instance.quantity_sold)



class RestockHistory(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity_added = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    restocked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)  # Track supplier
    restock_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} restocked by {self.restocked_by} from {self.supplier}"
    

from django.db import models
from django.db import models
from django.core.exceptions import ValidationError

class SalesInvoice(models.Model):
    bill_no = models.AutoField(primary_key=True)
    bill_date = models.DateField(auto_now_add=True)
    invoice_no = models.IntegerField(unique=True, blank=True, null=True)
    invoice_date = models.DateTimeField(auto_now_add=True)

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    cashier = models.CharField(max_length=100, null=True, blank=True)
    is_local = models.BooleanField(default=True)
    is_interstate = models.BooleanField(default=False)
    billing_type = models.CharField(max_length=20, choices=[
        ('wholesale', 'Wholesale'),
        ('retail', 'Retail'),
        ('mrp', 'MRP'),
    ], default='mrp')

    # ✅ Snapshot totals
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    round_off = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Invoice {self.bill_no}"

    def save(self, *args, **kwargs):
        if self.invoice_no is None:
            last_invoice = SalesInvoice.objects.order_by('-invoice_no').first()
            self.invoice_no = (last_invoice.invoice_no + 1) if last_invoice else 1

        # Ensure only one of supplier or customer is set
        if self.supplier and self.customer:
            raise ValidationError("An invoice can have either a supplier or a customer, not both.")
        super().save(*args, **kwargs)

    def get_subtotal(self):
        return sum(item.amount for item in self.items.all())

    def get_discount_total(self):
        return sum(item.discount_amount for item in self.items.all())

    def get_tax_total(self):
        return sum(item.tax_amount for item in self.items.all())

    def get_grand_total(self):
        return sum(item.total_amount for item in self.items.all())


class SalesItem(models.Model):
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=255)
    hsn_code = models.CharField(max_length=50)
    batch = models.CharField(max_length=50, null=True, blank=True)
    exp_date = models.DateField(null=True, blank=True)
    unit = models.CharField(max_length=50)
    qty = models.PositiveIntegerField()
    free = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.FloatField(default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_percentage = models.FloatField(default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.amount = self.qty * self.price
        self.discount_amount = (self.amount * self.discount_percentage) / 100
        self.taxable_amount = self.amount - self.discount_amount
        self.tax_amount = (self.taxable_amount * self.tax_percentage) / 100
        self.total_amount = self.taxable_amount + self.tax_amount
        super().save(*args, **kwargs)


class Cashier(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Tax(models.Model):
    name = models.CharField(max_length=50)  # e.g., GST 5%, GST 18%
    percentage = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 5.00, 18.00

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"
