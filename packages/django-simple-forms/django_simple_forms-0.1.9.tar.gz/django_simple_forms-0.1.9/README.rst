===================
django-simple-forms
===================

The django-simple-forms Django app is in an early stage of development and looking for contributors. Priorities are completing tests and documentation. Use at your own risk.

This app is used to build and manage Django forms in the admin without having to write code. Form responses can be viewed or edited in the admin, and reponses can be emailed to any number of recipients our output as PDFs with custom templates. Responses can be downloaded as an Excel spreadsheet.

-----------
Quick start
-----------

1. Run ``pip install django-simple-forms``.

2. Add django-simple-forms and its dependencies to your installed apps: ::

    INSTALLED_APPS = (
        ...
        'django.contrib.sites',

        'adminsortable2',
        'ckeditor',
        'django_simple_file_handler',
        'django_simple_forms',
    )

3. Run ``python manage.py migrate``.

4. Include the django-simple-forms URLconf and the django-simple-file-handler URLconf in your website's ``urls.py``: ::

    urlpatterns = [
        ...
        path(
            'forms/',
            include('django_simple_forms.urls')
        ),
        path(
            'pdf/',
            include('django_simple_file_handler.urls'),
        ),
    ]

5. If you are already using the Django sites framework, run ``python manage.py forms_import_sites``.
You will then need to go to FORMS > Site profiles in your admin site and check to be sure your details are correct.
All new site profiles will be assigned an ``https://`` protocol, so change this if necessary.

If you are not already using the Django sites framework, go to your admin site and, under FORMS > Site profiles, create a profile with your site's information.

The ``SITE_ID`` setting is needed for django-simple-forms. See the `Django sites framework documentation <https://docs.djangoproject.com/en/2.2/ref/contrib/sites/>`_ for more information.

6. Refer to the `Django email documentation <https://docs.djangoproject.com/en/2.2/topics/email/>`_ for information on configuring a website to send email.

7. If you intend to use PDF output, see the ``Generating PDFs`` section of the `django-simple-file-handler documentation <https://github.com/jonathanrickard/django-simple-file-handler>`_ for additional configuration information.

-------------------
Management commands
-------------------

* ``forms_import_sites``: Creates a FormsSiteProfile instance for each instance in the Django sites framework
* ``delete_unused_addresses``: Deletes email addresses that do not have any forms assigned
* ``delete_expired_responses``: Deletes form responses that have reached or passed their deletion date

---------------------
Needing documentation
---------------------

* Optional settings
* User permissions
* Use of ``initial_boolean`` field in admin
* Use of `XlsxWriter <https://github.com/jmcnamara/XlsxWriter/>`_ in spreadsheet generation
* Explanation of admin customization options for response categories
* Explanation of how to specify custom HTML and CSS files for most internal and external pages through the form definition admin
* Explanation that ``email`` can not be used as a field name because it is already used as a hidden honeypot field
* Explanation that default error messages are built in, and any entered in the admin are just for customization
* Explanation that deleting a form instance will not delete its response category
* Explanation that clicking the "Delete" button in the admin for a form's responses will only delete the category if the form instance does not exist anymore — otherwise, it will just delete all of the associated responses and leave the category
* Explanation that reply-to email address's last name field is not checked if there is not a reply-to first name given
* Explanation that "true" and "false" strings are available for use in a Select widget to set a BooleanField using a hidden TypedChoiceField.
* Explanation that DateField and TimeField are rudimentary with just text inputs; in practice, they would usually be replaced using JavaScript widgets; input formats is not yet supported, but can be set universally in settings per Django documentation
* Explanation of formatting for date and time stored as strings
* Explanation of how ``app_label`` and ``model_name`` are used for ease of subclassing and to change ``get_queryset``
* Explanation of what values are available in email templates and how to access those values
* Explanation that template field data lists have a string of ``label`` + ``suffix`` as the first item that can be accessed as ``data.0`` in a template
* Explanation that, by default, ``output_formatted_date_time`` and ``output_text`` are used in the default templates, but ``output_dict`` and ``output_no_br`` are also available in most cases
* Explanation that ``created`` and ``updated`` model instance data is also available in HTML and PDF templates
* Explanation of the ``checkbox_select_multiple`` class being automatically added to the CheckboxSelectMultiple <ul> tag to make styling easier
