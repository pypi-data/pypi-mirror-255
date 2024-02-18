import ckeditor.fields
import django.contrib.sites.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('django_simple_file_handler', '0008_auto_20210702_1604'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('recipient_name', models.CharField(default='Anonymous', max_length=255)),
                ('email', models.EmailField(max_length=254)),
            ],
            options={
                'verbose_name_plural': 'email addresses',
            },
        ),
        migrations.CreateModel(
            name='FormDefinition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('definition_name', models.CharField(max_length=255, unique=True)),
                ('send_email', models.BooleanField(default=True)),
                ('subject_prefix', models.CharField(blank=True, default='Form email', max_length=255, verbose_name='subject prefix string')),
                ('email_html', models.CharField(default='django_simple_forms/internal/emails/form_email.html', max_length=255, verbose_name='HTML email template')),
                ('email_txt', models.CharField(default='django_simple_forms/internal/emails/form_email.txt', max_length=255, verbose_name='text email template')),
                ('reply_first', models.CharField(blank=True, max_length=255, verbose_name='reply-to first name CharField')),
                ('reply_last', models.CharField(blank=True, max_length=255, verbose_name='reply-to last name CharField')),
                ('reply_address', models.CharField(blank=True, max_length=255, verbose_name='reply-to email EmailField')),
                ('email_subject', models.CharField(blank=True, max_length=255, verbose_name='email subject CharField')),
                ('create_pdf', models.BooleanField(default=False, verbose_name='create PDF')),
                ('pdf_template', models.CharField(default='django_simple_forms/internal/pdfs/default_pdf.html', max_length=255, verbose_name='PDF template')),
                ('editable_data', models.BooleanField(default=False)),
                ('sort_created', models.BooleanField(default=True, verbose_name='sort by date created (if no table fields specified)')),
                ('form_html', models.CharField(default='django_simple_forms/external/pages/form_page.html', max_length=255, verbose_name='form HTML (external)')),
                ('form_css', models.CharField(default='django_simple_forms/external/css/form_style.css', max_length=255, verbose_name='form CSS (external)')),
                ('success_html', models.CharField(default='django_simple_forms/external/pages/form_submitted.html', max_length=255, verbose_name='success page HTML (external)')),
                ('button_label', models.CharField(default='Submit', max_length=255)),
                ('post_html', models.CharField(default='django_simple_forms/internal/pages/post_view.html', max_length=255, verbose_name='response HTML (internal)')),
                ('post_form_html', models.CharField(default='django_simple_forms/internal/pages/post_form.html', max_length=255, verbose_name='form HTML (internal)')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FormInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('alt_title', models.CharField(blank=True, max_length=255)),
                ('published', models.BooleanField(default=False)),
                ('descriptive_text', ckeditor.fields.RichTextField(blank=True)),
                ('data_json', models.JSONField(blank=True, null=True)),
                ('footer_text', ckeditor.fields.RichTextField(blank=True)),
                ('email_addresses', models.ManyToManyField(blank=True, related_name='form_instances', to='django_simple_forms.EmailAddress')),
                ('form_definition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_instances', to='django_simple_forms.formdefinition')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='FormsSiteProfile',
            fields=[
                ('site_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='sites.site')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('protocol', models.CharField(default='https://', max_length=255)),
            ],
            options={
                'verbose_name': 'site profile',
            },
            bases=('sites.site', models.Model),
            managers=[
                ('objects', django.contrib.sites.models.SiteManager()),
            ],
        ),
        migrations.CreateModel(
            name='InputDefinition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('definition_name', models.CharField(max_length=255, unique=True)),
                ('field_type', models.CharField(choices=[('BooleanField', 'BooleanField'), ('CharField', 'CharField'), ('ChoiceField', 'ChoiceField'), ('DateField', 'DateField'), ('EmailField', 'EmailField'), ('MultipleChoiceField', 'MultipleChoiceField'), ('TimeField', 'TimeField')], default='CharField', max_length=255)),
                ('label', models.CharField(max_length=255)),
                ('label_suffix', models.CharField(default=':', max_length=255)),
                ('min_length', models.PositiveIntegerField(blank=True, null=True, verbose_name='min length (CharField and EmailField only)')),
                ('max_length', models.PositiveIntegerField(blank=True, default=255, null=True, verbose_name='max length (CharField and EmailField only)')),
                ('initial', models.CharField(blank=True, max_length=255, verbose_name='initial value')),
                ('initial_boolean', models.BooleanField(default=False, verbose_name='initial True (BooleanField only)')),
                ('boolean_true', models.CharField(blank=True, max_length=255, verbose_name='boolean true string (if select widget)')),
                ('boolean_false', models.CharField(blank=True, max_length=255, verbose_name='boolean false string (if select widget)')),
                ('empty_value', models.CharField(blank=True, max_length=255, verbose_name='empty value (CharField only)')),
                ('help_text', ckeditor.fields.RichTextField(blank=True)),
                ('strip', models.BooleanField(default=True, verbose_name='strip (CharField only)')),
                ('required', models.BooleanField(default=True)),
                ('widget_type', models.CharField(choices=[('CheckboxInput', 'CheckboxInput'), ('CheckboxSelectMultiple', 'CheckboxSelectMultiple'), ('DateInput', 'DateInput'), ('EmailInput', 'EmailInput'), ('Select', 'Select'), ('SelectMultiple', 'SelectMultiple'), ('Textarea', 'Textarea'), ('TextInput', 'TextInput'), ('TimeInput', 'TimeInput')], default='TextInput', max_length=255)),
                ('widget_autocomplete', models.BooleanField(default=True, verbose_name='autocomplete')),
                ('widget_title', models.CharField(blank=True, max_length=255, verbose_name='title')),
                ('widget_class', models.CharField(blank=True, max_length=255, verbose_name='class')),
            ],
            options={
                'ordering': ['definition_name'],
            },
        ),
        migrations.CreateModel(
            name='InputInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('field_name', models.CharField(max_length=255)),
                ('admin_only', models.BooleanField(default=False)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('form_definition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='input_instances', to='django_simple_forms.formdefinition')),
                ('input_definition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='input_instances', to='django_simple_forms.inputdefinition')),
            ],
            options={
                'verbose_name': 'input',
                'ordering': ['sort_order'],
            },
        ),
        migrations.CreateModel(
            name='PostCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('category', models.CharField(default='Uncategorized', max_length=255)),
                ('data_json', models.JSONField(blank=True, null=True)),
                ('form_instance', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='post_category', to='django_simple_forms.forminstance')),
            ],
            options={
                'verbose_name': 'form responses',
                'verbose_name_plural': 'form responses',
            },
        ),
        migrations.CreateModel(
            name='PostPDF',
            fields=[
            ],
            options={
                'verbose_name': 'post PDF',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('django_simple_file_handler.privatepdf',),
        ),
        migrations.CreateModel(
            name='TableField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('column_name', models.CharField(blank=True, max_length=255, verbose_name='custom column header')),
                ('tally_column', models.BooleanField(default=False, verbose_name='tally column (BooleanField only)')),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('form_definition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='table_fields', to='django_simple_forms.formdefinition')),
                ('input_instance', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='table_fields', to='django_simple_forms.inputinstance')),
            ],
            options={
                'ordering': ['sort_order'],
            },
        ),
        migrations.CreateModel(
            name='PostInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('data_json', models.JSONField(blank=True, null=True)),
                ('pdf', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='post_instance', to='django_simple_forms.postpdf')),
                ('post_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_instances', to='django_simple_forms.postcategory')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='ErrorDefinition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('value', models.CharField(max_length=255)),
                ('key', models.CharField(choices=[('required', 'required'), ('invalid', 'invalid (Datefield, EmailField, TimeField only)'), ('invalid_choice', 'invalid_choice (ChoiceField, MultipleChoiceField only)'), ('invalid_list', 'invalid_list (MultipleChoiceField only)'), ('max_length', 'max_length (CharField only)'), ('min_length', 'min_length (CharField only)')], default='required', max_length=255)),
                ('input_definition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_simple_forms.inputdefinition')),
            ],
            options={
                'verbose_name': 'error message',
            },
        ),
        migrations.CreateModel(
            name='ChoiceDefinition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('value', models.CharField(max_length=255)),
                ('display', models.CharField(max_length=255)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('input_definition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_simple_forms.inputdefinition')),
            ],
            options={
                'verbose_name': 'choice',
                'verbose_name_plural': 'choices (ChoiceField and MultipleChoiceField only',
                'ordering': ['sort_order'],
            },
        ),
    ]
