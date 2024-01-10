
from django.urls import path
from . import views

urlpatterns=[
    path('', views.art_details, name='art_details'),
    path('art_post/', views.art_post, name='art_post'),
    path('art_post/<int:artist_id>/', views.art_post, name='art_post'),
    path('draft_view/<int:artist_id>/', views.art_post, name='draft_view_art_post'),
    path('sold_art_details',views.sold_art_details,name='sold_art_details'),
    path('art_details/',views.art_details, name='art_details'),
    path('purchase_art/',views.purchase_art, name='purchase_art'),
    path('place_bid',views.place_bid,name='place_bid'),
    path('confirm_sale/',views.confirm_sale,name='confirm_sale'),
    path('art_tags/',views.art_tags,name='art_tags'),
    path('art_gallery',views.art_gallery, name='art_gallery'),



]