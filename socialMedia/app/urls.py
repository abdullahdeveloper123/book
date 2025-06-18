from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('home/', views.home, name='home'),
    path('add_dummy_books/', views.add_dummy_books, name='add_dummy_books'),
    path('details/<int:id>', views.detail, name='details'),
    path('search/', views.search, name='search'),
    path('save/', views.save, name='save'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    
]   