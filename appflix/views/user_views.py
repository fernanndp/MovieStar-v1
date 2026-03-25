from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Exists, OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from appflix.forms import ComentarioReviewForm
from appflix.models import ComentarioReview, Conversa, Review
from django.urls import reverse


@login_required
def minhas_reviews(request):
    reviews = (
        Review.objects.filter(usuario=request.user)
        .select_related("filme")
        .order_by("-data_criacao")
    )

    return render(
        request,
        "usuarios/minhas_reviews.html",
        {
            "reviews": reviews,
        },
    )


@login_required
def listar_usuarios(request):
    query = request.GET.get("q", "").strip()

    conversa_subquery = (
        Conversa.objects.filter(
            Q(user1=request.user, user2=OuterRef("pk")) |
            Q(user2=request.user, user1=OuterRef("pk"))
        )
        .filter(mensagens__isnull=False)
        .values("id")
        .distinct()[:1]
    )

    usuarios = User.objects.exclude(id=request.user.id)

    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    usuarios = (
        usuarios
        .annotate(
            total_reviews=Count("reviews"),
            media_avaliacoes=Avg("reviews__avaliacao"),
            conversa_existente=Exists(conversa_subquery),
            conversa_id=Subquery(conversa_subquery),
        )
        .order_by("username")
    )

    return render(
        request,
        "usuarios/usuarios.html",
        {
            "usuarios": usuarios,
            "query": query,
        },
    )


@login_required
def reviews_recentes(request):
    reviews = (
        Review.objects.select_related("usuario", "usuario__perfil", "filme")
        .prefetch_related("comentarios", "comentarios__usuario", "comentarios__usuario__perfil")
        .order_by("-data_criacao")
    )

    comentario_forms = {
        review.id: ComentarioReviewForm(prefix=f"review-{review.id}")
        for review in reviews
    }

    return render(
        request,
        "usuarios/reviews_recentes.html",
        {
            "reviews": reviews,
            "comentario_forms": comentario_forms,
        },
    )


@login_required
def perfil_publico(request, username):
    usuario = get_object_or_404(User, username=username)

    reviews = (
        Review.objects.filter(usuario=usuario)
        .select_related("filme")
        .order_by("-data_criacao")
    )

    resumo = reviews.aggregate(
        total_reviews=Count("id"),
        media_avaliacoes=Avg("avaliacao"),
    )

    conversa_existente = None
    if usuario != request.user:
        conversa_existente = (
            Conversa.objects.filter(
                Q(user1=request.user, user2=usuario) |
                Q(user2=request.user, user1=usuario)
            )
            .filter(mensagens__isnull=False)
            .distinct()
            .first()
        )

    return render(
        request,
        "usuarios/perfil_publico.html",
        {
            "usuario_perfil": usuario,
            "reviews": reviews,
            "total_reviews": resumo["total_reviews"] or 0,
            "media_avaliacoes": resumo["media_avaliacoes"],
            "conversa_existente": conversa_existente,
        },
    )


@require_POST
@login_required
def comentar_review(request, review_id):
    review = get_object_or_404(
        Review.objects.select_related("usuario", "filme"),
        id=review_id,
    )

    if review.usuario == request.user:
        messages.info(request, "Você não pode comentar na sua própria review.")
        next_url = request.POST.get("next_url") or reverse("reviews_recentes")
        return redirect(next_url)

    texto = request.POST.get(f"review-{review.id}-texto", "").strip()
    next_url = request.POST.get("next_url") or reverse("reviews_recentes")

    if not next_url.startswith("/"):
        next_url = reverse("reviews_recentes")

    if not texto:
        messages.error(request, "O comentário não pode ficar vazio.")
        return redirect(next_url)

    ComentarioReview.objects.create(
        review=review,
        usuario=request.user,
        texto=texto,
    )

    messages.success(request, "Comentário adicionado com sucesso.")
    return redirect(next_url)


@require_POST
@login_required
def editar_comentario_review(request, comentario_id):
    comentario = get_object_or_404(
        ComentarioReview.objects.select_related("usuario", "review"),
        id=comentario_id,
    )

    if comentario.usuario != request.user:
        messages.error(request, "Você só pode editar seus próprios comentários.")
        next_url = request.POST.get("next_url") or reverse("reviews_recentes")
        return redirect(next_url)

    texto = request.POST.get(f"comentario-{comentario.id}-texto", "").strip()
    next_url = request.POST.get("next_url") or reverse("reviews_recentes")

    if not next_url.startswith("/"):
        next_url = reverse("reviews_recentes")

    if not texto:
        messages.error(request, "O comentário não pode ficar vazio.")
        return redirect(next_url)

    comentario.texto = texto
    comentario.save(update_fields=["texto", "data_atualizacao"])

    messages.success(request, "Comentário editado com sucesso.")
    return redirect(next_url)


@require_POST
@login_required
def excluir_comentario_review(request, comentario_id):
    comentario = get_object_or_404(
        ComentarioReview.objects.select_related("usuario"),
        id=comentario_id,
    )

    if comentario.usuario != request.user:
        messages.error(request, "Você só pode excluir seus próprios comentários.")
        next_url = request.POST.get("next_url") or reverse("reviews_recentes")
        return redirect(next_url)

    next_url = request.POST.get("next_url") or reverse("reviews_recentes")

    if not next_url.startswith("/"):
        next_url = reverse("reviews_recentes")

    comentario.delete()
    messages.success(request, "Comentário excluído com sucesso.")
    return redirect(next_url)