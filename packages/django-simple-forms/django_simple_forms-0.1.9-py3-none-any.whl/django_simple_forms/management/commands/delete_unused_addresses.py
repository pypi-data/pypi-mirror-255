from django.core.management.base import (
    BaseCommand,
)


from ...models import (
    EmailAddress,
)


class Command(BaseCommand):
    help = 'Deletes email addresses that do not have any forms assigned'

    def handle(self, *args, **options):
        EmailAddress.objects.filter(
            form_instances=None,
        ).delete()
