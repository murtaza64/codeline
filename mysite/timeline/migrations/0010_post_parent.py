# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-26 19:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0009_auto_20170323_0602'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='timeline.Post'),
        ),
    ]
