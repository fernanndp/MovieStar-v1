import requests
from datetime import datetime

from django.conf import settings

from appflix.models import Filme


TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
REQUEST_TIMEOUT = 10


def _tmdb_get(endpoint, params=None):
    if not settings.TMDB_API_KEY:
        return None

    request_params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "pt-BR",
    }

    if params:
        request_params.update(params)

    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/{endpoint}",
            params=request_params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def _parse_release_date(date_str):
    if not date_str:
        return None

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def _extract_release_year(date_str):
    parsed_date = _parse_release_date(date_str)
    return parsed_date.year if parsed_date else None


def _build_poster_url(poster_path):
    if not poster_path:
        return ""
    return f"{TMDB_IMAGE_BASE_URL}{poster_path}"


def buscar_filmes_recente():
    data = _tmdb_get("movie/popular", {"page": 1})
    if not data:
        return []

    filmes = data.get("results", [])

    for filme in filmes:
        release_date_str = filme.get("release_date", "")
        parsed_date = _parse_release_date(release_date_str)
        filme["release_year"] = parsed_date.year if parsed_date else None
        filme["_release_sort"] = parsed_date

    filmes_ordenados = sorted(
        filmes,
        key=lambda filme: (filme["_release_sort"] is not None, filme["_release_sort"]),
        reverse=True,
    )

    for filme in filmes_ordenados:
        filme.pop("_release_sort", None)

    return filmes_ordenados


def buscar_filmes_por_titulo(titulo):
    data = _tmdb_get("search/movie", {"query": titulo, "page": 1})
    if not data:
        return []

    filmes = data.get("results", [])

    for filme in filmes:
        filme["release_year"] = _extract_release_year(filme.get("release_date"))

    return filmes


def buscar_e_salvar_filme(filme_id):
    filme_info = _tmdb_get(f"movie/{filme_id}")
    if not filme_info:
        return None

    data_lancamento = _parse_release_date(filme_info.get("release_date"))
    poster_url = _build_poster_url(filme_info.get("poster_path", ""))

    filme, _ = Filme.objects.update_or_create(
        id=str(filme_info["id"]),
        defaults={
            "titulo": filme_info.get("title", ""),
            "descricao": filme_info.get("overview", ""),
            "data_lancamento": data_lancamento,
            "poster": poster_url or None,
        },
    )

    return filme


def buscar_detalhes_filme(filme_id):
    return _tmdb_get(f"movie/{filme_id}")


def buscar_videos_filme(filme_id):
    return _tmdb_get(f"movie/{filme_id}/videos") or {}