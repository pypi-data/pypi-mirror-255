from django.conf import (
    settings,
)
from django.forms import (
    BooleanField,
    CharField,
    CheckboxInput,
    CheckboxSelectMultiple,
    ChoiceField,
    DateField,
    DateInput,
    EmailField,
    EmailInput,
    Form,
    HiddenInput,
    MultipleChoiceField,
    Select,
    SelectMultiple,
    Textarea,
    TextInput,
    TimeField,
    TimeInput,
    TypedChoiceField,
)


def get_recaptcha_widget():
    from captcha.widgets import (
        ReCaptchaV2Checkbox,
        ReCaptchaV2Invisible,
        ReCaptchaV3,
    )
    try:
        captcha_attrs = settings.FORMS_RECAPTCHA_ATTRS
    except AttributeError:
        captcha_attrs = {}
    try:
        captcha_params = settings.FORMS_RECAPTCHA_PARAMS
    except AttributeError:
        captcha_params = {}
    widget_dict = {
        1: ReCaptchaV2Checkbox(
            attrs=captcha_attrs,
            api_params=captcha_params,
        ),
        2: ReCaptchaV2Invisible(
            attrs=captcha_attrs,
            api_params=captcha_params,
        ),
        3: ReCaptchaV3(
            attrs=captcha_attrs,
            api_params=captcha_params,
        ),
    }
    try:
        widget_type = settings.FORMS_RECAPTCHA_TYPE
    except AttributeError:
        widget_type = 1
    return widget_dict[widget_type]


class GeneratedForm(Form):
    def __init__(self, *args, **kwargs):
        dict_data = kwargs.pop('dict_data')
        super().__init__(*args, **kwargs)
        field_dicts = dict_data['field_dicts']
        for item in field_dicts:
            field_data = item['field_data']
            added_field = eval(field_data['field_type'])()
            widget_data = item['widget_data']
            added_widget = eval(widget_data['widget_type'])()
            if widget_data['widget_attrs']:
                added_widget.attrs = widget_data['widget_attrs']
            added_field.widget = added_widget
            try:
                choice_dicts = field_data['field_args'].pop('choice_dicts')
                choice_tuples = []
                for choice in choice_dicts:
                    for key, value in choice.items():
                        choice_tuples.append((key, value))
                field_data['field_args']['choices'] = choice_tuples
            except KeyError:
                pass
            try:
                boolean_dicts = field_data['field_args'].pop('boolean_dicts')
                boolean_tuples = []
                for boolean in boolean_dicts:
                    for key, value in boolean.items():
                        boolean_tuples.append((key, value))
                field_data['field_args']['choices'] = boolean_tuples
                field_data['field_args']['coerce'] = lambda x: x == 'true'
            except KeyError:
                pass
            for key, value in field_data['field_args'].items():
                setattr(added_field, key, value)
            self.fields[field_data['field_name']] = added_field


class GeneratedFormPublic(GeneratedForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ''' Begin hidden field '''
        self.fields['email'] = EmailField(
            label='',
            required=False,
        )
        ''' End hidden field '''
        if hasattr(settings, 'RECAPTCHA_PUBLIC_KEY') and hasattr(settings, 'RECAPTCHA_PRIVATE_KEY'):
            try:
                from captcha.fields import (
                    ReCaptchaField,
                )
                self.fields['captcha'] = ReCaptchaField(
                    label='',
                    widget=get_recaptcha_widget(),
                )
            except ImportError:
                pass
