# Generated by Django 4.2.8 on 2025-01-24 02:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0022_remove_article_genres_article_genre_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="article",
            name="writer",
        ),
    ]
