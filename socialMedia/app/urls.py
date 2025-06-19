from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('home/', views.home, name='home'),
    path('details/<int:id>', views.detail, name='details'),
    path('search/', views.search, name='search'),
    path('save/', views.save, name='save'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('remove_wishlist/', views.remove_wishlist, name='remove_wishlist'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('save_order/', views.save_order, name='save_order'), 

    
]   