# Generated by Django 2.1.3 on 2018-12-20 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stance', '0003_auto_20181218_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stance',
            name='proof_last_check',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
