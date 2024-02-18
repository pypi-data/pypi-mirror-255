import copy
from datetime import (
    date,
    datetime,
    time,
)


from django.contrib.sites.models import (
    Site,
)
from django.db import (
    models,
)
from django.urls import (
    reverse,
)
from django.utils import (
    timezone,
)
from django.utils.crypto import (
    get_random_string,
)
from django.utils.formats import (
    localize,
)
from django.utils.text import (
    slugify,
)


from ckeditor.fields import (
    RichTextField,
)
from django_simple_file_handler.models import (
    PrivatePDF,
)


class BaseMixin(models.Model):
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        'last updated',
        auto_now=True,
    )

    class Meta:
        abstract = True


class FormsSiteProfile(BaseMixin, Site):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    protocol = models.CharField(
        max_length=255,
        default='https://',
    )

    def protocol_domain(self):
        return f'{self.protocol}{self.domain}'

    class Meta:
        verbose_name = 'site profile'


class EmailAddress(BaseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    recipient_name = models.CharField(
        max_length=255,
        default='Anonymous',
    )
    email = models.EmailField(
    )

    def __str__(self):
        return self.email

    def inst_count(self):
        count = self.form_instances.all().count()
        return str(count)

    inst_count.short_description = 'forms'

    class Meta:
        verbose_name_plural = 'email addresses'


class DictDefinition(BaseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    input_definition = models.ForeignKey(
        'InputDefinition',
        on_delete=models.CASCADE,
    )
    value = models.CharField(
        max_length=255,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.input_definition.downstream_update()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.input_definition.downstream_update()

    class Meta:
        abstract = True


ERROR_CHOICES = [
    ('required', 'required'),
    ('invalid', 'invalid (Datefield, EmailField, TimeField only)'),
    ('invalid_choice', 'invalid_choice (ChoiceField, MultipleChoiceField only)'),
    ('invalid_list', 'invalid_list (MultipleChoiceField only)'),
    ('max_length', 'max_length (CharField only)'),
    ('min_length', 'min_length (CharField only)'),
]


class ErrorDefinition(DictDefinition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    key = models.CharField(
        max_length=255,
        choices=ERROR_CHOICES,
        default='required'
    )

    def __str__(self):
        return f'{self.key}: {self.value}'

    class Meta:
        verbose_name = 'error message'


class ChoiceDefinition(DictDefinition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    display = models.CharField(
        max_length=255,
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False
    )

    def __str__(self):
        return f'{self.value}: {self.display}'

    class Meta(object):
        ordering = [
            'sort_order',
        ]
        verbose_name = 'choice'
        verbose_name_plural = 'choices (ChoiceField and MultipleChoiceField only'


FIELD_TYPES = [
    ('BooleanField', 'BooleanField'),
    ('CharField', 'CharField'),
    ('ChoiceField', 'ChoiceField'),
    ('DateField', 'DateField'),
    ('EmailField', 'EmailField'),
    ('MultipleChoiceField', 'MultipleChoiceField'),
    ('TimeField', 'TimeField'),
]


WIDGET_TYPES = [
    ('CheckboxInput', 'CheckboxInput'),
    ('CheckboxSelectMultiple', 'CheckboxSelectMultiple'),
    ('DateInput', 'DateInput'),
    ('EmailInput', 'EmailInput'),
    ('Select', 'Select'),
    ('SelectMultiple', 'SelectMultiple'),
    ('Textarea', 'Textarea'),
    ('TextInput', 'TextInput'),
    ('TimeInput', 'TimeInput'),
]


class InputDefinition(BaseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    definition_name = models.CharField(
        max_length=255,
        unique=True,
    )
    field_type = models.CharField(
        max_length=255,
        choices=FIELD_TYPES,
        default='CharField',
    )
    label = models.CharField(
        max_length=255,
    )
    label_suffix = models.CharField(
        max_length=255,
        default=':',
    )
    min_length = models.PositiveIntegerField(
        'min length (CharField and EmailField only)',
        blank=True,
        null=True,
    )
    max_length = models.PositiveIntegerField(
        'max length (CharField and EmailField only)',
        default=255,
        blank=True,
        null=True,
    )
    initial = models.CharField(
        'initial value',
        max_length=255,
        blank=True,
    )
    initial_boolean = models.BooleanField(
        'initial True (BooleanField only)',
        default=False,
    )
    boolean_true = models.CharField(
        'boolean true string (if select widget)',
        max_length=255,
        blank=True,
    )
    boolean_false = models.CharField(
        'boolean false string (if select widget)',
        max_length=255,
        blank=True,
    )
    empty_value = models.CharField(
        'empty value (CharField only)',
        max_length=255,
        blank=True,
    )
    help_text = RichTextField(
        blank=True,
    )
    strip = models.BooleanField(
        'strip (CharField only)',
        default=True,
    )
    required = models.BooleanField(
        default=True,
    )
    widget_type = models.CharField(
        max_length=255,
        choices=WIDGET_TYPES,
        default='TextInput',
    )
    widget_autocomplete = models.BooleanField(
        'autocomplete',
        default=True,
    )
    widget_title = models.CharField(
        'title',
        max_length=255,
        blank=True,
    )
    widget_class = models.CharField(
        'class',
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return self.definition_name

    def full_label(self):
        return f'{self.label}{self.label_suffix}'

    def dict_data(self):
        field_data = {
            'field_type': self.field_type,
            'field_args': {
                'label': self.label,
                'label_suffix': self.label_suffix,
                'required': self.required,
            }
        }
        field_args = field_data['field_args']
        if self.help_text:
            field_args['help_text'] = self.help_text
        error_messages = {
            'required': 'Field is required',
            'invalid': 'Invalid value',
            'invalid_choice': 'Invalid choice',
            'invalid_list': 'Invalid list',
            'max_length': 'Maximum length exceeded',
            'min_length': 'Minimum length not met',
        }
        error_definitions = ErrorDefinition.objects.filter(
            input_definition=self,
        )
        if error_definitions:
            for item in error_definitions.all():
                error_messages[item.key] = item.value
        field_args['error_messages'] = error_messages
        if self.field_type == 'BooleanField':
            if self.widget_type == 'Select':
                field_data['field_type'] = 'TypedChoiceField'
                field_args['boolean_dicts'] = [{False: self.boolean_false}, {True: self.boolean_true}]
                if self.initial_boolean:
                    field_args['initial'] = 'true'
                else:
                    field_args['initial'] = 'false'
            else:
                if self.initial_boolean:
                    field_args['initial'] = True
        else:
            if self.initial:
                field_args['initial'] = self.initial
        if self.field_type == 'CharField' or self.field_type == 'EmailField':
            if self.min_length:
                field_args['min_length'] = self.min_length
            if self.max_length:
                field_args['max_length'] = self.max_length
            if self.field_type == 'CharField':
                field_args['strip'] = self.strip
                field_args['empty_value'] = self.empty_value
        if self.field_type == 'ChoiceField' or self.field_type == 'MultipleChoiceField':
            choice_definitions = ChoiceDefinition.objects.filter(
                input_definition=self,
            )
            choice_dicts = [{item.value: item.display} for item in choice_definitions]
            field_args['choice_dicts'] = choice_dicts
        widget_data = {
            'widget_type': self.widget_type,
            'widget_attrs': {
            },
        }
        widget_attrs = widget_data['widget_attrs']      # Check which of these work for which field type
        if not self.widget_autocomplete:
            widget_attrs['autocomplete'] = 'off'
        if self.widget_title:
            widget_attrs['title'] = self.widget_title
        if self.widget_type == 'CheckboxSelectMultiple':
            default_class = 'checkbox_select_multiple'
        else:
            default_class = ''
        if default_class and self.widget_class:
            class_space = ' '
        else:
            class_space = ''
        class_str = f'{default_class}{class_space}{self.widget_class}'
        if class_str:
            widget_attrs['class'] = class_str
        data = {
            'field_data': field_data,
            'widget_data': widget_data,
        }
        return data

    def inst_count(self):
        count = self.input_instances.all().count()
        return str(count)

    inst_count.short_description = 'instances'

    def downstream_update(self, def_delete=False):
        for instance in self.input_instances.all():
            instance.downstream_update(
                def_delete=def_delete,
            )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.downstream_update()

    def delete(self, *args, **kwargs):
        self.downstream_update(
            def_delete=True,
        )
        super().delete(*args, **kwargs)

    class Meta:
        ordering = [
            'definition_name',
        ]


class InputInstance(BaseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    form_definition = models.ForeignKey(
        'FormDefinition',
        on_delete=models.CASCADE,
        related_name='input_instances',
    )
    input_definition = models.ForeignKey(
        'InputDefinition',
        on_delete=models.CASCADE,
        related_name='input_instances',
    )
    field_name = models.CharField(
        max_length=255,
    )
    admin_only = models.BooleanField(
        default=False,
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False
    )

    def __str__(self):
        return self.field_name

    def dict_data(self):
        if self.input_definition:
            data = self.input_definition.dict_data()
            data['field_data']['field_name'] = self.field_name
            data['admin_only'] = self.admin_only
            return data

    def downstream_update(self, def_delete=False):
        if def_delete:
            self.input_definition = None
            self.delete()
        self.form_definition.downstream_update()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.downstream_update()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.downstream_update()

    class Meta(object):
        ordering = [
            'sort_order',
        ]
        verbose_name = 'input'


class TableField(BaseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    form_definition = models.ForeignKey(
        'FormDefinition',
        on_delete=models.CASCADE,
        related_name='table_fields',
    )
    input_instance = models.OneToOneField(
        'InputInstance',
        on_delete=models.CASCADE,
        related_name='table_fields',
    )
    column_name = models.CharField(
        'custom column header',
        max_length=255,
        blank=True,
    )
    tally_column = models.BooleanField(
        'tally column (BooleanField only)',
        default=False,
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False
    )

    class Meta(object):
        ordering = [
            'sort_order',
        ]


class FormDefinition(BaseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.from_admin = False

    definition_name = models.CharField(
        max_length=255,
        unique=True,
    )
    send_email = models.BooleanField(
        default=True,
    )
    subject_prefix = models.CharField(
        'subject prefix string',
        max_length=255,
        blank=True,
        default='Form email',
    )
    email_html = models.CharField(
        'HTML email template',
        max_length=255,
        default='django_simple_forms/internal/emails/form_email.html',
    )
    email_txt = models.CharField(
        'text email template',
        max_length=255,
        default='django_simple_forms/internal/emails/form_email.txt',
    )
    reply_first = models.CharField(
        'reply-to first name CharField',
        max_length=255,
        blank=True,
    )
    reply_last = models.CharField(
        'reply-to last name CharField',
        max_length=255,
        blank=True,
    )
    reply_address = models.CharField(
        'reply-to email EmailField',
        max_length=255,
        blank=True,
    )
    email_subject = models.CharField(
        'email subject CharField',
        max_length=255,
        blank=True,
    )
    create_pdf = models.BooleanField(
        'create PDF',
        default=False,
    )
    pdf_template = models.CharField(
        'PDF template',
        max_length=255,
        default='django_simple_forms/internal/pdfs/default_pdf.html',
    )
    editable_data = models.BooleanField(
        default=False,
    )
    sort_created = models.BooleanField(
        'sort by date created (if no table fields specified)',
        default=True,
    )
    form_html = models.CharField(
        'form HTML (external)',
        max_length=255,
        default='django_simple_forms/external/pages/form_page.html',
    )
    form_css = models.CharField(
        'form CSS (external)',
        max_length=255,
        default='django_simple_forms/external/css/form_style.css',
    )
    success_html = models.CharField(
        'success page HTML (external)',
        max_length=255,
        default='django_simple_forms/external/pages/form_submitted.html',
    )
    button_label = models.CharField(
        max_length=255,
        default='Submit',
    )
    post_html = models.CharField(
        'response HTML (internal)',
        max_length=255,
        default='django_simple_forms/internal/pages/post_view.html',
    )
    post_form_html = models.CharField(
        'form HTML (internal)',
        max_length=255,
        default='django_simple_forms/internal/pages/post_form.html',
    )

    def __str__(self):
        return self.definition_name

    def inst_count(self):
        count = self.form_instances.all().count()
        return str(count)

    inst_count.short_description = 'instances'

    def table_header(self, field):
        if field.column_name:
            header = field.column_name
        else:
            header = field.input_instance.input_definition.full_label()
        return header

    def dict_data(self):
        data = {
            'field_dicts': [instance.dict_data() for instance in self.input_instances.all()],
            'table_fields': [{field_table.input_instance.field_name: self.table_header(field_table)}
                             for field_table in self.table_fields.all()],
            'tally_fields': [field_tally.input_instance.field_name
                             for field_tally in self.table_fields.all()
                             if field_tally.tally_column
                             and field_tally.input_instance.input_definition.field_type == 'BooleanField'],
            'sort_created': self.sort_created,
            'date_fields': [field_date.field_name
                            for field_date in self.input_instances.all()
                            if field_date.input_definition.field_type == 'DateField'],
            'time_fields': [field_time.field_name
                            for field_time in self.input_instances.all()
                            if field_time.input_definition.field_type == 'TimeField'],
        }
        return data

    def downstream_update(self):
        for instance in self.form_instances.all():
            instance.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.from_admin:
            self.downstream_update()


class FormInstance(BaseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    title = models.CharField(
        max_length=255,
        unique=True,
    )
    alt_title = models.CharField(
        max_length=255,
        blank=True,
    )
    form_definition = models.ForeignKey(
        'FormDefinition',
        on_delete=models.CASCADE,
        related_name='form_instances',
    )
    published = models.BooleanField(
        default=False,
    )
    descriptive_text = RichTextField(
        blank=True,
    )
    email_addresses = models.ManyToManyField(
        EmailAddress,
        related_name='form_instances',
        blank=True,
    )
    data_json = models.JSONField(
        blank=True,
        null=True,
    )
    footer_text = RichTextField(
        blank=True,
    )

    def __str__(self):
        return self.title

    def form_url(self):
        url_str = reverse(
            'django_simple_forms:form_page',
            kwargs={
                'pk': self.pk,
                'title_slug': slugify(self.title),
            },
        )
        return url_str

    def dict_data(self):
        return self.data_json

    def save(self, *args, **kwargs):
        self.data_json = self.form_definition.dict_data()
        super().save(*args, **kwargs)
        post_category, created = PostCategory.objects.get_or_create(
            form_instance=self,
        )
        post_category.save()

    class Meta:
        ordering = [
            'title',
        ]


class PostCategory(BaseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    category = models.CharField(
        max_length=255,
        default='Uncategorized',
    )
    form_instance = models.OneToOneField(
        'FormInstance',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='post_category',
    )
    data_json = models.JSONField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.category

    def inst_count(self):
        count = self.post_instances.all().count()
        return str(count)

    inst_count.short_description = 'response count'

    def save(self, *args, **kwargs):
        if self.form_instance:
            self.category = self.form_instance.title
            self.data_json = {
                'table_fields': self.form_instance.data_json['table_fields'],
                'tally_fields': self.form_instance.data_json['tally_fields'],
                'sort_created': self.form_instance.data_json['sort_created'],
                'date_fields': self.form_instance.data_json['date_fields'],
                'time_fields': self.form_instance.data_json['time_fields'],
            }
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for post in self.post_instances.all():
            post.delete()
        if not self.form_instance:
            super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'form responses'
        verbose_name_plural = 'form responses'


class PostPDF(PrivatePDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = 'post PDF'


def format_data(form_instance=None, cleaned_data=None):
    if form_instance and cleaned_data:
        for key, value in cleaned_data.items():
            if value is None:
                cleaned_data[key] = ''
            if isinstance(value, date):
                cleaned_data[key] = value.strftime('%Y-%m-%d')
            if isinstance(value, time):
                cleaned_data[key] = value.strftime('%H:%M:%S')
            if isinstance(value, str):
                cleaned_data[key] = value.replace('\r\n', '<br>')
            if isinstance(value, list):
                formatted_list = []
                for data in cleaned_data[key]:
                    if isinstance(data, str):
                        data.replace('\r\n', '<br>')
                    formatted_list.append(data)
                cleaned_data[key] = formatted_list
        label_dicts = [
            {item['field_data']['field_name']:
                item['field_data']['field_args']['label'] + item['field_data']['field_args']['label_suffix']}
            for item in form_instance.dict_data()['field_dicts']
        ]
        stored_dict = {'data_dicts': []}
        for pair in label_dicts:
            for key, value in pair.items():
                data_value = cleaned_data[key]
                if isinstance(data_value, list):
                    value_list = [value] + data_value
                    stored_dict['data_dicts'].append({key: value_list})
                else:
                    stored_dict['data_dicts'].append({key: [value, data_value]})
    else:
        stored_dict = {}
    return stored_dict


class PostInstanceManager(models.Manager):
    def create_instance(self, form_instance=None, cleaned_data=None):
        stored_dict = format_data(
            form_instance=form_instance,
            cleaned_data=cleaned_data,
        )
        post = self.create(
            post_category=form_instance.post_category,
            data_json=stored_dict,
        )
        return post


class PostInstance(BaseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    post_category = models.ForeignKey(
        'PostCategory',
        on_delete=models.CASCADE,
        related_name='post_instances',
    )
    data_json = models.JSONField(
        blank=True,
        null=True,
    )
    pdf = models.OneToOneField(
        'PostPDF',
        on_delete=models.SET_NULL,
        related_name='post_instance',
        blank=True,
        null=True,
    )
    objects = PostInstanceManager()

    def output_dict(self):
        output = {}
        if self.data_json:
            try:
                data_dicts = self.data_json['data_dicts']
                for pair in data_dicts:
                    for key, value in pair.items():
                        output[key] = value
            except KeyError:
                pass
        return output

    def output_no_br(self):
        output_copy = copy.deepcopy(self.output_dict())
        for key, value in output_copy.items():
            unformatted_list = [item.replace('<br>', '\r\n') if isinstance(item, str) else item for item in value]
            output_copy[key] = unformatted_list
        return output_copy

    def output_formatted_date_time(self):
        output_dict_copy = copy.deepcopy(self.output_dict())
        for date_field in self.data_json['date_fields']:
            try:
                date_in = output_dict_copy[date_field][1]
                date_obj = datetime.strptime(date_in, '%Y-%m-%d')
                date_out = localize(date_obj.date())
                output_dict_copy[date_field][1] = date_out
            except (KeyError, ValueError) as error:
                pass
        for time_field in self.data_json['time_fields']:
            try:
                time_in = output_dict_copy[time_field][1]
                time_obj = datetime.strptime(time_in, '%H:%M:%S')
                time_out = localize(time_obj.time())
                output_dict_copy[time_field][1] = time_out
            except (KeyError, ValueError) as error:
                pass
        return output_dict_copy

    def output_text(self):
        output_formatted_date_time = copy.deepcopy(self.output_formatted_date_time())
        for key, value in output_formatted_date_time.items():
            unformatted_list = [item.replace('<br>', '\r\n') if isinstance(item, str) else item for item in value]
            output_formatted_date_time[key] = unformatted_list
        return output_formatted_date_time

    def save(self, *args, **kwargs):
        if not self.data_json:
            self.data_json = {}
        self.data_json['date_fields'] = self.post_category.data_json['date_fields']
        self.data_json['time_fields'] = self.post_category.data_json['time_fields']
        if self.post_category.form_instance:
            if self.post_category.form_instance.form_definition.create_pdf:
                if self.pdf:
                    self.pdf.delete()
                title = self.post_category.form_instance.title
                file_title = f'{title}-{get_random_string(20)}'
                local_time = timezone.localtime(timezone.now())
                if not self.created:
                    self.created = local_time
                    self.updated = local_time
                else:
                    self.updated = local_time
                self.pdf = PostPDF.objects.create(
                    title=file_title,
                    template_location=self.post_category.form_instance.form_definition.pdf_template,
                    template_data={
                        'title': title,
                        'created': self.created,
                        'updated': self.updated,
                        'descriptive_text': self.post_category.form_instance.descriptive_text,
                        'footer_text': self.post_category.form_instance.footer_text,
                        'output_dict': self.output_dict(),
                        'output_formatted_date_time': self.output_formatted_date_time(),
                    },
                )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.pdf:
            self.pdf.delete()
        super().delete(*args, **kwargs)

    class Meta:
        ordering = [
            '-created',
        ]
