from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q


class Filme(models.Model):
    id = models.CharField(max_length=15, primary_key=True)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    data_lancamento = models.DateField(null=True, blank=True)
    poster = models.URLField(max_length=500, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["titulo"]
        verbose_name = "Filme"
        verbose_name_plural = "Filmes"

    def __str__(self):
        return self.titulo


class Review(models.Model):
    filme = models.ForeignKey(
        Filme,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    comentario = models.TextField()
    avaliacao = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-data_criacao"]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        constraints = [
            models.UniqueConstraint(
                fields=["filme", "usuario"],
                name="unique_review_por_usuario_filme",
            )
        ]

    def __str__(self):
        return f"{self.usuario.username} - {self.filme.titulo}"


class Conversa(models.Model):
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="conversas_como_user1",
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="conversas_como_user2",
    )
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
            ordering = ["-atualizada_em"]
            verbose_name = "Conversa"
            verbose_name_plural = "Conversas"
            constraints = [
            models.UniqueConstraint(
                fields=["user1", "user2"],
                name="unique_conversa_entre_dois_usuarios",
            ),
            models.CheckConstraint(
                condition=~Q(user1=F("user2")),
                name="check_conversa_nao_permite_mesmo_usuario",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.user1_id and self.user2_id and self.user1_id > self.user2_id:
            self.user1_id, self.user2_id = self.user2_id, self.user1_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user1.username} ↔ {self.user2.username}"

    def participantes(self):
        return [self.user1, self.user2]

    def outro_usuario(self, usuario_atual):
        if usuario_atual == self.user1:
            return self.user2
        return self.user1

    def ultima_mensagem(self):
        return self.mensagens.order_by("-criada_em").first()


class Mensagem(models.Model):
    conversa = models.ForeignKey(
        Conversa,
        on_delete=models.CASCADE,
        related_name="mensagens",
    )
    remetente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mensagens_enviadas",
    )
    texto = models.TextField()
    criada_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    class Meta:
        ordering = ["criada_em"]
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"

    def __str__(self):
        return f"{self.remetente.username}: {self.texto[:30]}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Conversa.objects.filter(pk=self.conversa_id).update(atualizada_em=self.criada_em)


class Perfil(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    foto = models.ImageField(
        upload_to="perfil_fotos/",
        blank=True,
        null=True,
    )

class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"
 
def __str__(self):
        return f"Perfil de {self.usuario.username}"

class ComentarioReview(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comentarios",
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comentarios_reviews",
    )
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["data_criacao"]
        verbose_name = "Comentário de review"
        verbose_name_plural = "Comentários de reviews"

    def __str__(self):
        return f"{self.usuario.username} em {self.review.id}"