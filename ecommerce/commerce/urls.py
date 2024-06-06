from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter





router = DefaultRouter()
router.register('store', views.StoreViewSet)
router.register(r'store-user/(?P<user_id>\d+)', views.StoreByUserViewSet, basename='store-by-user')
router.register('products', views.ProductViewSet, basename='product')
router.register('product-images', views.ProductImageViewSet, basename='product-image')
router.register('order', views.OrderViewSet, basename='order')
router.register(r'order-by-user', views.UserOrderViewSet, basename='order-by-user')
router.register('order-detail', views.OrderDetailViewSet, basename='order-detail')
router.register(r'pending-order-details', views.PendingOrderDetailViewSet, basename='pending-order-details')
router.register('payment', views.PaymentViewSet, basename='payment')
router.register('similar-products', views.SimilarProductViewSet, basename='similar-products')
router.register('seller-statistics', views.SellerStatisticsViewSet, basename='seller-statistics')
router.register('categories', views.CategoryViewSet)
router.register(r'products-category/(?P<category_id>\d+)', views.ProductByCategoryViewSet, basename='products-by-category')
router.register('user', views.UserViewSet)
router.register('review', views.ReviewViewSet)
router.register(r'productvariants', views.ProductVariantViewSet)
router.register(r'productvariants-product/(?P<product_id>\d+)', views.ProductvariantsByProductViewSet, basename='productvariants-by-product')
router.register(r'review-products/(?P<product_id>\d+)', views.ReviewsByProductViewSet, basename='reviews-by-product')
router.register(r'review-store/(?P<store_id>\d+)', views.ReviewsByStoreViewSet, basename='reviews-by-store')
router.register(r'product-images/item/(?P<product_id>\d+)', views.ImageByProductId, basename='image-by-product')
router.register(r'products-store/(?P<store_id>\d+)', views.ProductByStoreViewSet, basename='products-by-store')
urlpatterns = [
    path('', include(router.urls)),
]