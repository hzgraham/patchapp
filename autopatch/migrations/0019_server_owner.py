# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0018_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='owner',
            field=models.CharField(blank=True, null=True, max_length=50),
        ),
    ]
