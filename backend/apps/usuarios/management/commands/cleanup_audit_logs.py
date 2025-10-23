from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.usuarios.models import AuditoriaLog


class Command(BaseCommand):
    help = "Elimina logs de auditoría con más de N días (default 365)."

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=365)

    def handle(self, *args, **opts):
        days = opts['days']
        limit = timezone.now() - timedelta(days=days)
        qs = AuditoriaLog.objects.filter(fecha__lt=limit)
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Eliminados {count} logs anteriores a {days} días"))

