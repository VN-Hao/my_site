from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import HttpResponse
from django.urls import reverse
from .models import Post, CTF
from .forms import ChatInputForm
from .bot import ChatBot

posts = Post.objects.all()
bot = ChatBot()


# Create your views here.
def starting_page(request):
    random_posts = posts[:3]
    return render(request, "blog/index.html", {"posts": random_posts})


def posts_page(request):
    return render(
        request,
        "blog/all-posts.html",
        {
            "posts": posts,
        },
    )


def post_detail_page(request, slug):
    post = get_object_or_404(Post, slug=slug)
    path = f"blog/games/{slug}/introduction.html"
    return render(
        request, path, {"post": post, "post_tags": post.tags.all()}
    )


def game_level_page(request, slug, level_number):
    print(CTF.objects.all())
    challenge = get_object_or_404(CTF, level_number=level_number)
    print(challenge)
    path = f"blog/games/{slug}/game-level.html"
    return render(request, path, {
        "level_number": level_number,
        "level_title": challenge.level_title,
        "level_description": challenge.level_description
    })


class ChatView(View):
    def get(self, request):
        if request.session.get("chat_history"):
            del request.session["chat_history"]

        request.session["chat_history"] = []
        form = ChatInputForm()

        return render(
            request,
            "blog/chat.html",
            {"chat_history": request.session["chat_history"], "form": form},
        )

    def post(self, request):
        form = ChatInputForm(request.POST)
        if form.is_valid():
            user_input = form.cleaned_data["chat_input"]
            bot_response = bot.get_response(user_input)

            history = request.session["chat_history"]
            history.append({"user": user_input, "bot": bot_response})
            request.session["chat_history"] = history

        return render(
            request,
            "blog/chat.html",
            {"chat_history": request.session["chat_history"], "form": form},
        )


def verify_flag(request):
    # request method here will always be POST
    print(request.POST)
    user_answer = request.POST.get("flag")
    level_number = int(request.POST.get("level_number"))
    challenge = CTF.objects.get(level_number=level_number)
    flag = challenge.level_answer
    is_correct = user_answer == flag
    if is_correct:
        return HttpResponse("Correct")
    return HttpResponse("Incorrect")
