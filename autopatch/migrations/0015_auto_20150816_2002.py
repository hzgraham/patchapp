# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0014_auto_20150816_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='plerrata',
            field=models.TextField(max_length=2000, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='server',
            name='uptodate',
            field=models.BooleanField(default=1),
        ),
        migrations.AlterField(
            model_name='server',
            name='updates',
            field=models.TextField(max_length=2000, blank=True, null=True),
        ),
    ]
