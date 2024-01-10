"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve 




urlpatterns = [
    path('artworks/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    path('admin/', admin.site.urls),
    path('',include('hello.urls')),
    path('home/', include('hello.urls')),
    path('login/', include('hello.urls')),
    path('register/',include('hello.urls')),
    path('logout/',include('hello.urls')),
    path('artist/', include('artist.urls')),
    path('artist_page/', include('artist.urls')),
    path('edit_profile/',include('artist.urls')),
    path('edit_profile/<int:artist_id>/', include('artist.urls')),
    path('draft_view/',include('artist.urls')),
    path('draft_view/<int:artist_id>/',include('artist.urls')),
    path('art_post/',include('art.urls')),
    path('art_post/<int:artist_id>/',include('art.urls')),
    path('gallery/',include('hello.urls')),
    path('delete_artwork/',include('artist.urls')),
    path('delete_draft',include('artist.urls')),
    path('investor_page',include('investor.urls')),
    path('art_details/',include('art.urls')),
    path('public_profile/',include('hello.urls')),
    path('purchase_art',include('art.urls')),
    path('place_bid',include('art.urls')),
    path('confirm_sale',include('art.urls')),
    path('investor_details',include('investor.urls')),
    path('sold_art_details',include('art.urls')),
    path('NFT_Bid',include('nfts.urls')),
    path('place_NFT_bid',include('nfts.urls')),
    path('confirm_NFT_sale',include('nfts.urls')),
    path('NFT_post',include('nfts.urls')),
    path('art_styles',include('hello.urls')),
    path('art_tags',include('art.urls')),
    path('add_to_watchlist',include('hello.urls')),
    path('watchlist',include('hello.urls')),
    path('filters',include('hello.urls')),
    path('search',include('hello.urls')),
    path('search_req',include('hello.urls')),
    path('art_gallery',include('art.urls')),
    path('nft_gallery',include('nfts.urls')),
    path('forgot_pass',include('hello.urls')),
    path('forgot_username',include('hello.urls')),
    path('reset_pass',include('hello.urls')),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)