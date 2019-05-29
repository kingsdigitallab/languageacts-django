from django.db import migrations, models
import django.db.models.deletion
import wagtail.search.index


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailredirects', '0006_redirect_increase_max_length'),
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('wagtailforms', '0003_capitalizeverbose'),
        ('cms', '0034_auto_20190129_1533'),
    ]

    operations = [
        migrations.CreateModel(
            name='POSLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
            options={
                'verbose_name': 'Eagle POS Label',
                'verbose_name_plural': 'Eagle POS Labels',
            },
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
        migrations.RemoveField(
            model_name='recordentrym2m',
            name='related_word',
        ),
        migrations.RemoveField(
            model_name='recordentrym2m',
            name='source',
        ),
        migrations.RemoveField(
            model_name='recordentrywordtype',
            name='source',
        ),
        migrations.RemoveField(
            model_name='recordentrywordtype',
            name='word_type',
        ),
        migrations.RemoveField(
            model_name='recordrankingandfrequencyentry',
            name='biblioref',
        ),
        migrations.RemoveField(
            model_name='recordrankingandfrequencyentry',
            name='page_ptr',
        ),
        migrations.DeleteModel(
            name='WordType',
        ),
        migrations.AlterModelOptions(
            name='lemmalanguage',
            options={'ordering': ['orderno'], 'verbose_name': 'Lemma Language', 'verbose_name_plural': 'Lemma Languages'},
        ),
        migrations.RemoveField(
            model_name='recordentry',
            name='first_attest_year',
        ),
        migrations.RemoveField(
            model_name='recordentry',
            name='hist_freq_data',
        ),
        migrations.RemoveField(
            model_name='recordentry',
            name='hist_freq_x_label',
        ),
        migrations.RemoveField(
            model_name='recordentry',
            name='hist_freq_y_label',
        ),
        migrations.RemoveField(
            model_name='recordentry',
            name='period',
        ),
        migrations.AddField(
            model_name='lemmalanguage',
            name='orderno',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='recordentry',
            name='diaphasic_variation',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='recordentry',
            name='diatopic_variation',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='recordentry',
            name='hist_freq',
            field=models.CharField(blank=True, max_length=2048, null=True, verbose_name='Historical Frequency'),
        ),
        migrations.AddField(
            model_name='recordentry',
            name='lemma',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='recordentry',
            name='morph_related_words',
            field=models.CharField(blank=True, max_length=2048, null=True, verbose_name='Morphologically Related Words'),
        ),
        migrations.AddField(
            model_name='recordentry',
            name='ranking_freq',
            field=models.CharField(blank=True, max_length=2048, null=True, verbose_name='Ranking/Frequency'),
        ),
        migrations.AddField(
            model_name='recordpage',
            name='latin_lemma',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='recordpage',
            name='latin_meaning',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AlterField(
            model_name='recordentry',
            name='first_attest',
            field=models.CharField(blank=True, max_length=2048, null=True, verbose_name='First Attestation'),
        ),
        migrations.AlterField(
            model_name='recordentry',
            name='hist_freq_image',
            field=models.ForeignKey(blank=True, help_text='Pre-rendered graph will take priority over manual data            inputted above.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='wagtailimages.Image', verbose_name='[OR] Pre-rendered Graph Image'),
        ),
        migrations.DeleteModel(
            name='RecordEntryM2M',
        ),
        migrations.DeleteModel(
            name='RecordEntryWordType',
        ),
        migrations.DeleteModel(
            name='RecordRankingAndFrequencyEntry',
        ),
        migrations.AddField(
            model_name='recordentry',
            name='pos',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='cms.POSLabel'),
        ),
        migrations.AddField(
            model_name='recordpage',
            name='latin_pos',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='cms.POSLabel'),
        ),
        migrations.DeleteModel(
            name='BiblioRef',
        ),
        migrations.DeleteModel(
            name='LemmaPeriod',
        ),
    ]
