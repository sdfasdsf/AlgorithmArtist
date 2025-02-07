# Generated by Django 4.2.8 on 2024-12-31 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0009_remove_comment_like_users"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="rating",
            field=models.IntegerField(
                choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                default=1,
                verbose_name="평점",
            ),
            preserve_default=False,
        ),
    ]
