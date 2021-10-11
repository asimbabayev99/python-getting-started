from django.urls import path, include
from home.views import *


urlpatterns = [
    path('', UpdateBot.as_view(), name='update'),
]