# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0023_auto_20150913_1708'),
    ]

    operations = [
        migrations.CreateModel(
            name='Packages',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('errata', models.CharField(null=True, max_length=128, blank=True)),
                ('pkgs', models.TextField(null=True, max_length=2000, blank=True)),
            ],
        ),
    ]
