# Generated by Django 4.2.8 on 2025-01-10 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0016_article_views"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="total_article_like",
            field=models.IntegerField(default=0, verbose_name="좋아요 수"),
        ),
    ]
