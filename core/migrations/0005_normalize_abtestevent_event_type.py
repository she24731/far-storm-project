# Generated migration for normalizing legacy ABTestEvent event_type values

from django.db import migrations


def forwards(apps, schema_editor):
    """
    Normalize legacy event_type values to canonical ones.
    Converts 'Variant Shown' → 'exposure' and 'Button Clicked' → 'conversion'.
    """
    ABTestEvent = apps.get_model("core", "ABTestEvent")
    
    # Normalize any legacy names to canonical ones
    ABTestEvent.objects.filter(event_type__iexact="Variant Shown").update(event_type="exposure")
    ABTestEvent.objects.filter(event_type__iexact="Button Clicked").update(event_type="conversion")


def backwards(apps, schema_editor):
    """
    Reverse migration: map back to legacy names.
    Note: This is optional and may not be needed, but included for completeness.
    """
    ABTestEvent = apps.get_model("core", "ABTestEvent")
    
    # Map back to legacy names (if needed)
    ABTestEvent.objects.filter(event_type="exposure").update(event_type="Variant Shown")
    ABTestEvent.objects.filter(event_type="conversion").update(event_type="Button Clicked")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_abtestevent_options_abtestevent_endpoint_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
