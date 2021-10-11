from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .models import Greeting

import requests
from django.http import JsonResponse
from django.views import View

from telebot import TeleBot, types
from rest_framework.response import Response
from rest_framework.views import APIView
 

bot = TeleBot(settings.TOKEN, threaded=False)



# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, "index.html")


 
class UpdateBot(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Бот запусчен и работает.")

    def post(self, request):
        # Сюда должны получать сообщения от телеграм и далее обрабатываться ботом
        json_str = request.body.decode('UTF-8')
        print(json_str)
        update = types.Update.de_json(json_str)
        bot.process_new_updates([update])
 
        return Response({'code': 200})
 
 
@bot.message_handler(commands=['start'])
def start_message(message):
    # User написал /start в диалоге с ботом
    text = '<b>Настройка бота!</b>\n\n'
    text += 'Чтобы пначать использовать бата и настроить его по Вашим предпочтениям ответьте на следующие вопросы.\n\n'
    text += '......................'
 
    keyboard = types.InlineKeyboardMarkup()
    key_begin = types.InlineKeyboardButton(text='🖊️ Начать', callback_data='begin')
    keyboard.add(key_begin)
 
    bot.send_message(message.chat.id, text=text, reply_markup=keyboard, parse_mode='HTML')


# Webhook
bot.remove_webhook()
bot.set_webhook(url="https://infinite-cove-65953.herokuapp.com/")