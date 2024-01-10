from . import views
from django.urls import path


urlpatterns=[
    path('NFT_Bid',views.NFT_Bid,name='NFT_Bid'),
    path('place_NFT_bid',views.NFT_place_bid, name='place_NFT_bid'),
    path('confirm_NFT_sale/',views.confirm_nft_sale,name='confirm_NFT_sale'),
    path('nft_gallery',views.nft_gallery, name='nft_gallery')

]
