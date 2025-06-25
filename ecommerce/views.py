from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
def home_view(request):
    data = {
        "message": "Welcome!"
    }
    return JsonResponse(data)

