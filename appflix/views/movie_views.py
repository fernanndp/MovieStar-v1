from io import BytesIO

import requests
from colorthief import ColorThief
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from appflix.forms import ReviewForm
from appflix.models import Filme, Review
from appflix.services.tmdb import (
    buscar_detalhes_filme,
    buscar_e_salvar_filme,
    buscar_filmes_por_titulo,
    buscar_filmes_recente,
    buscar_videos_filme,
)


REQUEST_TIMEOUT = 10
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def ajustar_cor_solida(cor_hex):
    if cor_hex == "transparent" or not cor_hex:
        return "#333333"
    return cor_hex


def ajustar_contraste(cor_hex):
    cor_hex = ajustar_cor_solida(cor_hex)

    r = int(cor_hex[1:3], 16)
    g = int(cor_hex[3:5], 16)
    b = int(cor_hex[5:7], 16)

    luminosidade = (0.299 * r + 0.587 * g + 0.114 * b) / 255

    if luminosidade > 0.7:
        return "#333333"

    return cor_hex


def _build_poster_url(poster_path):
    if not poster_path:
        return ""
    return f"{TMDB_IMAGE_BASE_URL}{poster_path}"


def _get_dominant_color_from_poster(poster_path):
    poster_url = _build_poster_url(poster_path)
    if not poster_url:
        return "#000000", ""

    try:
        poster_response = requests.get(poster_url, timeout=REQUEST_TIMEOUT)
        poster_response.raise_for_status()

        color_thief = ColorThief(BytesIO(poster_response.content))
        dominant_color = color_thief.get_color(quality=1)
        dominant_color_hex = "#%02x%02x%02x" % dominant_color
        dominant_color_hex = ajustar_contraste(dominant_color_hex)

        contrast_class = ""
        if dominant_color_hex == "#000000":
            contrast_class = "review-btn-high-contrast"

        return dominant_color_hex, contrast_class

    except Exception:
        return "#000000", ""


@login_required
def home(request):
    query = request.GET.get("q", "").strip()

    if query:
        filmes = buscar_filmes_por_titulo(query)
        mensagem = "Filme encontrado"
    else:
        filmes = buscar_filmes_recente()
        mensagem = "Filmes recentes"

    return render(
        request,
        "filmes/index.html",
        {
            "filmes": filmes,
            "mensagem": mensagem,
        },
    )


@login_required
def adicionar_review(request, filme_id):
    filme = Filme.objects.filter(id=str(filme_id)).first()

    if not filme:
        filme = buscar_e_salvar_filme(filme_id)

    if not filme:
        messages.error(request, "Não foi possível carregar este filme.")
        return redirect("home")

    review_existente = Review.objects.filter(usuario=request.user, filme=filme).first()
    if review_existente:
        messages.info(request, "Você já avaliou este filme. Edite sua review abaixo.")
        return redirect("editar_review", review_id=review_existente.id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.usuario = request.user
            review.filme = filme
            review.save()

            messages.success(request, "Review adicionada com sucesso!")
            return redirect("detalhes_filme", filme_id=filme.id)

        messages.error(request, "Erro ao adicionar a review. Verifique os dados e tente novamente.")
    else:
        form = ReviewForm()

    return render(
        request,
        "filmes/adicionar_review.html",
        {
            "form": form,
            "filme": filme,
            "editando": False,
        },
    )


@login_required
def editar_review(request, review_id):
    review = get_object_or_404(
        Review.objects.select_related("filme"),
        id=review_id,
        usuario=request.user,
    )

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review atualizada com sucesso!")
            return redirect("minhas_reviews")

        messages.error(request, "Erro ao atualizar a review. Verifique os dados e tente novamente.")
    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        "filmes/adicionar_review.html",
        {
            "form": form,
            "filme": review.filme,
            "review": review,
            "editando": True,
        },
    )


@login_required
def excluir_review(request, review_id):
    review = get_object_or_404(
        Review,
        id=review_id,
        usuario=request.user,
    )

    if request.method == "POST":
        review.delete()
        messages.success(request, "Review excluída com sucesso!")
        return redirect("minhas_reviews")

    return redirect("minhas_reviews")


def detalhes_filme(request, filme_id):
    filme_info = buscar_detalhes_filme(filme_id)
    if not filme_info:
        return render(request, "erros/404.html", status=404)

    video_info = buscar_videos_filme(filme_id)
    trailers = [
        video
        for video in video_info.get("results", [])
        if video.get("site") == "YouTube" and video.get("type") == "Trailer"
    ]
    trailer_key = trailers[0]["key"] if trailers else None

    dominant_color_hex, contrast_class = _get_dominant_color_from_poster(
        filme_info.get("poster_path", "")
    )

    release_date = filme_info.get("release_date")
    release_year = release_date[:4] if release_date else None

    filme_local = Filme.objects.filter(id=str(filme_id)).first()
    reviews = (
        Review.objects.filter(filme=filme_local)
        .select_related("usuario", "usuario__perfil")
        .prefetch_related("comentarios", "comentarios__usuario", "comentarios__usuario__perfil")
        .order_by("-data_criacao")
        if filme_local
        else []
)

    contexto = {
        "filme": {
            "id": filme_info["id"],
            "title": filme_info.get("title", ""),
            "overview": filme_info.get("overview", ""),
            "release_year": release_year or "Ano não disponível",
            "poster_path": filme_info.get("poster_path", ""),
            "backdrop_path": filme_info.get("backdrop_path", ""),
            "trailer_key": trailer_key,
        },
        "dominant_color": dominant_color_hex,
        "contrast_class": contrast_class,
        "form": ReviewForm(),
        "reviews": reviews,
    }

    return render(request, "filmes/detalhes_filme.html", contexto)