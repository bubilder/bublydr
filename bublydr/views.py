from django.shortcuts import render

def home(request):
    """Домашня сторінка ресторану"""
    return render(request, 'home.html')