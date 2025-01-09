# Generated by Django 4.2.8 on 2025-01-09 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0014_alter_comment_comment_like"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="article",
            name="title",
        ),
        migrations.AddField(
            model_name="article",
            name="Article_title",
            field=models.CharField(
                default="", max_length=200, verbose_name="게시글 제목"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="article",
            name="movie_title",
            field=models.CharField(
                default="", max_length=200, verbose_name="영화 제목"
            ),
            preserve_default=False,
        ),
    ]
