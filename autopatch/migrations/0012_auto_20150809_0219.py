# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0011_errata'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='env',
            field=models.CharField(max_length=50, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='server',
            name='satid',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='server',
            name='updates',
            field=models.TextField(max_length=256, blank=True, null=True),
        ),
    ]
