from datetime import (
    timedelta
)


from django.conf import (
    settings,
)
from django.core.management.base import (
    BaseCommand,
)
from django.utils import (
    timezone,
)


from ...models import (
    PostCategory,
    PostInstance,
)


class Command(BaseCommand):
    help = 'Deletes form responses that have reached or passed their deletion date'

    def handle(self, *args, **options):
        try:
            days_saved = settings.FORMS_DELETE_RESPONSES
        except AttributeError:
            days_saved = 365
        today = timezone.now().date()
        expiration_date = today - timedelta(days=days_saved)
        PostInstance.objects.filter(
            created__date__lte=expiration_date,
        ).delete()
        PostCategory.objects.filter(
            form_instance=None,
        ). filter(
            post_instances=None,
        ).delete()
