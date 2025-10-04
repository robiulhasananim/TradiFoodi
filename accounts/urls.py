from django.urls import path
from .views import BuyerRegisterView, LoginView, BuyerProfileView, ResetPasswordView

urlpatterns = [
    path('buyer/register/', BuyerRegisterView.as_view(), name='buyer-register'),
    path('buyer/login/', LoginView.as_view(), name='buyer-login'),
    path('buyer/profile/', BuyerProfileView.as_view(), name='buyer-profile'),
    path('buyer/reset-password/', ResetPasswordView.as_view(), name='buyer-reset-password'),
]
