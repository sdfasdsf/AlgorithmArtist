# Generated by Django 4.2.8 on 2025-01-16 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("AI", "0001_initial"),
        ("accounts", "0010_alter_user_comment_likes"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="Conversation_List",
            field=models.ManyToManyField(
                blank=True, related_name="AIConversation", to="AI.ai"
            ),
        ),
    ]
