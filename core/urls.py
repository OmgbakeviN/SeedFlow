from django.urls import path, include
from core.views import home
from . import views
from .views import project_list, create_project, project_detail,investor_dashboard, entrepreneur_dashboard, custom_login, signup, upload_kyc, kyc_pending, logout_view, update_profile, update_profile, investment
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path("signup/", signup, name="signup"),
    path("login/", custom_login, name="login"),
    path("upload-kyc/", upload_kyc, name="upload_kyc"),
    path("kyc-pending/", kyc_pending, name="kyc_pending"),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),  # Page de détail d'un projet
    path('projects/', project_list, name='project_list'),
    path('create-project/', create_project, name='create_project'),
    path('projects/', project_list, name='projects'),  
    path('projects/<int:project_id>/', project_detail, name='project_detail'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('emntrepreneur-dashboard/', entrepreneur_dashboard, name='entrepreneur_dashboard'),
    path("intveestor/dashboard/", investor_dashboard, name="investor_dashboard"),
    path("update-prnofile/", update_profile, name="update_profile"),
    path("payment/<int:project_id>",investment, name="investment"),
    path("logout/", logout_view, name="logout"),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)