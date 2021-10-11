from django.db import models

# Create your models here.
class Chat(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=256, null=True, blank=True)
    first_name = models.CharField(max_length=256, null=True, blank=True)
    last_name = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return str(self.id) + "-" + self.username
    


ACTION_NAMES = (
    ('upload_file', 'upload_file'),
    ('upload_keywords', 'upload_keywords'),
    ('enter_password', 'enter_password')
)


ACTION_STATUSES = (
    ('pending', 'pending'),
    ('canceled', 'canceled'),
    ('completed', 'completed')
)


class Action(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=32, choices=ACTION_NAMES)
    status = models.CharField(max_length=32, choices=ACTION_STATUSES, default="pending")
    detail = models.CharField(max_length=32, null=True, blank=True)



class Keyword(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return str(self.id) + "-" + self.name



