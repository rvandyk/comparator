# Generated by Django 2.0.6 on 2018-06-13 09:20

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comparator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('fields', models.TextField()),
                ('result', models.TextField()),
                ('running', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CrawlerModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('url', models.TextField()),
                ('attributesJson', models.TextField()),
                ('running', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ScrapyItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.CharField(max_length=100, null=True)),
                ('data', models.TextField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('crawler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.CrawlerModel')),
            ],
        ),
        migrations.AddField(
            model_name='comparator',
            name='model1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='model1', to='mainapp.CrawlerModel'),
        ),
        migrations.AddField(
            model_name='comparator',
            name='model2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='model2', to='mainapp.CrawlerModel'),
        ),
    ]
