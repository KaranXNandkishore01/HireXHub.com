from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0003_add_application_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], default='Pending', max_length=20),
        ),
    ]
