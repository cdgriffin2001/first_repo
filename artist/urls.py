from django.urls import path

from . import views



urlpatterns = [
    path('', views.artist_page, name='artist_page'),
    path('edit_profile/<int:artist_id>/', views.edit_profile, name='edit_profile_with_id'),
    path('draft_view/', views.draft_view, name='draft_view'),
    path('draft_view/<int:artist_id>/', views.draft_view, name='draft_view'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('delete_artwork',views.delete_artwork, name='delete_artwork'),
    path('delete_draft',views.delete_draft, name='delete_draft'),



]

