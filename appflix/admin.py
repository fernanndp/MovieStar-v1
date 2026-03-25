from django.contrib import admin

from .models import Conversa, Filme, Mensagem, Review


@admin.register(Filme)
class FilmeAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "data_lancamento", "data_criacao")
    search_fields = ("id", "titulo")
    list_filter = ("data_lancamento", "data_criacao")
    ordering = ("titulo",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "filme", "usuario", "avaliacao", "data_criacao", "data_atualizacao")
    search_fields = ("filme__titulo", "usuario__username", "usuario__email", "comentario")
    list_filter = ("avaliacao", "data_criacao", "data_atualizacao")
    raw_id_fields = ("filme", "usuario")
    ordering = ("-data_criacao",)


class MensagemInline(admin.TabularInline):
    model = Mensagem
    extra = 0
    fields = ("remetente", "texto", "lida", "criada_em")
    readonly_fields = ("criada_em",)
    raw_id_fields = ("remetente",)
    ordering = ("-criada_em",)


@admin.register(Conversa)
class ConversaAdmin(admin.ModelAdmin):
    list_display = ("id", "user1", "user2", "criada_em", "atualizada_em", "total_mensagens")
    search_fields = ("user1__username", "user2__username", "user1__email", "user2__email")
    list_filter = ("criada_em", "atualizada_em")
    raw_id_fields = ("user1", "user2")
    readonly_fields = ("criada_em", "atualizada_em")
    ordering = ("-atualizada_em",)
    inlines = [MensagemInline]

    @admin.display(description="Mensagens")
    def total_mensagens(self, obj):
        return obj.mensagens.count()


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ("id", "conversa", "remetente", "texto_resumido", "lida", "criada_em")
    search_fields = (
        "texto",
        "remetente__username",
        "remetente__email",
        "conversa__user1__username",
        "conversa__user2__username",
    )
    list_filter = ("lida", "criada_em")
    raw_id_fields = ("conversa", "remetente")
    readonly_fields = ("criada_em",)
    ordering = ("-criada_em",)

    @admin.display(description="Texto")
    def texto_resumido(self, obj):
        return obj.texto[:60] + ("..." if len(obj.texto) > 60 else "")