from django.urls import path, include
from hello.views import *


urlpatterns = [
    path('', UpdateBot.as_view(), name='update'),
]