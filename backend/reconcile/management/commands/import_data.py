from django.core.management.base import BaseCommand
from reconcile.importer import import_csv_data

class Command(BaseCommand):
    help = "Import the locations, System A and System B CSV files idempotently."
    def handle(self, *args, **options):
        result = import_csv_data()
        self.stdout.write(self.style.SUCCESS("Import complete"))
        for key, value in result.items():
            self.stdout.write(f"{key}: {value}")
