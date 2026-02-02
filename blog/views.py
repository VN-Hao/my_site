from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import Http404, JsonResponse
from django.db.models import Max
from .models import Post, CTF, Room, Move
from .forms import ChatInputForm
from .bot import ChatBot
import json


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


def game_level_page(request, slug, level_number, status="unanswered"):
    try:
        challenge = CTF.objects.get(level_number=level_number)
    except CTF.DoesNotExist:
        max_level = CTF.objects.aggregate(Max('level_number'))['level_number__max']
        if max_level is not None and level_number > max_level:
            return render(request, f"blog/games/{slug}/game-complete.html")
        raise Http404("Level not found")

    path = f"blog/games/{slug}/game-level.html"
    return render(request, path, {
        "level_number": level_number,
        "level_title": challenge.level_title,
        "level_description": challenge.level_description,
        "status": status
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

        if "chat_history" not in request.session:
            request.session["chat_history"] = []

        if form.is_valid():
            user_input = form.cleaned_data["chat_input"]
            bot_response = bot.get_response(user_input)

            history = request.session["chat_history"]
            history.append({"user": user_input, "bot": bot_response})
            request.session["chat_history"] = history
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"user": user_input, "bot": bot_response})
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
             return JsonResponse({"error": "Invalid form data"}, status=400)

        return render(
            request,
            "blog/chat.html",
            {"chat_history": request.session["chat_history"], "form": form},
        )


def verify_flag(request):
    # request method here will always be POST
    user_answer = request.POST.get("flag")
    level_number = int(request.POST.get("level_number"))
    challenge = CTF.objects.get(level_number=level_number)
    flag = challenge.level_answer
    is_correct = user_answer == flag
    status = "correct" if is_correct else "incorrect"
    return game_level_page(request, "ctf", level_number, status)

def tic_tac_toe_game(request):
    room_id = request.GET.get('room_id')
    action = request.GET.get('action')

    if action == 'host' and room_id:
        Room.objects.get_or_create(room_id=room_id)
    
    elif action == 'join' and room_id:
        room_exists = Room.objects.filter(room_id=room_id).exists()
        if not room_exists:
            return render(request, "blog/games/tic-tac-toe/introduction.html", {
                "post": Post.objects.get(slug="tic-tac-toe"), # Assuming usage context from intro page
                "error": "Invalid Room ID"
            })

    return render(request, "blog/games/tic-tac-toe/game.html")

def tic_tac_toe_move(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            room_id = data.get("room_id")
            x = data.get("x")
            y = data.get("y")
            player = data.get("player")
            
            room = Room.objects.get(room_id=room_id)
            # Check for existing move
            if Move.objects.filter(room=room, x=x, y=y).exists():
                return JsonResponse({"status": "error", "message": "Cell already occupied"})
            
            Move.objects.create(room=room, x=x, y=y, player=player)
            return JsonResponse({"status": "success"})
        except Room.DoesNotExist:
             return JsonResponse({"status": "error", "message": "Room not found"})
        except Exception as e:
             return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid method"})

def tic_tac_toe_get_updates(request):
    room_id = request.GET.get("room_id")
    try:
        room = Room.objects.get(room_id=room_id)
        # Using simple serialization for now
        moves = list(room.moves.values('x', 'y', 'player'))
        return JsonResponse({"status": "success", "moves": moves})
    except Room.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Room not found"})

def tic_tac_toe_clear(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            room_id = data.get("room_id")
            room = Room.objects.get(room_id=room_id)
            room.moves.all().delete()
            return JsonResponse({"status": "success"})
        except Room.DoesNotExist:
             return JsonResponse({"status": "error", "message": "Room not found"})
        except Exception as e:
             return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid method"})

def tic_tac_toe_end(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            room_id = data.get("room_id")
            room = Room.objects.get(room_id=room_id)
            room.delete()
            return JsonResponse({"status": "success"})
        except Room.DoesNotExist:
             return JsonResponse({"status": "error", "message": "Room not found"})
        except Exception as e:
             return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid method"})

