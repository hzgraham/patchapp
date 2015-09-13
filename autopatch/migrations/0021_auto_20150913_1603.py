# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0020_audit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='audit',
            name='record',
        ),
        migrations.AddField(
            model_name='audit',
            name='comments',
            field=models.TextField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='audit',
            name='exclude',
            field=models.TextField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='audit',
            name='hostgroup',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='audit',
            name='mode_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='audit',
            name='skip',
            field=models.BooleanField(default=True),
        ),
    ]
