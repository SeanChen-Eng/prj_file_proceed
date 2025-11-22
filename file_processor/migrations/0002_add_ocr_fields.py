# Generated migration for OCR fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file_processor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pdfconversion',
            name='ocr_text',
            field=models.JSONField(blank=True, default=dict, help_text='Extracted text from PDF pages'),
        ),
        migrations.AddField(
            model_name='pdfconversion',
            name='ocr_status',
            field=models.CharField(choices=[('not_started', 'Not Started'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='not_started', max_length=20),
        ),
    ]