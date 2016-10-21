# -*- coding: utf-8 -*-
import random

from django.core.management.base import BaseCommand

from ui.models import *


class Command(BaseCommand):
    help = 'Deletes corpus and all annotations'

    def add_arguments(self, parser):
        parser.add_argument('corpus-name')

    def handle(self, *args, **options):
        Corpus.objects.filter(name=options['corpus-name']).delete()
        self.stdout.write(self.style.SUCCESS('Done!'))
