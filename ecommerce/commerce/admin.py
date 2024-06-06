from django.contrib import admin

from django.contrib.auth.models import Permission
from django.template.response import TemplateResponse
from django.utils.html import mark_safe
from .models import *
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.urls import path
from django.db.models.functions import TruncMonth, TruncQuarter, TruncYear, ExtractMonth, ExtractQuarter, ExtractYear
from django.db.models import Count, Sum, Q, F


class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "is_active", "role", "get_store"]

    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = 'Active'

    def role(self, obj):
        return obj.get_role_display()
    role.short_description = 'Role'

    def get_store(self, obj):
        if obj.store:
            return obj.store.store_name
        else:
            return None
    get_store.short_description = 'Store'




class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "parent"]
    search_fields = ["parent__name", "name"]
    readonly_fields = ['category_image']

    def category_image(self, category):
        if category.image:
            return mark_safe('<img src="{url}" width="450" height="120" />'.format(url=category.image.url))


class StoreAdmin(admin.ModelAdmin):
    list_display = ["id", "store_name", "user", "active"]
    search_fields = ["store_name", "user__username"]
    readonly_fields = ['store_wallpaper', 'get_average_rating']

    def get_average_rating(self, obj):
        return obj.average_rating()

    get_average_rating.short_description = 'Average Rating'

    def average_rating(self, obj):
        return obj.average_rating()

    average_rating.short_description = 'Average Rating'


    def store_wallpaper(self, store):
        if store.wallpaper:
            return mark_safe('<img src="{url}" width="450" height="120" />'.format(url=store.wallpaper.url))



class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['preview_image']

    def preview_image(self, product):
        if product.image:
            return mark_safe('<img src="{url}" width="120" height="120" />'.format(url=product.image.url))
        else:
            return "No image selected"

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)
    class Meta:
        model = Product
        fields = '__all__'

class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "product_name", "category", "store", "price", "stock"]
    search_fields = ["product_name", "category__name", "store__store_name"]
    inlines = [ProductImageInline, ProductVariantInline]
    form = ProductForm
    readonly_fields = ['get_average_rating']

    def get_average_rating(self, obj):
        return obj.average_rating()

    get_average_rating.short_description = 'Average Rating'

    def average_rating(self, obj):
        return obj.average_rating()

    average_rating.short_description = 'Average Rating'

class CommerceAppAdminSite(admin.AdminSite):
    site_header = 'HỆ THỐNG QUẢN LÝ SÀN GIAO DỊCH THƯƠNG MẠI ĐIỆN TỬ'

    def get_urls(self):
        return [
            path('commerce-stats/', self.commerce_stats)
        ] + super().get_urls()

    def commerce_stats(self, request):
        total_stores = Store.objects.count()
        active_stores = Store.objects.filter(active=True).count()
        total_customers = User.objects.filter(role=User.CUSTOMER_ROLE).count()
        total_sellers = User.objects.filter(role=User.SELLER_ROLE).count()
        unconfirmed_sellers = User.objects.filter(role=User.SELLER_ROLE, is_active=False).count()

        monthly_total_sales = Order.objects.filter(order_status='completed').annotate(
            month=ExtractMonth('order_date')
        ).values('month').annotate(total_sales=Sum('total_amount')).order_by('month')

        monthly_store_sales = OrderDetail.objects.filter(order__order_status='completed').annotate(
            month=ExtractMonth('order__order_date'),
            store_name=F('product__store__store_name')
        ).values('month', 'store_name').annotate(total_sales=Sum('price')).order_by('month')

        monthly_paid_orders = Order.objects.filter(order_status='completed').annotate(
            month=ExtractMonth('order_date'),
            store_name=F('store__store_name')
        ).values('month', 'store_name').annotate(total_paid_orders=Count('id')).order_by('month')

        most_paid_orders_store = monthly_paid_orders.order_by('-total_paid_orders').first()

        lowest_sales_store = monthly_store_sales.order_by('total_sales').first()

        quarterly_total_sales = Order.objects.filter(order_status='completed').annotate(
            quarter=ExtractQuarter('order_date')
        ).values('quarter').annotate(total_sales=Sum('total_amount')).order_by('quarter')

        quarterly_store_sales = OrderDetail.objects.filter(order__order_status='completed').annotate(
            quarter=ExtractQuarter('order__order_date'),
            store_name=F('product__store__store_name')
        ).values('quarter', 'store_name').annotate(total_sales=Sum('price')).order_by('quarter')

        quarterly_paid_orders = Order.objects.filter(order_status='completed').annotate(
            quarter=ExtractQuarter('order_date'),
            store_name=F('store__store_name')
        ).values('quarter', 'store_name').annotate(total_paid_orders=Count('id')).order_by('quarter')

        most_paid_orders_store_quarter = quarterly_paid_orders.order_by('-total_paid_orders').first()

        lowest_sales_store_quarter = quarterly_store_sales.order_by('total_sales').first()

        yearly_total_sales = Order.objects.filter(order_status='completed').annotate(
            year=ExtractYear('order_date')
        ).values('year').annotate(total_sales=Sum('total_amount')).order_by('year')

        yearly_store_sales = OrderDetail.objects.filter(order__order_status='completed').annotate(
            year=ExtractYear('order__order_date'),
            store_name=F('product__store__store_name')
        ).values('year', 'store_name').annotate(total_sales=Sum('price')).order_by('year')

        yearly_paid_orders = Order.objects.filter(order_status='completed').annotate(
            year=ExtractYear('order_date'),
            store_name=F('store__store_name')
        ).values('year', 'store_name').annotate(total_paid_orders=Count('id')).order_by('year')

        most_paid_orders_store_year = yearly_paid_orders.order_by('-total_paid_orders').first()

        lowest_sales_store_year = yearly_store_sales.order_by('total_sales').first()

        context = {
            'total_stores': total_stores,
            'active_stores': active_stores,
            'total_customers': total_customers,
            'total_sellers': total_sellers,
            'unconfirmed_sellers': unconfirmed_sellers,
            'monthly_total_sales': monthly_total_sales,
            'monthly_store_sales': monthly_store_sales,
            'monthly_paid_orders': monthly_paid_orders,
            'most_paid_orders_store': most_paid_orders_store,
            'lowest_sales_store': lowest_sales_store,
            'quarterly_total_sales': quarterly_total_sales,
            'quarterly_store_sales': quarterly_store_sales,
            'quarterly_paid_orders': quarterly_paid_orders,
            'most_paid_orders_store_quarter': most_paid_orders_store_quarter,
            'lowest_sales_store_quarter': lowest_sales_store_quarter,
            'yearly_total_sales': yearly_total_sales,
            'yearly_store_sales': yearly_store_sales,
            'yearly_paid_orders': yearly_paid_orders,
            'most_paid_orders_store_year': most_paid_orders_store_year,
            'lowest_sales_store_year': lowest_sales_store_year,
        }

        return TemplateResponse(request, 'admin/admin-commerce-stats.html', context)



class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'store', 'product', 'quantity', 'price']
    search_fields = ['order__user__username', 'product__product_name']
    readonly_fields = ['order', 'store', 'product', 'quantity', 'price']

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'payment_method', 'amount', 'payment_date']
    list_filter = ['payment_method']
    search_fields = ['order__user__username', 'payment_method']
    date_hierarchy = 'payment_date'

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'store', 'order_date', 'total_amount', 'payment_method', 'order_status']
    list_filter = ['order_status', 'payment_method']
    search_fields = ['user__username', 'order_status']
    date_hierarchy = 'order_date'

class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "product", "store", "rating", "comment", "created_at", "active"]
    search_fields = ["user__username", "product__product_name", "store__store_name"]
    list_filter = ["active"]





admin.site = CommerceAppAdminSite('ecommerce')
admin.site.register(Review, ReviewAdmin)
admin.site.register(OrderDetail, OrderDetailAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Permission)

