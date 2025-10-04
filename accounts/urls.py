from django.urls import path
from .views import RegisterView, LoginView, ProfileView, AdminOnlyView, SellerOnlyView, BuyerOnlyView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('admin-only/', AdminOnlyView.as_view(), name='admin-only'),
    path('seller-only/', SellerOnlyView.as_view(), name='seller-only'),
    path('buyer-only/', BuyerOnlyView.as_view(), name='buyer-only'),
]
