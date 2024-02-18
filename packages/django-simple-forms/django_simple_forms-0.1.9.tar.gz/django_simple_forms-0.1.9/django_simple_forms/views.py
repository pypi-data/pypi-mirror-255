from collections import (
    OrderedDict,
)
from io import (
    BytesIO,
)
from itertools import (
    chain,
)


from django.apps import (
    apps,
)
from django.conf import (
    settings,
)
from django.contrib.sites.models import (
    Site,
)
from django.contrib.staticfiles.storage import (
    staticfiles_storage,
)
from django.core.exceptions import (
    ObjectDoesNotExist,
)
from django.core.mail import (
    EmailMultiAlternatives,
)
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import (
    render,
)
from django.template.loader import (
    get_template,
)
from django.urls import (
    reverse,
)
from django.utils import (
    timezone,
)
from django.utils.safestring import (
    mark_safe,
)
from django.utils.text import (
    slugify,
)


import xlsxwriter


from .forms import (
    GeneratedForm,
    GeneratedFormPublic,
)
from .models import (
    ChoiceDefinition,
    ErrorDefinition,
    format_data,
    FormInstance,
    FormsSiteProfile,
    InputInstance,
    PostCategory,
    PostInstance,
)


def get_object(app_label, model_name, pk):
    model_class = apps.get_model(
        app_label,
        model_name,
    )
    return model_class.objects.get(
        pk=pk,
    )


def clone_object(obj, clear_attrs=None, attr_name=None, reverse_str=None, reverse_args=None):
    if reverse_args is None:
        reverse_args = []
    obj.pk = None
    obj.id = None
    if clear_attrs:
        for attr in clear_attrs:
            setattr(obj, attr, None)
    if attr_name:
        clone_num = 1
        found_copy = True
        clone_name = ''
        while found_copy:
            clone_name = f'{getattr(obj, attr_name)} copy {str(clone_num)}'
            try:
                obj.__class__.objects.get(
                    **{attr_name: clone_name},
                )
                clone_num += 1
            except ObjectDoesNotExist:
                found_copy = False
        setattr(obj, attr_name, clone_name)
    obj.save()
    if not reverse_str:
        reverse_str = f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change'
    reverse_args += [obj.pk]
    redirect = HttpResponseRedirect(
        reverse(
            reverse_str,
            args=reverse_args,
        )
    )
    return obj, redirect


def clone_related(obj, related, attr):
    for item in related:
        item.pk = None
        item.id = None
        setattr(item, attr, obj)
        item.save()


def clone_input_definition(request, app_label, model_name, pk):
    obj = get_object(
        app_label,
        model_name,
        pk,
    )
    error_defs = ErrorDefinition.objects.filter(
        input_definition=obj,
    )
    choice_defs = ChoiceDefinition.objects.filter(
        input_definition=obj,
    )
    related = chain(
        error_defs,
        choice_defs,
    )
    clone = clone_object(
        obj,
        attr_name='definition_name',
    )
    clone_related(
        clone[0],
        related,
        'input_definition',
    )
    return clone[1]


def clone_email_address(request, app_label, model_name, pk):
    obj = get_object(
        app_label,
        model_name,
        pk,
    )
    form_instances = obj.form_instances.all()
    clone = clone_object(
        obj,
        attr_name='recipient_name',
    )
    clone[0].email = 'example@example.com'
    clone[0].save()
    for item in form_instances:
        item.email_addresses.add(clone[0])
    return clone[1]


def clone_form_definition(request, app_label, model_name, pk):
    obj = get_object(
        app_label,
        model_name,
        pk,
    )
    related = InputInstance.objects.filter(
        form_definition=obj,
    )
    clone = clone_object(
        obj,
        attr_name='definition_name',
    )
    clone_related(
        clone[0],
        related,
        'form_definition',
    )
    return clone[1]


def clone_form_instance(request, app_label, model_name, pk):
    obj = get_object(
        app_label,
        model_name,
        pk,
    )
    email_addresses = obj.email_addresses.all()
    clone = clone_object(
        obj,
        attr_name='title',
    )
    clone[0].published = False
    clone[0].save()
    for item in email_addresses:
        clone[0].email_addresses.add(item)
    return clone[1]


def clone_post_instance(request, app_label, model_name, pk):
    obj = get_object(
        'django_simple_forms',
        'postinstance',
        pk,
    )
    clone = clone_object(
        obj,
        clear_attrs=[
            'pdf',
        ],
        reverse_str='django_simple_forms:form_page_admin',
        reverse_args=[
            app_label,
            model_name,
        ],
    )
    return clone[1]


def form_page(request, pk, title_slug):
    try:
        form_instance = FormInstance.objects.get(pk=pk)
        if not form_instance.published:
            raise Http404()
    except (ValueError, ObjectDoesNotExist) as error:
        raise Http404()
    ''' Begin getting time elements '''
    form_submit_time = timezone.now().timestamp()
    if 'form_load_time' in request.session:
        form_load_time = request.session['form_load_time']
        del request.session['form_load_time']
    else:
        form_load_time = form_submit_time
    ''' End getting time elements '''
    form_definition = form_instance.form_definition
    page_template = form_definition.form_html
    success_template = form_definition.success_html
    dict_data = form_instance.dict_data()
    for field in dict_data['field_dicts']:
        if field['admin_only']:
            field['widget_data']['widget_type'] = 'HiddenInput'
            field['field_data']['field_args']['required'] = False
    form = GeneratedFormPublic(
        dict_data=dict_data,
    )
    if request.method == 'POST':
        form = GeneratedFormPublic(
            request.POST,
            dict_data=dict_data,
        )
        if form.is_valid():
            cleaned_data = form.cleaned_data
            context = {
                'title': form_instance.title,
                'css_style': staticfiles_storage.url(form_definition.form_css),
            }
            ''' Begin checking how quickly form was submitted '''
            if form_submit_time - form_load_time > 1:
                ''' End checking how quickly form was submitted '''
                ''' Begin checking for input in hidden field '''
                if not cleaned_data['email']:
                    ''' End checking for input in hidden field '''
                    ''' Note: Optional reCAPTCHA is verified in the page'''
                    ''' Begin removing security data '''
                    cleaned_data.pop('email')
                    try:
                        cleaned_data.pop('captcha')
                    except KeyError:
                        pass
                    ''' End removing security data '''
                    post_instance = PostInstance.objects.create_instance(
                        form_instance=form_instance,
                        cleaned_data=cleaned_data,
                    )
                    if form_definition.send_email:
                        try:
                            from_address = settings.FORMS_FROM_ADDRESS
                        except AttributeError:
                            from_address = settings.DEFAULT_FROM_EMAIL
                        input_instances = form_definition.input_instances
                        first_instance = input_instances.all().filter(
                            field_name=form_definition.reply_first,
                        ).first()
                        last_instance = input_instances.all().filter(
                            field_name=form_definition.reply_last,
                        ).first()
                        address_instance = input_instances.all().filter(
                            field_name=form_definition.reply_address,
                        ).first()
                        if address_instance and address_instance.input_definition.field_type == 'EmailField':
                            reply_address = cleaned_data[address_instance.field_name]
                            reply_to = reply_address
                            if first_instance and first_instance.input_definition.field_type == 'CharField':
                                reply_first = cleaned_data[first_instance.field_name]
                                reply_to = f'"{reply_first}" <{reply_address}>'
                                if last_instance and last_instance.input_definition.field_type == 'CharField':
                                    reply_last = cleaned_data[last_instance.field_name]
                                    reply_to = f'"{reply_first} {reply_last}" <{reply_address}>'
                        else:
                            try:
                                reply_to = settings.FORMS_REPLY_ADDRESS
                            except AttributeError:
                                reply_to = from_address
                        subject_instance = input_instances.all().filter(
                            field_name=form_definition.email_subject,
                        ).first()
                        prefix_str = post_instance.post_category.form_instance.form_definition.subject_prefix
                        if subject_instance and subject_instance.input_definition.field_type == 'CharField':
                            field_str = cleaned_data[subject_instance.field_name]
                        else:
                            field_str = ''
                        if prefix_str and field_str:
                            space_str = ' '
                        else:
                            space_str = ''
                        subject_str = f'{prefix_str}{space_str}{field_str}'
                        text_template = form_definition.email_txt
                        html_template = form_definition.email_html
                        subject = subject_str
                        site_domain = Site.objects.get_current().domain
                        site_profile = FormsSiteProfile.objects.filter(
                            domain=site_domain,
                        ).first()
                        if post_instance.pdf:
                            pdf_url = f'{site_profile.protocol_domain()}{post_instance.pdf.proxy_url()}'
                        else:
                            pdf_url = ''
                        email_content = {
                            'subject': subject,
                            'form_name': form_instance.title,
                            'output_dict': post_instance.output_dict(),
                            'output_no_br': post_instance.output_no_br(),
                            'output_formatted_date_time': post_instance.output_formatted_date_time(),
                            'output_text': post_instance.output_text(),
                            'pdf_url': pdf_url,
                        }
                        email_txt = get_template(text_template).render(email_content)
                        email_html = get_template(html_template).render(email_content)
                        recipients = [
                            f'"{address.recipient_name}" <{address.email}>'
                            for address in form_instance.email_addresses.all()
                        ]
                        message = EmailMultiAlternatives(
                            subject,
                            email_txt,
                            from_address,
                            recipients,
                            reply_to=[reply_to],
                        )
                        message.attach_alternative(email_html, 'text/html')
                        message.send(fail_silently=False)
            return render(
                request,
                success_template,
                context,
            )
    ''' Begin setting when form was loaded '''
    request.session['form_load_time'] = timezone.now().timestamp()
    ''' End setting when form was loaded '''
    context = {
        'title': form_instance.title,
        'descriptive_text': mark_safe(form_instance.descriptive_text),
        'footer_text': mark_safe(form_instance.footer_text),
        'button_label': form_instance.form_definition.button_label,
        'css_style': staticfiles_storage.url(form_instance.form_definition.form_css),
        'form': form,
    }
    return render(
        request,
        page_template,
        context,
    )


def form_page_admin(request, app_label, model_name, pk, add_instance=False):
    post_instance = PostInstance.objects.none()
    if add_instance:
        if not request.user.has_perm('django_simple_forms.add_postinstance'):
            raise Http404()
        try:
            post_category = PostCategory.objects.get(pk=pk)
        except (ValueError, ObjectDoesNotExist) as error:
            raise Http404()
        form_instance = post_category.form_instance
        if not form_instance:
            raise Http404()
        title = f'Add response: {form_instance.title}'
        dict_data = form_instance.dict_data()
    else:
        post_instance = PostInstance.objects.get(pk=pk)
        post_category = post_instance.post_category
        form_instance = post_category.form_instance
        if not form_instance:
            raise Http404()
        if not form_instance.form_definition.editable_data\
                or not request.user.has_perm('django_simple_forms.change_postinstance'):
            raise Http404()
        title = f'Edit response: {form_instance.title}'
        dict_data = form_instance.dict_data()
        for key, value in post_instance.output_no_br().items():
            for field in dict_data['field_dicts']:
                if field['field_data']['field_name'] == key:
                    try:
                        if field['field_data']['field_type'] == 'MultipleChoiceField':
                            field['field_data']['field_args']['initial'] = value[1:]
                        else:
                            field['field_data']['field_args']['initial'] = value[1]
                        if field['field_data']['field_type'] == 'TypedChoiceField':
                            if field['field_data']['field_args']['initial']:
                                field['field_data']['field_args']['initial'] = 'true'
                            else:
                                field['field_data']['field_args']['initial'] = 'false'
                    except IndexError:
                        pass
    page_template = form_instance.form_definition.post_form_html
    reverse_str = f'admin:{app_label}_{model_name}_change'
    form = GeneratedForm(
        dict_data=dict_data,
    )
    if request.method == 'POST':
        form = GeneratedForm(
            request.POST,
            dict_data=dict_data,
        )
        category_return = HttpResponseRedirect(
            reverse(
                reverse_str,
                args=(post_category.pk,),
            )
        )
        if 'cancel' in request.POST:
            return category_return
        if form.is_valid():
            cleaned_data = form.cleaned_data
            if add_instance:
                PostInstance.objects.create_instance(
                    form_instance=form_instance,
                    cleaned_data=cleaned_data,
                )
            else:
                stored_dict = format_data(
                    form_instance=form_instance,
                    cleaned_data=cleaned_data,
                )
                if post_instance:
                    post_instance.data_json = stored_dict
                    post_instance.save()
            return category_return
    context = {
        'title': title,
        'form': form,
    }
    return render(
        request,
        page_template,
        context,
    )


def form_page_admin_add(request, app_label, model_name, pk):
    return form_page_admin(
        request,
        app_label,
        model_name,
        pk,
        add_instance=True,
    )


def post_view(request, app_label, model_name, pk):
    try:
        post_instance = PostInstance.objects.get(pk=pk)
    except (ValueError, ObjectDoesNotExist) as error:
        raise Http404()
    if not request.user.has_perm('django_simple_forms.view_postinstance'):
        raise Http404()
    title = f'View response: {post_instance.post_category.category}'
    delete_post = False
    delete_perm = False
    if request.user.has_perm('django_simple_forms.delete_postinstance'):
        delete_perm = True
    if request.method == 'POST':
        reverse_str = f'admin:{app_label}_{model_name}_change'
        category_return = HttpResponseRedirect(
            reverse(
                reverse_str,
                args=(post_instance.post_category.pk,),
            )
        )
        if 'return' in request.POST:
            return category_return
        if 'delete' in request.POST:
            delete_post = True
        if 'confirm' in request.POST:
            post_instance.delete()
            return category_return
    context = {
        'title': title,
        'output_dict': post_instance.output_dict(),
        'output_formatted_date_time': post_instance.output_formatted_date_time(),
        'created': post_instance.created,
        'updated': post_instance.updated,
        'delete_perm': delete_perm,
        'delete_post': delete_post,
    }
    if post_instance.post_category.form_instance:
        page_template = post_instance.post_category.form_instance.form_definition.post_html
    else:
        page_template = 'django_simple_forms/internal/pages/post_view.html'
    return render(
        request,
        page_template,
        context,
    )


def post_spreadsheet(request, app_label, model_name, pk):
    category = get_object(
        app_label,
        model_name,
        pk,
    )
    post_instances = category.post_instances
    form_slug = slugify(category.category)
    datetime_str = str(timezone.now()).split('.')[0].replace(' ', '_').replace(':', '.')
    filename = f'{form_slug}_{datetime_str}.xlsx'
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    format_title = workbook.add_format(
        {
            'bold': True,
            'font_size': 16,
        }
    )
    format_header = workbook.add_format(
        {
            'bold': True,
            'font_size': 12,
        }
    )
    format_header.set_bottom(1)
    format_header.set_text_wrap()
    format_cell_data = workbook.add_format(
        {
            'align': 'top',
            'font_size': 12,
        }
    )
    format_cell_data.set_text_wrap()
    format_tallies = workbook.add_format(
        {
            'bold': True,
            'font_size': 12,
        }
    )
    format_tallies.set_top(1)
    format_tallies.set_text_wrap()
    worksheet = workbook.add_worksheet()
    worksheet.write(0, 0, category.category, format_title)
    col_dict = OrderedDict()
    for post in post_instances.all():
        for key, value in post.output_no_br().items():
            if key not in col_dict:
                col_dict[key] = value[0]
    col_keys = []
    header_row = 2
    header_col = 0
    for key, value in col_dict.items():
        col_keys.append(key)
        worksheet.write(header_row, header_col, value, format_header)
        header_col += 1
    last_col = len(col_dict) - 1
    worksheet.set_column(0, last_col, 20)
    data_row = 3
    for post in post_instances.all():                           # Doing this iteration a second time
        for key, value in post.output_no_br().items():
            data_col = col_keys.index(key)
            if len(value) > 2:
                value_list = value[1:]
                cell_data = ''
                for item in value_list:
                    cell_data += f'{str(item)},\r\n'
                cell_data = cell_data[:-3]
            else:
                try:
                    if value[1] is True:
                        cell_data = '✓'
                    elif value[1] is False:
                        cell_data = '✕'
                    else:
                        cell_data = value[1]
                except IndexError:
                    cell_data = ''
            worksheet.write(data_row, data_col, cell_data, format_cell_data)
        data_row += 1
    tallies = ['' for key in col_keys]
    for field_name in category.data_json['tally_fields']:
        total = 0
        for instance in category.post_instances.all():
            for item in instance.data_json['data_dicts']:
                for key, value in item.items():
                    if key == field_name and value[1]:
                        total += 1
        tally_str = f'Total:\r\n{str(total)}'
        tallies[col_keys.index(field_name)] = str(tally_str)
    for index in range(len(tallies)):
        worksheet.write(data_row, index, tallies[index], format_tallies)
    workbook.close()
    response = HttpResponse(
        content_type='application/vnd.ms-excel',
    )
    response['Content-Disposition'] = f'attachment;filename="{filename}"'
    response.write(output.getvalue())
    return response
