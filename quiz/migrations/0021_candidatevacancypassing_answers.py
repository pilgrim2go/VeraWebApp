# Generated by Django 2.0.2 on 2018-03-15 15:24

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0020_auto_20180315_0859'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidatevacancypassing',
            name='answers',
            field=jsonfield.fields.JSONField(default=''),
            preserve_default=False,
        ),
    ]
