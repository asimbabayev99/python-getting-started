from django.urls import path, include
from hello.views import *
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt



urlpatterns = [
    path('', csrf_exempt(UpdateBot.as_view()), name='update'),
]