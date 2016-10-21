# -*- coding: utf-8 -*-
import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from ui.models import *


class Command(BaseCommand):
    help = 'Loads corpus from csv file'

    def add_arguments(self, parser):
        parser.add_argument('corpus-name')
        parser.add_argument('corpus-file')

    @transaction.atomic
    def handle(self, *args, **options):
        corpus_name = options['corpus-name']
        corpus_file = options['corpus-file']

        corpus = Corpus.objects.create(name=corpus_name)

        with open(corpus_file, encoding='utf-8') as inf:
            reader = csv.DictReader(inf)
            for i, row in enumerate(reader):
                Sentence.objects.create(corpus=corpus,
                                        text=row["sentence"],
                                        gap_start=row["gap_start"],
                                        gap_end=row["gap_end"],
                                        variants=row["variants"].split(','))
                if i % 1000 == 0:
                    self.stdout.write('{} rows imported'.format(i))

            self.stdout.write('{} rows imported'.format(i))

        self.stdout.write(self.style.SUCCESS('Done!'))
