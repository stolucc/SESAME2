# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-19 17:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20190219_1745'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='call',
            name='criteria',
        ),
    ]