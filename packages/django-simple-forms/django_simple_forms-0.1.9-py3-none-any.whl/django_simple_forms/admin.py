from functools import (
    partial,
)
from operator import (
    itemgetter,
)


from django import (
    forms,
)
from django.core.exceptions import (
    ObjectDoesNotExist,
)
from django.forms import (
    ValidationError,
)
from django.contrib import (
    admin
)
from django.contrib.staticfiles.storage import (
    staticfiles_storage,
)
from django.http import (
    HttpResponseRedirect,
)
from django.urls import (
    reverse,
)
from django.utils import (
    timezone,
)
from django.utils.formats import (
    localize,
)
from django.utils.safestring import (
    mark_safe,
)


from adminsortable2.admin import (
    SortableAdminBase,
    SortableInlineAdminMixin,
)


from .models import (
    ChoiceDefinition,
    EmailAddress,
    ErrorDefinition,
    FormDefinition,
    FormInstance,
    FormsSiteProfile,
    InputDefinition,
    InputInstance,
    PostCategory,
    TableField,
)


class BaseAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_css = 'admin/css/django_simple_forms.css'
    actions = None
    readonly_fields = [
        'created',
        'updated',
    ]
    bottom_fieldsets = [
        (
            'Date and time information', {
                'fields': [
                    'created',
                    'updated',
                ],
                'classes': [
                    'collapse',
                ],
            }
        ),
    ]
    fieldsets = bottom_fieldsets
    list_per_page = 20

    @property
    def media(self):
        css = {
            'all': (
                self.base_css,
            ),
        }
        return forms.Media(css=css)


class FormsSiteProfileAdmin(BaseAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.top_fieldsets = [
            (
                None, {
                    'fields': [
                        'protocol',
                        'domain',
                        'name',
                    ]
                }
            ),
        ]
        self.fieldsets = self.top_fieldsets + self.bottom_fieldsets

    search_fields = [
        'protocol',
        'domain',
        'name',
    ]
    list_display = [
        'name',
        'domain',
    ]
    ordering = [
        'name',
    ]


admin.site.register(
    FormsSiteProfile,
    FormsSiteProfileAdmin,
)


class CloneableAdmin(BaseAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly_fields = [
            'clone_link',
        ] + self.readonly_fields
        self.bottom_fieldsets = [
            (
                'Clone', {
                    'fields': [
                        'clone_link',
                    ],
                }
            ),
        ] + self.bottom_fieldsets
        self.list_display = [
            'clone_link',
        ]
        self.view_name = ''

    def clone_link(self, obj):
        view_str = f'django_simple_forms:{self.view_name}'
        if obj.pk:
            url_str = reverse(
                view_str,
                kwargs={
                    'app_label': obj._meta.app_label,
                    'model_name': obj._meta.model_name,
                    'pk': obj.pk,
                },
            )
            link_str = f'<a href="{url_str}"><input type="button" class= "small_admin_button" value="Clone"></a>'
        else:
            link_str = 'Click "save and continue editing" to enable cloning.'
        return mark_safe(link_str)

    clone_link.short_description = 'clone'


class FormInstanceInline(admin.TabularInline):
    model = FormInstance.email_addresses.through
    verbose_name = 'associated form'
    verbose_name_plural = 'associated forms'
    extra = 0


class EmailAddressAdmin(CloneableAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly_fields = [
            'inst_count',
        ] + self.readonly_fields
        self.top_fieldsets = [
            (
                None, {
                    'fields': [
                        'recipient_name',
                        'email',
                    ],
                }
            ),
        ]
        self.fieldsets = self.top_fieldsets + self.bottom_fieldsets
        self.list_display = [
            'recipient_name',
            'email',
            'inst_count',
        ] + self.list_display
        self.view_name = 'clone_email_address'

    inlines = [
        FormInstanceInline,
    ]
    search_fields = [
        'recipient_name',
        'email',
    ]
    ordering = [
        'recipient_name',
    ]


admin.site.register(
    EmailAddress,
    EmailAddressAdmin,
)


class ErrorDefinitionInline(admin.TabularInline):
    model = ErrorDefinition
    fields = [
        'key',
        'value',
    ]
    extra = 0


class ChoiceDefinitionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ChoiceDefinition
    exclude = [
    ]
    extra = 0


class InputDefinitionAdmin(SortableAdminBase, CloneableAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly_fields = [
            'def_links',
            'inst_count',
        ] + self.readonly_fields
        self.top_fieldsets = [
            (
                'Field', {
                    'fields': [
                        'definition_name',
                        'field_type',
                        'label',
                        'label_suffix',
                    ],
                }
            ),
            (
                'Field arguments', {
                    'fields': [
                        'min_length',
                        'max_length',
                        'initial',
                        'initial_boolean',
                        'boolean_true',
                        'boolean_false',
                        'empty_value',
                        'help_text',
                        'strip',
                        'required',
                    ],
                    'classes': [
                        'collapse',
                    ],
                }
            ),
            (
                'Widget', {
                    'fields': [
                        'widget_type',
                    ]
                }
            ),
            (
                'Widget attributes', {
                    'fields': [
                        'widget_autocomplete',
                        'widget_title',
                        'widget_class',
                    ],
                    'classes': [
                        'collapse',
                    ],
                }
            ),
            (
                'Form definitions', {
                    'fields': [
                        'def_links',
                    ],
                    'classes': [
                        'collapse',
                    ],
                }
            ),
        ]
        self.fieldsets = self.top_fieldsets + self.bottom_fieldsets
        self.list_display = [
            'definition_name',
            'field_type',
            'widget_type',
            'required',
            'inst_count',
        ] + self.list_display
        self.view_name = 'clone_input_definition'

    inlines = [
        ErrorDefinitionInline,
        ChoiceDefinitionInline,
    ]
    search_fields = [
        'definition_name',
    ]
    ordering = [
        'definition_name',
    ]

    def def_links(self, obj):
        link_str = ''
        for item in obj.input_instances.all():
            url_str = reverse(
                f'admin:{item.form_definition._meta.app_label}_{item.form_definition._meta.model_name}_change',
                args=(item.form_definition.pk,),
            )
            link_str = f'{link_str}<a href="{url_str}">{item.form_definition.definition_name}</a><br><br>'
        if link_str:
            link_str = link_str[:-8]
        else:
            link_str = 'Input is not being used in any form definitions.'
        return mark_safe(link_str)

    def_links.short_description = 'form definitions'


admin.site.register(
    InputDefinition,
    InputDefinitionAdmin,
)


class InputInstanceInlineForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        field_name = cleaned_data.get('field_name')
        if field_name == 'email':
            raise ValidationError(
                'The field name "email" is reserved for the honeypot field.',
            )

    class Meta:
        model = InputInstance
        exclude = [
        ]


class InputInstanceInline(SortableInlineAdminMixin, admin.TabularInline):
    form = InputInstanceInlineForm
    model = InputInstance
    extra = 0


class TableFieldInline(SortableInlineAdminMixin, admin.TabularInline):
    def get_formset(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(
            self.formfield_for_dbfield,
            request=request,
            obj=obj,
        )
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        form_definition = kwargs.pop('obj', None)
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'input_instance' and form_definition:
            formfield.queryset = form_definition.input_instances
        return formfield

    model = TableField
    extra = 0


class FormDefinitionAdmin(SortableAdminBase, CloneableAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.obj = None
        self.readonly_fields = [
            'inst_links',
            'inst_count',
        ] + self.readonly_fields
        self.top_fieldsets = [
            (
                None, {
                    'fields': [
                        'definition_name',
                        'editable_data',
                        'sort_created',
                    ],
                }
            ),
            (
                'Email settings', {
                    'fields': [
                        'send_email',
                        'email_html',
                        'email_txt',
                        'reply_first',
                        'reply_last',
                        'reply_address',
                        'subject_prefix',
                        'email_subject',
                    ],
                    'classes': [
                        'collapse',
                    ],
                }
            ),
            (
                'PDF settings', {
                    'fields': [
                        'create_pdf',
                        'pdf_template',
                    ],
                    'classes': [
                        'collapse',
                    ],
                }
            ),
            (
                'Page settings', {
                    'fields': [
                        'form_html',
                        'form_css',
                        'success_html',
                        'button_label',
                        'post_html',
                        'post_form_html',
                    ],
                    'classes': [
                        'collapse',
                    ],
                }
            ),
            (
                'Form instances', {
                    'fields': [
                        'inst_links',
                    ],
                    'classes': [
                        'collapse',
                    ],
                }
            ),
        ]
        self.fieldsets = self.top_fieldsets + self.bottom_fieldsets
        self.list_display = [
            'definition_name',
            'inst_count',
        ] + self.list_display
        self.view_name = 'clone_form_definition'

    inlines = [
        InputInstanceInline,
        TableFieldInline,
    ]
    search_fields = [
        'definition_name',
    ]
    ordering = [
        'definition_name',
    ]

    def inst_links(self, obj):
        if obj.pk:
            link_str = ''
            for item in obj.form_instances.all():
                url_str = reverse(
                    f'admin:{item._meta.app_label}_{item._meta.model_name}_change',
                    args=(item.pk,),
                )
                link_str = f'{link_str}<a href="{url_str}">{item.title}</a><br><br>'
            if link_str:
                link_str = link_str[:-8]
        else:
            link_str = 'Click "save and continue editing" to get a link.'
        return mark_safe(link_str)

    inst_links.short_description = 'form instances'

    def get_form(self, request, obj=None, **kwargs):
        self.obj = obj
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.from_admin = True
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        form.save_m2m()
        for formset in formsets:
            self.save_formset(request, form, formset, change=change)
        try:
            self.obj.downstream_update()
        except AttributeError:
            pass


admin.site.register(
    FormDefinition,
    FormDefinitionAdmin,
)


class FormInstanceAdminForm(forms.ModelForm):
    email_addresses = forms.ModelMultipleChoiceField(
        queryset=EmailAddress.objects.order_by(
            'email',
        ),
        label='Email addresses',
        required=False,
        widget=admin.widgets.FilteredSelectMultiple(
            'email addresses',
            False,
        )
    )

    class Meta:
        model = FormInstance
        exclude = [
        ]


class FormInstanceAdmin(CloneableAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly_fields = [
            'form_link',
            'def_link',
            'cat_link',
        ] + self.readonly_fields
        self.top_fieldsets = [
            (
                None, {
                    'fields': [
                        'title',
                        'alt_title',
                        'form_definition',
                        'published',
                        'descriptive_text',
                        'footer_text',
                        'email_addresses',
                    ],
                }
            ),
        ]
        self.bottom_fieldsets[0][1]['fields'] = self.bottom_fieldsets[0][1]['fields'] + [
            'form_link',
            'def_link',
            'cat_link',
        ]
        self.fieldsets = self.top_fieldsets + self.bottom_fieldsets
        self.list_display = [
            'title',
            'published',
            'form_link',
        ] + self.list_display
        self.view_name = 'clone_form_instance'

    def get_form(self, request, obj=None, **kwargs):
        if obj and not self.has_change_permission(request, obj):
            return super().get_form(request, obj, **kwargs)
        return FormInstanceAdminForm

    search_fields = [
        'title',
    ]

    def form_link(self, obj):
        if obj.published:
            link_str = f'<a href="{obj.form_url()}" target="_blank">Form page</a>'
        else:
            link_str = 'Unpublished'
        return mark_safe(link_str)

    form_link.short_description = 'page'

    def def_link(self, obj):
        if obj.pk:
            url_str = reverse(
                f'admin:{obj.form_definition._meta.app_label}_{obj.form_definition._meta.model_name}_change',
                args=(obj.form_definition.pk,),
            )
            link_str = f'<a href="{url_str}">{obj.form_definition.definition_name}</a>'
        else:
            link_str = 'Click "save and continue editing" to get a link.'
        return mark_safe(link_str)

    def_link.short_description = 'form definition'

    def cat_link(self, obj):
        link_str = 'Click "save and continue editing" to get a link.'
        if obj.pk:
            try:
                url_str = reverse(
                    f'admin:{obj.post_category._meta.app_label}_{obj.post_category._meta.model_name}_change',
                    args=(obj.post_category.pk,),
                )
                link_str = f'<a href="{url_str}">Form responses</a>'
            except ObjectDoesNotExist:
                pass
        return mark_safe(link_str)

    cat_link.short_description = 'responses'


admin.site.register(
    FormInstance,
    FormInstanceAdmin,
)


class PostCategoryAdmin(BaseAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = None
        self.obj = None
        self.obj_app_label = None
        self.obj_model_name = None
        self.obj_pk = None
        self.obj_form_instance = None
        self.readonly_fields = [
           'add_response',
           'spreadsheet_export',
           'responses',
           'inst_link',
           'inst_count',
        ] + self.readonly_fields
        self.top_fieldsets = [
            (
                None, {
                    'fields': [
                        'inst_link',
                        'add_response',
                        'inst_count',
                        'spreadsheet_export',
                        'responses',
                    ],
                }
            ),
        ]
        self.fieldsets = self.top_fieldsets + self.bottom_fieldsets

    search_fields = [
        'category',
    ]
    list_display = [
        'form_title',
        'inst_count',
        'form_instance_exists',
    ]
    ordering = [
        'category',
    ]

    def form_instance_exists(self, obj):
        if obj.form_instance:
            image_url = 'admin/img/icon-yes.svg'
            alt = 'True'
        else:
            image_url = 'admin/img/icon-no.svg'
            alt = 'False'
        image_str = f'<img src="{staticfiles_storage.url(image_url)}" alt="{alt}">'
        return mark_safe(image_str)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, **kwargs):
        self.request = request
        self.obj = obj
        return super().get_form(request, obj, **kwargs)

    def form_title(self, obj):
        return obj.category

    def inst_link(self, obj):
        if obj.form_instance:
            page_url = obj.form_instance.form_url()
            admin_url = reverse(
                f'admin:{obj.form_instance._meta.app_label}_{obj.form_instance._meta.model_name}_change',
                args=(obj.form_instance.pk,),
            )
            if obj.form_instance.published:
                page_link = f'<a href="{page_url}" target="_blank">Form page</a>'
            else:
                page_link = 'Form not published'
            link_str = f'{page_link}' \
                       f'<br>' \
                       f'<br>' \
                       f'<a href="{admin_url}">Form instance admin</a>'
        else:
            link_str = 'Form instance does not exist.'
        return mark_safe(link_str)

    inst_link.short_description = 'form instance'

    def add_response(self, obj):
        url_str = reverse(
            'django_simple_forms:form_page_admin_add',
            kwargs={
                'app_label': obj._meta.app_label,
                'model_name': obj._meta.model_name,
                'pk': obj.pk,
            },
        )
        if not obj.form_instance:
            return 'Form instance does not exist.'
        if self.request.user.has_perm('django_simple_forms.add_postinstance'):
            return mark_safe(
                f'<a href="{url_str}">'
                f'<input type="button" class= "small_admin_button" value="Add response">'
                f'</a>'
            )
        else:
            return ''

    def spreadsheet_export(self, obj):
        url_str = reverse(
            'django_simple_forms:post_spreadsheet',
            kwargs={
                'app_label': obj._meta.app_label,
                'model_name': obj._meta.model_name,
                'pk': obj.pk,
            },
        )
        return mark_safe(
            f'<a href="{url_str}">'
            f'<input type="button" class= "small_admin_button" value="Download responses">'
            f'</a>'
        )

    def trim_list(self, post, name):
        try:
            trimmed_list = post.output_formatted_date_time()[name][1:]
        except (IndexError, KeyError) as error:
            trimmed_list = []
        return trimmed_list

    def responses(self, obj):
        field_names = [item for field in obj.data_json['table_fields'] for item in field]
        headers_list = ['Created:']
        if obj.data_json['table_fields']:
            headers_list += [
                value for header_dict in obj.data_json['table_fields'] for key, value in header_dict.items()
            ]
        if not obj.data_json['sort_created'] and obj.data_json['table_fields']:
            headers_list.pop(0)
        data_lists = [
            [[post.created] for x in range(len(headers_list) - len(field_names))]
            + [self.trim_list(post, name) for name in field_names]
            + [post.pk]
            for post in obj.post_instances.all()
        ]
        for index in reversed(range(len(headers_list) + 1)):
            data_lists = sorted(data_lists, key=itemgetter(index))
        if obj.data_json['sort_created'] or not obj.data_json['table_fields']:
            for unformatted_row in data_lists:
                unformatted_row[0][0] = localize(timezone.localtime(unformatted_row[0][0]))
        headers_list += [
            'Data:',
            'PDF:',
            'Clone:',
        ]
        html_str = '<div id="responses_container">' \
                   '<table id="responses_table">'
        html_str += f'<tr>'
        for header in headers_list:
            html_str += f'<th><strong>{header}</strong></th>'
        html_str += f'</tr>'
        for post_list in data_lists:
            row_list = post_list[:-1]
            post = obj.post_instances.all().filter(
                pk=post_list[-1]
            ).first()
            view_link_str = '—'
            if self.request.user.has_perm('django_simple_forms.view_postinstance'):
                url_str_view = reverse(
                    'django_simple_forms:post_view',
                    kwargs={
                        'app_label': obj._meta.app_label,
                        'model_name': obj._meta.model_name,
                        'pk': post.pk,
                    },
                )
                view_link_str = f'<a href="{url_str_view}">View</a>'
            edit_link_str = '—'
            if post.post_category.form_instance:
                if post.post_category.form_instance.form_definition.editable_data\
                        and self.request.user.has_perm('django_simple_forms.change_postinstance'):
                    url_str_edit = reverse(
                        'django_simple_forms:form_page_admin',
                        kwargs={
                            'app_label': obj._meta.app_label,
                            'model_name': obj._meta.model_name,
                            'pk': post.pk,
                        },
                    )
                    edit_link_str = f'<a href="{url_str_edit}">Edit</a>'
            data_link_str = f'{view_link_str} | {edit_link_str}'
            row_list.append([data_link_str])
            pdf_link_str = '—'
            if post.pdf and self.request.user.has_perm('django_simple_forms.view_postpdf'):
                pdf_link_str = f'<a href=" {post.pdf.proxy_url()}" target="_blank">View</a>'
            row_list.append([pdf_link_str])
            clone_button_str = '—'
            if post.post_category.form_instance:
                if post.post_category.form_instance.form_definition.editable_data\
                        and self.request.user.has_perm('django_simple_forms.add_postinstance')\
                        and self.request.user.has_perm('django_simple_forms.change_postinstance'):
                    url_str_clone = reverse(
                        'django_simple_forms:clone_post_instance',
                        kwargs={
                            'app_label': obj._meta.app_label,
                            'model_name': obj._meta.model_name,
                            'pk': post.pk,
                        },
                    )
                    clone_button_str = f'<a href="{url_str_clone}"><input type="button" class= "small_admin_button" value="Clone"></a>'
            row_list.append([clone_button_str])
            html_str += '<tr>'
            for cell_list in row_list:
                if cell_list == row_list[-1]:
                    td_class = 'post_instance no_right_border'
                else:
                    td_class = 'post_instance'
                cell_str = ''
                for data_item in cell_list:
                    if isinstance(data_item, bool):
                        image_url = 'admin/img/icon-unknown.svg'
                        alt = 'Null'
                        if data_item:
                            image_url = 'admin/img/icon-yes.svg'
                            alt = 'True'
                        if not data_item:
                            image_url = 'admin/img/icon-no.svg'
                            alt = 'False'
                        cell_str = f'<img src="{staticfiles_storage.url(image_url)}" alt="{alt}">  '
                    else:
                        cell_str += f'{str(data_item)}, '
                if cell_str:
                    cell_str = cell_str[:-2]
                html_str += f'<td class="{td_class}">{cell_str}</td>'
            html_str += '</tr>'
        col_keys = []
        if obj.data_json:
            col_keys = [key for header_dict in obj.data_json['table_fields'] for key, value in header_dict.items()]
        tally_fields = obj.data_json['tally_fields']
        tallies = []
        for field_name in col_keys:
            if field_name in tally_fields:
                total = 0
                for instance in obj.post_instances.all():
                    for item in instance.data_json['data_dicts']:
                        for key, value in item.items():
                            if key == field_name and value[1]:
                                total += 1
                tally = str(total)
            else:
                tally = ''
            tallies.append(tally)
        tallies += ['', '', '']
        tally_row = False
        tally_html = '<tr class="tally_row">'
        for tally_str in tallies:
            if tally_str:
                tally_row = True
                tally_str = f'<u>Total</u>:<br>{tally_str}'
            tally_html += f'<td class="post_instance no_right_border tally_cell">{tally_str}</td>'
        tally_html += '</tr>'
        if tally_row:
            html_str += tally_html
        html_str += '</table>' \
                    '</div>'
        return mark_safe(html_str)

    @property
    def media(self):
        css = {
            'all': (
                self.base_css,
            ),
        }
        if self.obj:
            if self.obj.form_instance:
                css = {
                    'all': (
                        self.base_css,
                        'admin/css/delete_button.css',
                    ),
                }
        return forms.Media(css=css)

    def delete_model(self, request, obj):
        self.obj_app_label = obj._meta.app_label
        self.obj_model_name = obj._meta.model_name
        self.obj_pk = obj.pk
        self.obj_form_instance = obj.form_instance
        obj.delete()

    def response_delete(self, request, obj_display, obj_id):
        if self.obj_form_instance:
            reverse_str = f'admin:{self.obj_app_label}_{self.obj_model_name}_change'
            reverse_args = [self.obj_pk]
            redirect = HttpResponseRedirect(
                reverse(
                    reverse_str,
                    args=reverse_args,
                )
            )
        else:
            reverse_str = f'admin:{self.obj_app_label}_{self.obj_model_name}_changelist'
            redirect = HttpResponseRedirect(
                reverse(
                    reverse_str,
                )
            )
        return redirect


admin.site.register(
    PostCategory,
    PostCategoryAdmin,
)
