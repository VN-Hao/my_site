from django.shortcuts import render, get_object_or_404
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
    return render(request, "blog/post-detail.html", {
        "post": post,
        "post_tags": post.tags.all()
    })
    
def chat(request):
    # Initialize chat history in session if it doesn't exist
    if 'chat_history' not in request.session:
        request.session['chat_history'] = [
            {
                "user": "Hey! How are you?",
                "bot": "I'm doing great, thanks! How about you?"
            }
        ]
        
    if request.method == "POST":
        form = ChatInputForm(request.POST)
        if form.is_valid():
            user_input = form.cleaned_data['chat_input']
            bot_response = bot.get_response(user_input)
            
            # Update session
            # We need to re-assign the list to trigger the session save
            history = request.session['chat_history']
            history.append({
                "user": user_input,
                "bot": bot_response
            })
            request.session['chat_history'] = history
    else:
        form = ChatInputForm()
        
    return render(request, "blog/chat.html", {
        "chat_history": request.session['chat_history'],
        "form": form
    })
