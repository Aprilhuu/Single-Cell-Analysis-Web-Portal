# Generated by Django 2.2.5 on 2020-01-04 20:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dataset', '0008_auto_20200102_2240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='path',
            field=models.FilePathField(allow_folders=True, match=True,
                                       path='D:\\Repo\\Single-Cell-Analysis-Web-Portal\\userData\\datafile'),
        ),
    ]