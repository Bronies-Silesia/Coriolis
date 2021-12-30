# Generated by Django 3.2.10 on 2021-12-30 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20211230_0208'),
    ]

    operations = [
        migrations.AddField(
            model_name='tickettype',
            name='must_pay_online',
            field=models.BooleanField(default=False, help_text='Determines if the ticket can be paid on-site or online only.', verbose_name='must pay online'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='status',
            field=models.CharField(choices=[('CNCL', 'Cancelled'), ('WAIT', 'Waiting for Organizers'), ('WPAY', 'Waiting for online payment'), ('OKNP', 'Ready (payment on site)'), ('OKPD', 'Ready (paid)'), ('USED', 'Used'), ('ONST', 'Used on site')], default='WAIT', max_length=4, verbose_name='status'),
        ),
    ]
