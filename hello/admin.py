from django.contrib import admin
from hello.models import Action, Keyword, Chat
# Register your models here.

admin.site.register(Action)
admin.site.register(Keyword)
admin.site.register(Chat)