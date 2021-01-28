# Generated by Django 2.2 on 2020-12-30 10:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0006_role'),
        ('article', '0021_auto_20201204_1216'),
    ]

    operations = [
        migrations.AddField(
            model_name='articleauthors',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='author_credit', to='author.Role'),
        ),
        migrations.AddField(
            model_name='articleauthors',
            name='show_in_beginning',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='articleauthors',
            name='show_in_end',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name='articleauthors',
            unique_together={('article', 'author', 'role', 'sort_order')},
        ),
    ]
