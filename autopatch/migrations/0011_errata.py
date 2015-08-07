# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0010_auto_20150804_0003'),
    ]

    operations = [
        migrations.CreateModel(
            name='Errata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('RHEA', models.CharField(max_length=128, null=True, blank=True)),
                ('RHSA', models.CharField(max_length=128, null=True, blank=True)),
                ('RHBA', models.CharField(max_length=128, null=True, blank=True)),
            ],
        ),
    ]
