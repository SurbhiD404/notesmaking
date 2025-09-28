from django.urls import path
from . import views


urlpatterns = [
path('notes/', views.notes_list_create),
path('notes/<int:pk>/', views.note_detail),
path('register/', views.register),
path('login/', views.login_view),
]