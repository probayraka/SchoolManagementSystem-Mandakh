# Generated by Django 3.2 on 2021-04-27 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_management_app', '0005_rename_tnews_tcomment_tnews'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tcomment',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
