# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-08 11:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0004_auto_20161222_1054'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='private',
            field=models.BooleanField(default=True),
        ),
    ]
