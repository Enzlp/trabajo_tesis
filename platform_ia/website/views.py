from django.shortcuts import render

# Create your views here.

def home(request):
  return render(request, 'home.html', {'dropdown_val': 0})

def login(request):
  return render(request, 'auth/login.html', {'is_auth': True})

def register(request):
  return render(request, 'auth/register.html', {'is_auth': True})