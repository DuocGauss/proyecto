# Generated by Django 4.2.5 on 2023-12-19 11:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_bomberos', '0003_revisiondiaria_id_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='compania',
            field=models.ForeignKey(blank=True, default='Sin Compañia', null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_bomberos.compañia'),
        ),
    ]
