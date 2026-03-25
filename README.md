# 🎬 MovieStar

MovieStar é uma plataforma web desenvolvida com **Django** onde usuários podem descobrir filmes, criar reviews, interagir com outras pessoas e trocar mensagens privadas.

O projeto começou como uma aplicação simples de filmes e evoluiu para uma experiência mais social, com **perfil público**, **foto de perfil**, **feed de reviews recentes**, **comentários em reviews** e **chat privado entre usuários**.

---

## ✨ Funcionalidades

### Filmes
- Busca de filmes por título
- Exibição de filmes populares/recentes
- Página de detalhes do filme
- Trailer do filme, quando disponível
- Integração com a API do **TMDB**

### Reviews
- Criar review de um filme
- Editar review
- Excluir review
- Ver suas próprias reviews
- Ver reviews de outros usuários
- Feed de **reviews recentes**

### Perfis
- Cadastro e login de usuários
- Edição de perfil
- Upload de foto de perfil
- Remover foto de perfil
- Perfil público com estatísticas
- Exclusão de conta

### Interação entre usuários
- Buscar usuários da plataforma
- Visualizar perfil público de outros usuários
- Comentar em reviews de outros usuários
- Lista de conversas privadas
- Enviar mensagens privadas
- Excluir conversas com mensagens

### Interface
- Layout moderno em tema escuro
- Componentes estilizados com CSS customizado
- Responsividade para desktop e mobile

### Observação
---
O chat implementado neste projeto **não é em tempo real**.  
As mensagens são enviadas e exibidas por meio de requisições HTTP tradicionais, sem uso de WebSockets.
---

## 🛠️ Tecnologias utilizadas

- **Python**
- **Django**
- **SQLite** (desenvolvimento local)
- **HTML**
- **CSS**
- **JavaScript**
- **TMDB API**
- **Pillow** (upload de imagens)
- **requests**
- **ColorThief** (extração de cor dominante em alguns trechos do projeto)

---

## 📁 Estrutura do projeto

```text
MovieStar/
├─ appflix/
│  ├─ migrations/
│  ├─ services/
│  │  └─ tmdb.py
│  ├─ views/
│  │  ├─ __init__.py
│  │  ├─ auth_views.py
│  │  ├─ movie_views.py
│  │  ├─ user_views.py
│  │  └─ chat_views.py
│  ├─ admin.py
│  ├─ forms.py
│  ├─ models.py
│  ├─ settings.py
│  ├─ urls.py
│  ├─ asgi.py
│  └─ wsgi.py
│
├─ templates/
│  ├─ base.html
│  ├─ auth/
│  ├─ movies/
│  ├─ users/
│  ├─ chat/
│  └─ errors/
│
├─ static/
│  ├─ css/
│  └─ images/
│
├─ media/
├─ manage.py
├─ requirements.txt
├─ .env.example
├─ .gitignore
└─ README.md
