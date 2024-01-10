from django.urls import path

from . import views

urlpatterns = [
    path('', views.investor_page, name='investor_page'),
    path('investor_details',views.investor_details, name='investor_details'),
    path('NFT_post',views.NFT_post,name='NFT_post'),
    
]