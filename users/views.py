from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile


def login_view(request):
    """Вход пользователя"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.first_name or user.username}!')
            
            # Перенаправляем пользователя на предыдущую страницу, если она была указана
            return redirect(next_url if next_url else 'catalog:index')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    
    next_url = request.GET.get('next', '')
    return render(request, 'users/login.html', {'next': next_url})


def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Вы вышли из аккаунта.')
    return redirect('catalog:index')


def register(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('catalog:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'users/register.html', {'title': 'Регистрация'})
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')
            return render(request, 'users/register.html', {'title': 'Регистрация'})
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует.')
            return render(request, 'users/register.html', {'title': 'Регистрация'})
        
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password,
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', '')
        )
        
        # Обновление профиля
        profile = user.profile
        profile.phone = request.POST.get('phone', '')
        profile.save()
        
        # Автоматическая авторизация после регистрации
        login(request, user)
        messages.success(request, f'Добро пожаловать, {user.first_name or user.username}! Регистрация прошла успешно.')
        return redirect('catalog:index')
    
    context = {
        'title': 'Регистрация',
    }
    return render(request, 'users/register.html', context)


@login_required
def profile(request):
    """Профиль пользователя"""
    user = request.user
    
    context = {
        'title': 'Профиль пользователя',
        'user': user,
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit(request):
    """Редактирование профиля пользователя"""
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        # Обновление данных пользователя
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Обновление данных профиля
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.postal_code = request.POST.get('postal_code', '')
        
        # Обработка аватара
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        
        messages.success(request, 'Профиль успешно обновлен.')
        return redirect('users:profile')
    
    context = {
        'title': 'Редактирование профиля',
        'user': user,
        'profile': profile,
    }
    return render(request, 'users/profile_edit.html', context)
