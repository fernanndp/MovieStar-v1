from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Mensagem, Review, Perfil, ComentarioReview


STAR_CHOICES = [(i, f"{i} Estrela{'s' if i > 1 else ''}") for i in range(1, 6)]


class ReviewForm(forms.ModelForm):
    avaliacao = forms.IntegerField(
        required=False,
        widget=forms.RadioSelect(choices=STAR_CHOICES),
    )

    class Meta:
        model = Review
        fields = ["comentario", "avaliacao"]
        widgets = {
            "comentario": forms.Textarea(
                attrs={
                    "placeholder": "Escreva sua review...",
                    "rows": 4,
                }
            ),
        }
        labels = {
            "comentario": "Comentário",
            "avaliacao": "Avaliação",
        }

    def clean_avaliacao(self):
        avaliacao = self.cleaned_data.get("avaliacao")

        if avaliacao in (None, ""):
            return None

        if avaliacao not in range(1, 6):
            raise forms.ValidationError("A avaliação deve estar entre 1 e 5.")

        return avaliacao


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        labels = {
            "username": "Nome de usuário",
            "email": "E-mail",
            "first_name": "Primeiro nome",
            "last_name": "Sobrenome",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Seu nome de usuário"}),
            "email": forms.EmailInput(attrs={"placeholder": "seuemail@exemplo.com"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Seu primeiro nome"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Seu sobrenome"}),
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="E-mail",
        widget=forms.EmailInput(attrs={"placeholder": "seuemail@exemplo.com"}),
    )
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Digite sua senha"}),
    )
    password2 = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirme sua senha"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {
            "username": "Nome de usuário",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Escolha um nome de usuário"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()

        if commit:
            user.save()

        return user

class PerfilForm(forms.ModelForm):
    remover_foto = forms.BooleanField(
        required=False,
        label="Remover foto atual",
    )

    class Meta:
        model = Perfil
        fields = ["foto"]
        labels = {
            "foto": "Foto de perfil",
        }
        widgets = {
            "foto": forms.FileInput(attrs={"accept": "image/*", "class": "profile-file-input"})
        }

    def save(self, commit=True):
        perfil = super().save(commit=False)

        if self.cleaned_data.get("remover_foto") and perfil.foto:
            perfil.foto.delete(save=False)
            perfil.foto = None

        if commit:
            perfil.save()

        return perfil

class MensagemForm(forms.ModelForm):
    class Meta:
        model = Mensagem
        fields = ["texto"]
        labels = {
            "texto": "Mensagem",
        }
        widgets = {
            "texto": forms.Textarea(
                attrs={
                    "placeholder": "Digite sua mensagem...",
                    "rows": 3,
                }
            ),
        }

    def clean_texto(self):
        texto = self.cleaned_data["texto"].strip()

        if not texto:
            raise forms.ValidationError("A mensagem não pode estar vazia.")

        return texto
class ComentarioReviewForm(forms.ModelForm):
    class Meta:
        model = ComentarioReview
        fields = ["texto"]
        labels = {
            "texto": "Comentário",
        }
        widgets = {
            "texto": forms.Textarea(
                attrs={
                    "placeholder": "Escreva um comentário...",
                    "rows": 3,
                }
            )
        }

    def clean_texto(self):
        texto = self.cleaned_data["texto"].strip()
        if not texto:
            raise forms.ValidationError("O comentário não pode ficar vazio.")
        return texto