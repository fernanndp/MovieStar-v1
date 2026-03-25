from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.home, name="home"),
    path("filme/<str:filme_id>/", views.detalhes_filme, name="detalhes_filme"),
    path("filme/<str:filme_id>/review/adicionar/", views.adicionar_review, name="adicionar_review"),

    path("reviews/", views.minhas_reviews, name="minhas_reviews"),
    path("reviews/recentes/", views.reviews_recentes, name="reviews_recentes"),
    path("reviews/<int:review_id>/comentar/", views.comentar_review, name="comentar_review"),
    path("reviews/<int:review_id>/editar/", views.editar_review, name="editar_review"),
    path("reviews/<int:review_id>/excluir/", views.excluir_review, name="excluir_review"),

    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path("perfil/excluir/", views.excluir_conta, name="excluir_conta"),

    path("usuarios/", views.listar_usuarios, name="listar_usuarios"),
    path("usuarios/<str:username>/", views.perfil_publico, name="perfil_publico"),

    path("mensagens/", views.listar_conversas, name="listar_conversas"),
    path("mensagens/nova/<str:username>/", views.iniciar_conversa, name="iniciar_conversa"),
    path("mensagens/<int:conversa_id>/", views.abrir_conversa, name="abrir_conversa"),
    path("mensagens/<int:conversa_id>/excluir/", views.excluir_conversa, name="excluir_conversa"),

    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="auth/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)