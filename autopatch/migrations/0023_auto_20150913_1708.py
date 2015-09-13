# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autopatch', '0022_audit_server'),
    ]

    operations = [
        migrations.RenameField(
            model_name='audit',
            old_name='mode_date',
            new_name='mod_date',
        ),
    ]
