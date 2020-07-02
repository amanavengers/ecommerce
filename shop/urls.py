from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name="ShopHome"),
    path('about/', views.about, name="AboutUS"),
    path('contact', views.contact, name="Contactus"),
    path('tracker/', views.tracker, name="Trackingstatus"),
    path('search/', views.search, name="Search"),
    path('productview/<int:id>', views.productview, name="prodview"),
    path('checkout/', views.checkout, name="Checkout"),
    path('sell/', views.SellView.as_view(), name="Sell")
]
