# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0004_server'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='exclude',
            field=models.TextField(max_length=256, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='server',
            name='hostgroup',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='server',
            name='skip',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='server',
            name='server',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
