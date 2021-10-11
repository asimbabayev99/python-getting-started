from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .models import *
import json
import requests
import lxml.html
from django.http import JsonResponse
from django.views import View
import pandas as pd
import time

from telebot import TeleBot, types
from rest_framework.response import Response
from rest_framework.views import APIView




BASE_URL = 'https://webmobcontact.nunu-app.xyz/?logged_hash=NW1GNTV6c3pVdE0venpwcWNIY3ZBSmZHYzJMYzZBVGtPNDJmVGdxQ2NFKzd1RXFmdWdiQnJURUp6QjZTTkhLVnRGNTFJbHdJME1kUnRON29ZWFp4OSsrRldOK1dKUnNMV3RLMDNwU3JjVzg9'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'

session = requests.Session()
session.headers = {'user-agent': USER_AGENT}
session.headers.update({'Referer': BASE_URL})
session.get(BASE_URL)

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
        update = types.Update.de_json(json_str)
        bot.process_new_updates([update])
 
        return Response({'code': 200})



@bot.message_handler(commands=['start', 'reset'])
def welcome(message):
    Chat.objects.filter(id=message.chat.id).delete()
    # Action.objects.filter(chat_id=message.chat.id).delete()
    # Keyword.objects.filter(chat_id=message.chat.id).delete()
    Chat.objects.create(
        id=message.chat.id,
        username=message.from_user.username, 
        first_name=message.from_user.first_name, 
        last_name=message.from_user.last_name
    )
    new_action = Action(
        chat_id=message.chat.id,
        name='enter_password',
    )
    new_action.save()

    text = "<b>Добро пожаловать, {0.first_name}!</b>\n".format(message.from_user)
    text += "Я - <b>{0.first_name}</b>, бот созданный для поиска контаков. Для использования данных услуг введите <b>ключ:</b>".format(bot.get_me())
    bot.send_message(message.chat.id, text, parse_mode='html')




# @bot.message_handler(commands=['reset'])
# def reset(message):
#     Action.objects.filter(chat_id=message.chat.id).delete()
#     Keyword.objects.filter(chat_id=message.chat.id).delete()
#     bot.send_message(message.chat.id, "Your data reset")



@bot.message_handler(commands=['terminate'])
def terminate(message):
    Action.objects.filter(chat_id=message.chat.id).update(status="canceled")
    bot.send_message(message.chat.id, "jobs terminated")
    



@bot.message_handler(commands=['help'])
def welcome(message):
    bot.send_message(message.chat.id, "При отправке номера вы получите список имен сохранненых в контактах других людей. \nПри отпрвке файла с номерами вы сможете произвести поиск среди контактов по ключевым словам")



def get_progress_bar(completed, total):
    print(completed, total)
    percentage = int(completed / total * 100)
    result = (int(percentage / 10) * "#") + (10 - int(percentage / 10)) * "." + " (" + str(completed) + ", " + str(total) + ")"
    return result



@bot.message_handler(content_types=['document'])
def receive_document(message):
    last_action = Action.objects.filter(chat_id=message.chat.id).order_by('-id').first()
    if last_action and last_action.name == "enter_password" and last_action.status != 'completed':
        bot.send_message(message.chat.id, "<b>Введите ключ:</b>", parse_mode="html")
        return  
    elif last_action and last_action.status != "completed":
        bot.send_message(message.chat.id, "Подождите завершения действий. Для отмены последних действий введите команду <a>/terminate<a>", parse_mode="html")
        return

    fileID = message.document.file_id
    file = bot.get_file(fileID)
    filename = message.document.file_name

    data = {
        'fileID': fileID,
        'filename': filename,
        'filepath': file.file_path,
    }

    new_action = Action(
        chat=message.chat.id,
        name='upload_file',
        detail=json.dumps(data)
    )
    new_action.save()


    keywords = Keyword.objects.filter(chat_id=message.chat.id).all()
    keywords = [i.name for i in keywords]

    if len(keywords) > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton("Да", callback_data='yes')
        item2 = types.InlineKeyboardButton("Нет", callback_data='no')
        markup.add(item1, item2)
        bot.send_message(message.chat.id, 'Хотите использовать последний список имен? ' + ", ".join(keywords), reply_markup=markup)
    else:
        new_action = Action(
            chat=message.chat.id,
            name='upload_keywords'
        ).save()
        bot.send_message(message.chat.id, 'Введит список имен через запятую:')



def check_numbers(message, action):
    data = json.loads(action.detail)
    keywords = Keyword.objects.filter(chat_id=message.chat.id).all()
    keywords = [i.name for i in keywords]
    print("keywords = ", keywords)

    ext = data['filename'].split(".")[-1]
    if ext == "xls" or ext == "xlsx":
        read_file = pd.read_excel('https://api.telegram.org/file/bot{0}/{1}'.format(settings.TOKEN, data['filepath']))
    elif ext == "csv":
        read_file = pd.read_csv('https://api.telegram.org/file/bot{0}/{1}'.format(settings.TOKEN, data['filepath']))
    else:
        bot.send_message(message.chat.id, "Невеный формат. Принимаются файлы следующих форматов: csv, xls, xlsx")
        return

    
    total_rows = len(read_file.index)
    print("total row count:", total_rows)

    result = {}
    msg = bot.send_message(message.chat.id, get_progress_bar(0, total_rows))
    # print(msg)

    for i, row in read_file.iterrows():
        print(row['Telefon nömrəsi'])
        last_action = Action.objects.filter(chat_id=message.chat.id).order_by('-id').first()
        if not last_action or last_action.status == "canceled":
            bot.delete_message(message.chat.id, msg.message_id)
            return
        try:
            bot.edit_message_text(chat_id=message.chat.id, text=get_progress_bar(i, total_rows), message_id=msg.message_id)
            response = session.get("https://webmobcontact.nunu-app.xyz/result?n={0}&f=1".format(row['Telefon nömrəsi']))
            tree = lxml.html.fromstring(response.text)
            user_name = tree.xpath("//*[@id='content']/div/div/div/div[1]/div[1]/div[2]/h1")[0].text_content()
            names = [user_name, ]

            tags = tree.xpath("//*[@id='tagList']/span")
            for tag in tags:
                user_name = tag.text_content()
                names.append(user_name)

            contains = False
            for name in names:
                for key in keywords:
                    if name.lower().find(key) >= 0:
                        print(row['Telefon nömrəsi'], names)
                        result.update({
                            row['Telefon nömrəsi'] : names
                        })
                        contains = True
                        break
                if contains:
                    break
        except Exception as e:
            print(e)
        
        time.sleep(settings.REQUEST_PAUSE)

    # print(result)
    result = [str(key) + '\n' + str(value) for key, value in result.items()]
    bot.delete_message(message.chat.id, msg.message_id)
    if result:
        bot.send_message(message.chat.id, "\n".join(result))
    else:
        bot.send_message(message.chat.id, "Ничего не найдено")




def normalize_keywords(keywords):
    new_keywords = []
    for i in keywords:
        if i is None or i.strip() == "":
            continue
        else:
            new_keywords.append(i.strip())
    return new_keywords
        



@bot.message_handler(content_types=['text'])
def receive_number(message):
    last_action = Action.objects.filter(chat_id=message.chat.id).order_by('-id').first()
    if last_action:
        if last_action.name == "upload_keywords" and last_action.status != "completed":
            Keyword.objects.filter(chat_id=message.chat.id).delete()
            keywords = message.text.split(",")
            keywords = normalize_keywords(keywords)
            for i in keywords:
                new_keyword= Keyword(
                    chat=message.chat.id,
                    name=i
                ).save()
            last_action.status = "completed"
            last_action.save()
            
            action = Action.objects.filter(chat_id=message.chat.id, name="upload_file").order_by('-id').first()
            check_numbers(message=message, action=action)
            action.status == "completed"
            action.save()
            return
        elif last_action.name == "enter_password" and last_action.status != "completed":
            if message.text == settings.SECRET:
                last_action.status = "completed"
                last_action.save()
                bot.send_message(message.chat.id, "Теперь вы можете пользоваться услугами. Для помощи введите команду <a>/help<a>", parse_mode="html")
            else:
                bot.reply_to(message, "Ключ неверный! Повторите попытку снова")
            return

       
    try:
        last_action = Action.objects.filter(chat_id=message.chat.id).order_by('-id').first()
        if last_action and last_action.status != 'completed':
            bot.send_message("wait for job to complete. In order to cancel running jobs enter <a>/terminate</a> command.", parse_mode="html")
            return

        res = session.get("https://webmobcontact.nunu-app.xyz/result?n={0}&f=1".format(message.text))
        tree = lxml.html.fromstring(res.text)
        
        user_name = tree.xpath("//*[@id='content']/div/div/div/div[1]/div[1]/div[2]/h1")[0].text_content()
        names = [user_name, ]

        tags = tree.xpath("//*[@id='tagList']/span")
        for tag in tags:
            user_name = tag.text
            names.append(user_name)

        bot.reply_to(message, str(names))
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, str("Not found!"))
 


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'yes':
                keywords = Keyword.objects.filter(chat_id=call.message.chat.id).all()
                keywords = [i.name for i in keywords]
                action = Action.filter(chat_id=call.message.chat.id, name="upload_file").order_by('-id').first()
                bot.delete_message(call.message.chat.id, call.message.message_id)
                print(action)
                check_numbers(message=call.message, action=action)
                action.status = 'completed'
                action.save()
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введит список имен через запятую", reply_markup=None)
                new_action = Action(
                    chat=call.message.chat.id,
                    name='upload_keywords'
                ).save()

            # show alert
            # bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="ЭТО ТЕСТОВОЕ УВЕДОМЛЕНИЕ!!11")

    except Exception as e:
        print(repr(e))

# Webhook
# bot.remove_webhook()
# bot.set_webhook(url="https://infinite-cove-65953.herokuapp.com/bot")