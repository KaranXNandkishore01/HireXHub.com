from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='full_name',
            field=models.CharField(max_length=255, default=''),
        ),
        migrations.AddField(
            model_name='application',
            name='email',
            field=models.EmailField(max_length=254, default=''),
        ),
        migrations.AddField(
            model_name='application',
            name='phone',
            field=models.CharField(max_length=20, default=''),
        ),
        migrations.AddField(
            model_name='application',
            name='start_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='application',
            name='available_interview_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='application',
            name='cover_letter',
            field=models.TextField(blank=True, default=''),
        ),
    ]
