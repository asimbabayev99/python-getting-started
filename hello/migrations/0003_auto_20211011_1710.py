# Generated by Django 2.2.3 on 2021-10-11 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0002_auto_20211011_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='first_name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='chat',
            name='last_name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='chat',
            name='username',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
