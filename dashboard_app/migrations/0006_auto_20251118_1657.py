from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_app', '0005_remove_item_image'),  # adjust to your last migration
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
    