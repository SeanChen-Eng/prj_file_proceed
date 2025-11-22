# Generated migration for analysis_type field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file_processor', '0002_add_ocr_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageanalysis',
            name='analysis_type',
            field=models.CharField(choices=[('dify', 'Dify API'), ('zhipu', 'ZHIPU Vision')], default='dify', max_length=20),
        ),
    ]