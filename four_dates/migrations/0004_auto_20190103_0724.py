# Generated by Django 2.0.5 on 2019-01-03 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('four_dates', '0003_auto_20190103_0721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fourdates',
            name='flag',
            field=models.BooleanField(default=False),
        ),
    ]
