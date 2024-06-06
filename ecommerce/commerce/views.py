
from django.db.models import Q, Sum, Count
from datetime import datetime
from django.http import HttpResponse
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from .models import *
from .serializers import UserSerializer, StoreSerializer, CategorySerializer, ProductSerializer, ProductImageSerializer,  ReviewSerializer, OrderSerializer, OrderDetailSerializer, PaymentSerializer, ProductVariantSerializer


# Create your views here.

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, ]

    def get_permissions(self):
        if self.action == 'current_user':
            return [permissions.IsAuthenticated()]
        elif self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action == 'update_current_user':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=False, methods=['get'])
    def current_user(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_current_user(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # Update user information
        user = serializer.save()

        # Update password if new_password provided
        new_password = request.data.get('new_password')
        if new_password:
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.data)



class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.filter(active=True)
    serializer_class = StoreSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated()]

class StoreByUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if user_id:
            return Store.objects.filter(user_id=user_id)
        return Store.objects.none()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['product_name', 'price', 'store__store_name', 'category__name']
    ordering_fields = ['product_name', 'price']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated()]


class ProductByStoreViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        store_id = self.kwargs.get('store_id')
        if store_id:
            return Product.objects.filter(store_id=store_id)
        return Product.objects.none()

class ProductByCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        if category_id:
            return Product.objects.filter(category_id=category_id)
        return Product.objects.none()

class SimilarProductViewSet(viewsets.ViewSet):
    def list(self, request):
        product_id = request.query_params.get('product_id')
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                similar_products = Product.objects.filter(
                    Q(category=product.category) | Q(product_name__icontains=product.product_name)
                ).exclude(id=product_id)[:5]
                # Lấy 5 sản phẩm cùng loại hoặc tên gần giống, loại trừ sản phẩm hiện tại
                serializer_class = ProductSerializer(similar_products, many=True)
                return Response(serializer_class.data)
            except Product.DoesNotExist:
                return Response({"message": "Product not found."}, status=404)
        else:
            return Response({"message": "Product ID is required."}, status=400)


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated()]



class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer

class ProductvariantsByProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductVariantSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        if product_id:
            return ProductVariant.objects.filter(product_id=product_id)
        return ProductVariant.objects.none()


class ImageByProductId(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        if product_id:
            return ProductImage.objects.filter(product_id=product_id)
        return ProductImage.objects.none()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(active=True)
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated()]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.filter(active=True)
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated()]


class UserOrderViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        user = request.user
        orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class ReviewsByProductViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]  # Có thể điều chỉnh quyền truy cập ở đây

    def list(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

class ReviewsByStoreViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]  # Có thể điều chỉnh quyền truy cập ở đây

    def list(self, request, store_id):
        reviews = Review.objects.filter(store_id=store_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

class PendingOrderDetailViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        user = request.user
        pending_order_details = OrderDetail.objects.filter(order__user=user, order__order_status='pending')
        serializer = OrderDetailSerializer(pending_order_details, many=True)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]



class SellerStatisticsViewSet(viewsets.ViewSet):
    def list(self, request):
        user = request.user
        store = Store.objects.filter(user=user).first()

        monthly_revenue = self.get_revenue_by_period(store, 'month')
        monthly_product_stats = self.get_product_stats(store, 'month')
        highest_revenue_product_month = self.get_highest_revenue_product(store, 'month')
        lowest_revenue_product_month = self.get_lowest_revenue_product(store, 'month')

        quarterly_revenue = self.get_revenue_by_period(store, 'quarter')
        quarterly_product_stats = self.get_product_stats(store, 'quarter')
        highest_revenue_product_quarter = self.get_highest_revenue_product(store, 'quarter')
        lowest_revenue_product_quarter = self.get_lowest_revenue_product(store, 'quarter')

        yearly_revenue = self.get_revenue_by_period(store, 'year')
        yearly_product_stats = self.get_product_stats(store, 'year')
        highest_revenue_product_year = self.get_highest_revenue_product(store, 'year')
        lowest_revenue_product_year = self.get_lowest_revenue_product(store, 'year')

        response_data = {
            'monthly_revenue': monthly_revenue,
            'monthly_product_stats': monthly_product_stats,
            'highest_revenue_product_month': highest_revenue_product_month,
            'lowest_revenue_product_month': lowest_revenue_product_month,
            'quarterly_revenue': quarterly_revenue,
            'quarterly_product_stats': quarterly_product_stats,
            'highest_revenue_product_quarter': highest_revenue_product_quarter,
            'lowest_revenue_product_quarter': lowest_revenue_product_quarter,
            'yearly_revenue': yearly_revenue,
            'yearly_product_stats': yearly_product_stats,
            'highest_revenue_product_year': highest_revenue_product_year,
            'lowest_revenue_product_year': lowest_revenue_product_year,
        }

        return Response(response_data)

    def get_revenue_by_period(self, store, period):
        today = datetime.now()
        filter_params = {'order__order_status': 'completed'}
        if period == 'month':
            filter_params['order__order_date__month'] = today.month
            filter_params['order__order_date__year'] = today.year
        elif period == 'quarter':
            quarter = (today.month - 1) // 3 + 1
            filter_params['order__order_date__quarter'] = quarter
            filter_params['order__order_date__year'] = today.year
        elif period == 'year':
            filter_params['order__order_date__year'] = today.year

        return OrderDetail.objects.filter(store=store, **filter_params).aggregate(total=Sum('price'))['total']

    def get_product_stats(self, store, period):
        today = datetime.now()
        filter_params = {'order__order_status': 'completed'}
        if period == 'month':
            filter_params['order__order_date__month'] = today.month
            filter_params['order__order_date__year'] = today.year
        elif period == 'quarter':
            quarter = (today.month - 1) // 3 + 1
            filter_params['order__order_date__quarter'] = quarter
            filter_params['order__order_date__year'] = today.year
        elif period == 'year':
            filter_params['order__order_date__year'] = today.year

        return OrderDetail.objects.filter(store=store, **filter_params).values('product__product_name').annotate(
            total_sales=Sum('quantity'), total_revenue=Sum('price'))

    def get_highest_revenue_product(self, store, period):
        today = datetime.now()
        filter_params = {'order__order_status': 'completed'}
        if period == 'month':
            filter_params['order__order_date__month'] = today.month
            filter_params['order__order_date__year'] = today.year
        elif period == 'quarter':
            quarter = (today.month - 1) // 3 + 1
            filter_params['order__order_date__quarter'] = quarter
            filter_params['order__order_date__year'] = today.year
        elif period == 'year':
            filter_params['order__order_date__year'] = today.year

        return OrderDetail.objects.filter(store=store, **filter_params).values('product__product_name').annotate(
            total_revenue=Sum('price')).order_by('-total_revenue').first()

    def get_lowest_revenue_product(self, store, period):
        today = datetime.now()
        filter_params = {'order__order_status': 'completed'}
        if period == 'month':
            filter_params['order__order_date__month'] = today.month
            filter_params['order__order_date__year'] = today.year
        elif period == 'quarter':
            quarter = (today.month - 1) // 3 + 1
            filter_params['order__order_date__quarter'] = quarter
            filter_params['order__order_date__year'] = today.year
        elif period == 'year':
            filter_params['order__order_date__year'] = today.year

        return OrderDetail.objects.filter(store=store, **filter_params).values('product__product_name').annotate(
            total_revenue=Sum('price')).order_by('total_revenue').first()


def index(request):
    return HttpResponse("e-commerce app")
