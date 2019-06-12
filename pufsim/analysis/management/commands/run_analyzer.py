from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import os

from pufsim.analysis import models

class Command(BaseCommand):
    help = 'Runs the specified analyzer'

    def add_arguments(self, parser):
        parser.add_argument('analyzer_type', nargs=1, type=str)
        parser.add_argument('analyzer_id', nargs=1, type=int)

    def handle(self, *args, **options):
        print("starting handler")
        obj_type = getattr(models, options['analyzer_type'][0], None)
        obj = obj_type.objects.get(pk=options['analyzer_id'][0])
        obj.pid = os.getpid()
        obj.save()
        if not obj_type:
            print("PUFSIM :: (run_analyzer) obj_type not found")
            return
        obj = obj_type.objects.get(pk=options['analyzer_id'][0])
        if not obj:
            print("PUFSIM :: (run_analyzer) obj_type not found")
            return
        obj.run()
        obj = obj_type.objects.get(pk=options['analyzer_id'][0])
        obj.pid = 0
        obj.save()
