from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import HttpResponse
from .models import Post
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
    return render(
        request, f"blog/{slug}.html", {"post": post, "post_tags": post.tags.all()}
    )


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
    user_answer = request.POST.get("flag")
    flag = "elpis{always_check_the_source_code}"
    is_correct = user_answer == flag
    if is_correct:
        return HttpResponse("Correct")
    return HttpResponse("Incorrect")
