from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from appflix.forms import CustomUserCreationForm, EditProfileForm, PerfilForm
from appflix.models import Perfil


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Perfil.objects.get_or_create(usuario=user)
            messages.success(request, "Conta criada com sucesso.")
            return redirect("login")
    else:
        form = CustomUserCreationForm()

    return render(request, "auth/register.html", {"form": form})


@login_required
def editar_perfil(request):
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)
        perfil_form = PerfilForm(request.POST, request.FILES, instance=perfil)

        if form.is_valid() and perfil_form.is_valid():
            form.save()
            perfil_form.save()
            messages.success(request, "Perfil atualizado com sucesso.")
            return redirect("editar_perfil")
    else:
        form = EditProfileForm(instance=request.user)
        perfil_form = PerfilForm(instance=perfil)

    return render(
        request,
        "usuarios/editar_perfil.html",
        {
            "form": form,
            "perfil_form": perfil_form,
            "perfil": perfil,
        },
    )


@require_POST
@login_required
def excluir_conta(request):
    usuario = request.user
    logout(request)
    usuario.delete()
    messages.success(request, "Sua conta foi excluída com sucesso.")
    return redirect("home")