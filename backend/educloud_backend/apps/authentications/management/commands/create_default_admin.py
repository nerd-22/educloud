from django.core.management.base import BaseCommand
from apps.authentications.models import SuperAdmin

class Command(BaseCommand):
    help = 'Creates a default super admin user'

    def handle(self, *args, **kwargs):
        if not SuperAdmin.objects.filter(email='admin@educloud.com').exists():
            user = SuperAdmin.objects.create_superuser(
                username='admin',
                email='admin@educloud.com',
                password='admin123',
                is_super_admin=True
            )
            self.stdout.write(self.style.SUCCESS('Successfully created default super admin user'))
