# Generated by Django 2.2.10 on 2021-08-12 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letsgo', '0002_steppost'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('thumbnail', models.ImageField(default='none', upload_to='categories/')),
            ],
        ),
    ]
