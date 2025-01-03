# shortener/urls.py
from django.urls import path
from . import views

app_name = 'shortener'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('stats/', views.url_stats, name='stats'),

    # URL operations
    path('create/', views.create_url, name='create_url'),
    path('urls/<str:short_code>/delete/', views.delete_url, name='delete_url'),
    path('urls/<str:short_code>/qr-code/', views.generate_qr, name='generate_qr'),

    # API endpoints
    path('api/urls/', views.url_list_api, name='url_list_api'),
    path('api/urls/create/', views.create_url_api, name='create_url_api'),

    # Analytics
    path('urls/<str:short_code>/stats/', views.url_detail_stats, name='url_detail_stats'),

    # Redirect (keep this last to avoid conflicts)
    path('<str:short_code>/', views.redirect_to_original, name='redirect'),
]