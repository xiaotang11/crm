# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-01 15:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0006_auto_20180201_2132'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='courserecord',
            options={'verbose_name': '上课记录表'},
        ),
        migrations.AlterModelOptions(
            name='studyrecord',
            options={'verbose_name': '学习记录'},
        ),
        migrations.RenameField(
            model_name='studyrecord',
            old_name='attendence',
            new_name='attendance',
        ),
    ]