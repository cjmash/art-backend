# Generated by Django 2.0.1 on 2018-07-17 11:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20180713_0814'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetincidentreport',
            name='submitted_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
