# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0016_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='uptodate',
            field=models.BooleanField(default=0),
        ),
    ]
