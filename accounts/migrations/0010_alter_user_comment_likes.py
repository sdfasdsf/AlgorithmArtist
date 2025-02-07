# Generated by Django 4.2.8 on 2025-01-09 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0015_remove_article_title_article_article_title_and_more"),
        ("accounts", "0009_user_comment_likes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="comment_likes",
            field=models.ManyToManyField(
                blank=True, related_name="liked", to="articles.comment"
            ),
        ),
    ]
