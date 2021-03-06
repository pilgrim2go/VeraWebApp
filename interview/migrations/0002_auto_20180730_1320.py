# Generated by Django 2.0.4 on 2018-07-30 10:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('interview', '0001_initial'),
        ('pipeline', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledmeeting',
            name='candidate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidate_scheduled_meetings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='scheduledmeeting',
            name='recruiter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recruiter_scheduled_meetings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='interviewpassed',
            name='candidate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidate_passed_interviews', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='interviewpassed',
            name='interview',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='passes', to='interview.ActionInterview'),
        ),
        migrations.AddField(
            model_name='interviewpassed',
            name='recruiter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recruiter_passed_interviews', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='actioninterview',
            name='action',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='interview', to='pipeline.Action'),
        ),
        migrations.AlterUniqueTogether(
            name='scheduledmeeting',
            unique_together={('action_interview', 'candidate')},
        ),
    ]
