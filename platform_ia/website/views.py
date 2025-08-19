from django.shortcuts import render

# Create your views here.

def home(request):
  return render(request, 'home.html', {} )

def login(request):
  return render(request, 'auth/login.html', {'is_auth': True})

def register(request):
  return render(request, 'auth/register.html', {'is_auth': True})

def account(request):
  return render(request, 'auth/account.html',{})

def dashboard(request):
  return render(request, 'dashboard.html', {})

def search(request):
  return render(request, 'search.html', {})