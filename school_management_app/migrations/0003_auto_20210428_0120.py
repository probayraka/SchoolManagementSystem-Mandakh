# Generated by Django 3.2 on 2021-04-27 17:20

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('school_management_app', '0002_auto_20210427_1656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scomment',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='tcomment',
            name='id',
            field=models.AutoField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
