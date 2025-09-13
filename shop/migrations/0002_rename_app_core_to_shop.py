# Generated migration for renaming core app to shop

from django.db import migrations


def rename_content_types(apps, schema_editor):
    """Rename content types from core to shop"""
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # Update content types for all models in the app
    ContentType.objects.filter(app_label='core').update(app_label='shop')


def reverse_rename_content_types(apps, schema_editor):
    """Reverse the content type rename"""
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # Revert content types back to core
    ContentType.objects.filter(app_label='shop').update(app_label='core')


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(
            rename_content_types,
            reverse_rename_content_types,
        ),
    ]