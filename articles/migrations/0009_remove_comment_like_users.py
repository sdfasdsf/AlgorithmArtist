# Generated by Django 4.2.8 on 2024-12-31 10:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0008_alter_article_image"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comment",
            name="like_users",
        ),
    ]
