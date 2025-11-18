from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import csv
from apps.usuarios.models import AuditoriaLog


class Command(BaseCommand):
    help = "Respalda logs de auditoría antiguos en CSV (no se eliminan)."

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=365)
        parser.add_argument('--output', type=str, default='auditorias_backup.csv')

    def handle(self, *args, **opts):
        days = opts['days']
        limit = timezone.now() - timedelta(days=days)
        qs = AuditoriaLog.objects.filter(fecha__lt=limit)
        count = qs.count()
        if not count:
            self.stdout.write("No hay auditorías para respaldar.")
            return
        with open(opts['output'], 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['fecha','usuario','accion','modelo','objeto_id','ruta','ip','detalle'])
            for a in qs.iterator():
                writer.writerow([a.fecha, getattr(a.usuario,'username',None), a.accion, a.modelo, a.objeto_id, a.ruta, a.ip, a.detalle])
        self.stdout.write(self.style.SUCCESS(f"Respaldo generado ({count} registros) en {opts['output']}"))
