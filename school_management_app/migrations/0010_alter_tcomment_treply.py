# Generated by Django 3.2 on 2021-04-28 14:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school_management_app', '0009_auto_20210428_2046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tcomment',
            name='TReply',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='school_management_app.tcomment'),
        ),
    ]
