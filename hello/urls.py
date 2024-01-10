from django.urls import path

from . import views

urlpatterns = [
    path('',views.hello, name='hello'),
    path('home/', views.hello, name='home'),
    path('login/',views.login_view, name='login'),
    path('register/',views.register_view, name='register_view'),
    path('logout/',views.logout_view, name='logout'),
    path('gallery/',views.gallery, name='gallery'),
    path('public_profile/',views.public_profile, name='public_profile'),
    path('art_styles/',views.art_styles,name='art_styles'),
    path('add_to_watchlist/',views.add_to_watchlist,name='add_to_watchlist'),
    path('watchlist/',views.watchlist,name='watchlist'),
    path('filters/',views.filters,name='filters'),
    path('search/',views.search,name='search'),
    path('search_req/',views.search_req,name='search_req'),
    path('forgot_pass/',views.forgot_pass,name='forgot_pass'),
    path('forgot_username/',views.forgot_username,name='forgot_username'),
    path('reset_pass/',views.reset_pass,name='reset_pass'),



    
]