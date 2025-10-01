from django.urls import path
from .views import register, login_view, notes_list_create, note_detail


urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'), 
    path('notes/', notes_list_create, name='notes_list_create'),
    path('notes/<int:pk>/', note_detail, name='note_detail'),
    
]