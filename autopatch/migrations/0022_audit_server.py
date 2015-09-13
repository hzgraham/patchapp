# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0021_auto_20150913_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='audit',
            name='server',
            field=models.CharField(null=True, blank=True, max_length=256),
        ),
    ]
