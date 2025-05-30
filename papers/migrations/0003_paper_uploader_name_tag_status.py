# Generated by Django 4.2 on 2025-05-27 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("papers", "0002_alter_paper_options_alter_tag_options_paper_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="paper",
            name="uploader_name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="tag",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                ],
                default="approved",
                max_length=20,
            ),
        ),
    ]
