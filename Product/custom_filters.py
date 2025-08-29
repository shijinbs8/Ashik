from django import template

register = template.Library()

@register.filter
def sum_attribute(queryset, attribute):
    """
    Custom filter to sum up a specific attribute of a queryset.
    Usage: {{ sales_items|sum_attribute:"total_amount" }}
    """
    return sum(getattr(item, attribute, 0) for item in queryset)
