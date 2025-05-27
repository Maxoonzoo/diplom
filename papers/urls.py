from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_results, name='search_results'),
    path('upload/', views.upload_paper, name='upload_paper'),
    path('moderate/', views.moderate_papers, name='moderate_papers'),
    path('approve/<int:paper_id>/', views.approve_paper, name='approve_paper'),
    path('reject/<int:paper_id>/', views.reject_paper, name='reject_paper'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('tag/<str:category>/', views.tag_list, name='tag_list'),
    path('paper/<int:paper_id>/', views.paper_detail, name='paper_detail'),
    path('language/', views.get_current_language, name='get_current_language'),
]