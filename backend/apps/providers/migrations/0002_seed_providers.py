"""Seed five disabled provider records (no credentials, external calls, or activation).

This data migration is deliberately non-destructive on reverse: user-modified
provider records are not deleted by rolling back the seed-only migration.
"""

from django.db import migrations


PROVIDERS = (
    ("chatgpt", "ChatGPT"),
    ("gemini", "Gemini"),
    ("deepseek", "DeepSeek"),
    ("qwen", "Qwen"),
    ("zai", "Z.ai"),
)


def seed_providers(apps, schema_editor):
    provider_model = apps.get_model("providers", "Provider")
    for slug, name in PROVIDERS:
        provider_model.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "is_enabled": False, "homepage_url": ""},
        )


class Migration(migrations.Migration):
    dependencies = [("providers", "0001_initial")]

    operations = [migrations.RunPython(seed_providers, migrations.RunPython.noop)]
