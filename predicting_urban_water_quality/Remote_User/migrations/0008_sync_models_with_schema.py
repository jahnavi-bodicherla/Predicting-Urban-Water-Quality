"""Brings the migration history in line with Remote_User/models.py.

Migrations 0002-0007 were carried over from an older project and describe models
(ClientPosts_Model, review_Model) that models.py no longer defines, while the
three models the app actually uses (water_quality_type, detection_accuracy,
detection_ratio) had no migration at all -- their tables were created by hand and
only ever existed in the MySQL dump. This migration removes the dead models,
creates the missing ones and squares up ClientRegister_Model, so that a fresh
`manage.py migrate` produces a complete, working database on SQLite.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Remote_User', '0007_clientposts_model_names'),
    ]

    operations = [
        # --- drop models that no longer exist in models.py -------------------
        migrations.DeleteModel(name='ClientPosts_Model'),
        migrations.DeleteModel(name='review_Model'),

        # --- square up ClientRegister_Model with models.py -------------------
        migrations.AlterField(
            model_name='clientregister_model',
            name='phoneno',
            field=models.CharField(max_length=10),
        ),
        migrations.AddField(
            model_name='clientregister_model',
            name='address',
            field=models.CharField(default='', max_length=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clientregister_model',
            name='gender',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),

        # --- models used by the prediction views -----------------------------
        migrations.CreateModel(
            name='water_quality_type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('State_Name', models.CharField(max_length=30000)),
                ('District_Name', models.CharField(max_length=30000)),
                ('Block_Name', models.CharField(max_length=30000)),
                ('Panchayat_Name', models.CharField(max_length=30000)),
                ('Village_Name', models.CharField(max_length=30000)),
                ('Habitation_Name', models.CharField(max_length=30000)),
                ('Year', models.CharField(max_length=30000)),
                ('Prediction', models.CharField(max_length=30000)),
            ],
        ),
        migrations.CreateModel(
            name='detection_accuracy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('names', models.CharField(max_length=300)),
                ('ratio', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='detection_ratio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('names', models.CharField(max_length=300)),
                ('ratio', models.CharField(max_length=300)),
            ],
        ),
    ]
