from django.db import models


# Create your models here.
class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Tag(models.Model):
    caption = models.CharField(max_length=50)

    def __str__(self):
        return self.caption


class Post(models.Model):
    title = models.CharField(max_length=150)
    excerpt = models.CharField(max_length=200)
    image = models.CharField(max_length=100)
    date = models.DateField(auto_now=True)
    slug = models.SlugField(unique=True)  # db_index=True automatically
    content = models.TextField()
    author = models.ForeignKey(
        Author, on_delete=models.SET_NULL, null=True, related_name="posts"
    )
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title
    
class CTF(models.Model):
    level_number = models.IntegerField()
    level_title = models.CharField(max_length=200)
    level_description = models.TextField(null=True)
    level_answer = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "CTF Challenges"

    def __str__(self):
        return f"Level {self.level_number}"

class Room(models.Model):
    room_id = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.room_id

class Move(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='moves')
    x = models.IntegerField()
    y = models.IntegerField()
    player = models.CharField(max_length=1) # 'X' or 'O'
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

