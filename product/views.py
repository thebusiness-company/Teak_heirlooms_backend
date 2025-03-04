from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django import http
# Create your views here.

@cache_control(max_age=86400)
def home(request):
    return http.HttpResponse("Hello, world. You're at the home page.")