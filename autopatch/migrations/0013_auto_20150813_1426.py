# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0012_auto_20150809_0219'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='category',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.DeleteModel(
            name='Page',
        ),
    ]
