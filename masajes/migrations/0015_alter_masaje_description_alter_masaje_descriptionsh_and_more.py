# Generated by Django 5.1.7 on 2025-05-08 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masajes', '0014_masaje_duracion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masaje',
            name='description',
            field=models.TextField(blank=True, default='', max_length=750),
        ),
        migrations.AlterField(
            model_name='masaje',
            name='descriptionSh',
            field=models.TextField(blank=True, default='', max_length=250),
        ),
        migrations.AlterField(
            model_name='masaje',
            name='foto',
            field=models.ImageField(blank=True, default='default.jpg', upload_to='masajes/static/masajes/'),
        ),
        migrations.AlterField(
            model_name='tipomasaje',
            name='foto',
            field=models.ImageField(blank=True, default='default.jpg', upload_to='masajes/static/masajes/'),
        ),
    ]
