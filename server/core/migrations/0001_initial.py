# Generated by Django 2.2.5 on 2019-09-24 01:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_analyst', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ailment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('calories', models.PositiveIntegerField()),
                ('carbohydrates', models.PositiveIntegerField()),
                ('protein', models.PositiveIntegerField()),
                ('fats', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birth_date', models.DateField()),
                ('weight', models.PositiveIntegerField()),
                ('height', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField(null=True)),
                ('condition', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Ailment')),
                ('log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statuses', to='core.Log')),
            ],
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField(null=True)),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='meals', to='core.Food')),
                ('log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meals', to='core.Log')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='conditions',
            field=models.ManyToManyField(blank=True, to='core.Condition'),
        ),
        migrations.AddField(
            model_name='user',
            name='info',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Info'),
        ),
    ]
