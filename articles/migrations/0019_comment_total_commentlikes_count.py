# Generated by Django 4.2.8 on 2025-01-10 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0018_rename_total_article_like_article_total_likes_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="total_commentlikes_count",
            field=models.IntegerField(default=0, verbose_name="좋아요 수"),
        ),
    ]
