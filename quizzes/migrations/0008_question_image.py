# Generated by Django 3.1.7 on 2021-03-05 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quizzes", "0007_auto_20210303_1803"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="image",
            field=models.ImageField(blank=True, upload_to="questions_images/"),
        ),
    ]
