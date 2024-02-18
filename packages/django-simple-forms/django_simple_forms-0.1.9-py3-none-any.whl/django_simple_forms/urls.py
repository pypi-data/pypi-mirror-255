from django.urls import (
    path,
)


from .views import (
    clone_email_address,
    clone_form_definition,
    clone_form_instance,
    clone_input_definition,
    clone_post_instance,
    form_page,
    form_page_admin,
    form_page_admin_add,
    post_view,
    post_spreadsheet,
)


app_name = 'django_simple_forms'


urlpatterns = [
    path(
        '<pk>/<title_slug>.html',
        form_page,
        name='form_page',
    ),
    path(
        'clone-email-address/<app_label>/<model_name>/<pk>/',
        clone_email_address,
        name='clone_email_address',
    ),
    path(
        'clone-form-definition/<app_label>/<model_name>/<pk>/',
        clone_form_definition,
        name='clone_form_definition',
    ),
    path(
        'clone-form-instance/<app_label>/<model_name>/<pk>/',
        clone_form_instance,
        name='clone_form_instance',
    ),
    path(
        'clone-input-definition/<app_label>/<model_name>/<pk>/',
        clone_input_definition,
        name='clone_input_definition',
    ),
    path(
        'clone-post-instance/<app_label>/<model_name>/<pk>/',
        clone_post_instance,
        name='clone_post_instance',
    ),
    path(
        'post-add/<app_label>/<model_name>/<pk>/add/',
        form_page_admin_add,
        name='form_page_admin_add',
    ),
    path(
        'post-edit/<app_label>/<model_name>/<pk>/edit/',
        form_page_admin,
        name='form_page_admin',
    ),
    path(
        'post-view/<app_label>/<model_name>/<pk>/view/',
        post_view,
        name='post_view',
    ),
    path(
        'post-spreadsheet/<app_label>/<model_name>/<pk>/',
        post_spreadsheet,
        name='post_spreadsheet',
    ),
]
