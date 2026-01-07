from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0004_add_status_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='joblisting',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
