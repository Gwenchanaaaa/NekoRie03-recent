# Generated by Django 5.1.1 on 2024-11-11 21:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminmod', '0010_approvedstudent_rejectedstudent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='status',
        ),
    ]
