# Generated by Django 4.2.6 on 2023-10-12 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("schedule", "0011_alter_shiftpreference_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shiftpreference",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
