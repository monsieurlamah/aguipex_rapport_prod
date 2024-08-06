from django.urls import path
from userauths import views

urlpatterns = [
    path('inscription/', views.register_view, name='userauths-sign-up'),
    path('connexion/', views.login_view, name='userauths-sign-in'),
    path('deconnexion/', views.logout_view, name='userauths-sign-out'),
    path('profil/modification/', views.profil_update, name='userauths-profile-update'),
]