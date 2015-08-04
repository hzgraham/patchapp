# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0009_server_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='comments',
            field=models.TextField(max_length=256, blank=True, null=True),
        ),
    ]
