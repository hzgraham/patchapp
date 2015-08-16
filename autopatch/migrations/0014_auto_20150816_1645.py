# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0013_auto_20150813_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='updates',
            field=models.TextField(null=True, blank=True, max_length=1000),
        ),
    ]
