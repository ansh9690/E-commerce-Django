from django.contrib import admin
from .models import Item, OrderItem, Order, Address, Payment, CouponCode, Refund


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'ordered',
        'being_delivered',
        'recieved',
        'refund_requested',
        'refund_granted',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon',
    ]

    search_fields = [
        'user__username',
        'ref_code'
    ]

    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon',
    ]

    list_filter = [
        'ordered',
        'being_delivered',
        'recieved',
        'refund_requested',
        'refund_granted'
    ]

    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_diplay = [
        'user',
        'pin_code',
        'address',
        'apartment_address',
        'country',
        'address_type',
        'default',
    ]
    list_filter = [
        'default',
        'address_type',
    ]
    search_fields = [
        'user',
        'address',
        'apartment_address',
        'country',
        'pin_code',
    ]


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
admin.site.register(CouponCode)
admin.site.register(Refund)
