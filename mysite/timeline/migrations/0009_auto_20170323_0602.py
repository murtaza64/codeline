# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-23 06:02
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0008_post_last_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='edited',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='post',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 23, 6, 2, 12, 496371)),
            preserve_default=False,
        ),
    ]
