# Generated by Django 3.2.9 on 2021-12-21 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20211221_0040'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='contact_link',
            field=models.CharField(default='', help_text='Used for the big Contact Organizers button.', max_length=256, verbose_name='contact link'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='footer_content',
            field=models.TextField(default='', help_text='Muted text shown in the footer. Supports Markdown.', verbose_name='footer content'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='eventpage',
            name='slug',
            field=models.CharField(help_text='Short name used in links. Event-specific pages have precedence.', max_length=64, verbose_name='slug'),
        ),
    ]
