from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_results, name='search_results'),
    path('upload/', views.upload_paper, name='upload_paper'),
    path('tags/<str:category>/', views.tag_list, name='tag_list'),
]