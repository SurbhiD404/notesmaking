from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Note
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return Response({'detail': 'username, email and password required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'detail': 'username already taken'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        return Response({'detail': 'email already registered'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

    tokens = get_tokens_for_user(user)
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'tokens': tokens
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    data = request.data
    identifier = data.get('username') or data.get('email')
    password = data.get('password')

    if not identifier or not password:
        return Response({'detail': 'Provide username/email and password'}, status=status.HTTP_400_BAD_REQUEST)

    
    user = authenticate(request, username=identifier, password=password)
    if not user:
        
        try:
            user_obj = User.objects.get(email=identifier)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

    if not user:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    tokens = get_tokens_for_user(user)
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'tokens': tokens
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def notes_list_create(request):
    user = request.user
    if request.method == 'GET':
        notes = Note.objects.filter(owner=user).order_by('-updated_at')
        serialized = []
        for n in notes:
            serialized.append({
                'id': n.id,
                'name': n.name,
                'title': n.title,
                'content': n.content,
                'created_at': n.created_at,
                'updated_at': n.updated_at,
            })
        return Response(serialized)

    elif request.method == 'POST':
        data = request.data
        title = data.get('title')
        if not title:
            return Response({'detail': 'title is required'}, status=status.HTTP_400_BAD_REQUEST)
        name = data.get('name', '')
        content = data.get('content', '')
        note = Note.objects.create(owner=user, name=name, title=title, content=content)
        return Response({
            'id': note.id,
            'name': note.name,
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at,
            'updated_at': note.updated_at
        }, status=status.HTTP_201_CREATED)
        
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def note_detail(request, pk):
    user = request.user
    note = get_object_or_404(Note, pk=pk)

    if note.owner != user:
        return Response({'detail': 'Not found or not allowed'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({
            'id': note.id,
            'name': note.name,
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at,
            'updated_at': note.updated_at
        })

    if request.method in ['PUT', 'PATCH']:
        data = request.data
        if request.method == 'PUT' and not data.get('title'):
            return Response({'detail': 'title required for PUT'}, status=status.HTTP_400_BAD_REQUEST)
        if 'title' in data and data.get('title') is not None:
            note.title = data.get('title')
        if 'name' in data:
            note.name = data.get('name', '')
        if 'content' in data:
            note.content = data.get('content', '')
        note.save()
        return Response({
            'id': note.id,
            'name': note.name,
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at,
            'updated_at': note.updated_at
        })

    if request.method == 'DELETE':
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
