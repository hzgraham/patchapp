# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0014_auto_20150816_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='skip',
            field=models.BooleanField(default=True),
        ),
    ]
