from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Note(models.Model):
    owner = models.ForeignKey(User, related_name='notes', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    #display the title when the notes are called
   
    
