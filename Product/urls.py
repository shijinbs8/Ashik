from django.urls import path
from .views import *

urlpatterns=[
    path('Add_Product/',Add_Product,name='Add_Product'),
    path('Add_Category/',Add_Category,name='Add_Category'),
    path('add-hsn/', Add_hsn_code, name='add_hsn_code'),
    path('Delete-Category<int:id>/',Delete_Category,name='Delete_Category'),
    path('Delete-Hsn<int:id>/',Delete_Hsn,name='Delete_Hsn'),
    path('Product_List/',Product_List,name='Product_List'),
    path("restock-medicine/", restock_medicine, name="restock_medicine"),
    path('Product_Settings/',Product_Settings,name='Product_Settings'),
    path('Add_Supplier/',Add_Supplier,name='Add_Supplier'),
    path("add-customer/", add_customer, name="add_customer"),
    path("add-bank-account/", add_bank_account, name="add_bank_account"),
    path('Customer-List/',Customer_List,name='Customer_List'),
    path("get-product-details/<int:product_id>/", get_product_details, name="get-product-details"),
    path('get-product-price/<int:product_id>/', get_product_price, name='get_product_price'),

    path('sales/',add_sales_invoice,name='add_sales_invoice'),
    path('Invoice_List/',invoice_list,name='invoice_list'),
    path("invoice/<int:bill_no>/", invoice_detail, name="invoice_detail"),
        path('sales-report/', sales_report, name='sales_report'),
        path('add_cashier',Add_Casheir,name='Add_Cashier'),
          path("drug-search/", drug_search, name="drug_search"),
    path("drug-suggestions/", drug_suggestions, name="drug_suggestions"),
    path("invoice/print/<int:bill_no>/",print_invoice, name="print_invoice"),
    path('Add-Tax,',Add_Tax,name='Add_Tax'),
    path('restock-report/',Restoke_History,name='Restoke_History')









]