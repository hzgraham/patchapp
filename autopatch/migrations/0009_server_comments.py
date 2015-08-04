# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0008_auto_20150802_1833'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='comments',
            field=models.CharField(null=True, max_length=256, blank=True),
        ),
    ]
