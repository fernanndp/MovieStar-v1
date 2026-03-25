from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from appflix.forms import MensagemForm
from appflix.models import Conversa, Mensagem


def _ordenar_usuarios_para_conversa(usuario_a, usuario_b):
    if usuario_a.id > usuario_b.id:
        return usuario_b, usuario_a
    return usuario_a, usuario_b


def _obter_ou_criar_conversa(usuario_a, usuario_b):
    usuario_1, usuario_2 = _ordenar_usuarios_para_conversa(usuario_a, usuario_b)

    conversa, _ = Conversa.objects.get_or_create(
        user1=usuario_1,
        user2=usuario_2,
    )
    return conversa


@login_required
def listar_conversas(request):
    conversas_qs = (
        Conversa.objects.filter(Q(user1=request.user) | Q(user2=request.user))
        .select_related("user1", "user2")
        .annotate(
            total_mensagens=Count("mensagens"),
            nao_lidas=Count(
                "mensagens",
                filter=Q(mensagens__lida=False) & ~Q(mensagens__remetente=request.user),
            ),
        )
        .filter(total_mensagens__gt=0)
        .order_by("-atualizada_em")
    )

    conversas_data = []
    for conversa in conversas_qs:
        conversas_data.append(
            {
                "conversa": conversa,
                "outro_usuario": conversa.outro_usuario(request.user),
                "ultima_mensagem": conversa.ultima_mensagem(),
            }
        )

    return render(
        request,
        "chat/conversas.html",
        {
            "conversas_data": conversas_data,
        },
    )

@login_required
def iniciar_conversa(request, username):
    usuario_destino = get_object_or_404(User, username=username)

    if usuario_destino == request.user:
        messages.error(request, "Você não pode iniciar uma conversa com você mesmo.")
        return redirect("listar_usuarios")

    conversa = _obter_ou_criar_conversa(request.user, usuario_destino)
    return redirect("abrir_conversa", conversa_id=conversa.id)


@login_required
def abrir_conversa(request, conversa_id):
    conversa = get_object_or_404(
        Conversa.objects.select_related("user1", "user2"),
        id=conversa_id,
    )

    if request.user != conversa.user1 and request.user != conversa.user2:
        messages.error(request, "Você não tem acesso a esta conversa.")
        return redirect("listar_conversas")

    outro_usuario = conversa.outro_usuario(request.user)

    Mensagem.objects.filter(
        conversa=conversa,
        lida=False,
    ).exclude(remetente=request.user).update(lida=True)

    if request.method == "POST":
        form = MensagemForm(request.POST)
        if form.is_valid():
            mensagem = form.save(commit=False)
            mensagem.conversa = conversa
            mensagem.remetente = request.user
            mensagem.save()

            return redirect("abrir_conversa", conversa_id=conversa.id)
    else:
        form = MensagemForm()

    mensagens_chat = (
        conversa.mensagens.select_related("remetente")
        .all()
        .order_by("criada_em")
    )

    return render(
        request,
        "chat/chat.html",
        {
            "conversa": conversa,
            "outro_usuario": outro_usuario,
            "mensagens_chat": mensagens_chat,
            "form": form,
        },
    )
@require_POST
@login_required
def excluir_conversa(request, conversa_id):
    conversa = get_object_or_404(Conversa, id=conversa_id)

    if request.user != conversa.user1 and request.user != conversa.user2:
        messages.error(request, "Você não tem permissão para excluir esta conversa.")
        return redirect("listar_conversas")

    if not conversa.mensagens.exists():
        messages.info(request, "Só é possível excluir conversas que já tenham mensagens.")
        return redirect("abrir_conversa", conversa_id=conversa.id)

    conversa.delete()
    messages.success(request, "Conversa excluída com sucesso.")
    return redirect("listar_conversas")