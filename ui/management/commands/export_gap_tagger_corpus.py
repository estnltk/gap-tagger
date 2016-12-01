# -*- coding: utf-8 -*-
import random

from django.core.management.base import BaseCommand
from django.db import transaction
import pandas as pd

from ui.models import *


class Command(BaseCommand):
    help = 'Exports Gap-tagger-corpus.' \
           'Usage:' \
           'python export_gap_tagger_corpus.py <output-file-name>'

    def add_arguments(self, parser):
        parser.add_argument('out-file')

    @transaction.atomic
    def handle(self, *args, **options):
        out_file = options['out-file']
        columns = 'sentence,gap_start,gap_end,gap_word,variant,correct_selected,both_selected,annotator,time'
        rows = []
        for sa in SentenceAnnotation.filter(variant_selecte__isnull=False).select_related('sentence'):
            row = [
                sa.sentence.text,
                sa.sentence.gap_start,
                sa.sentence.gap_end,
                sa.sentence.text[sa.sentence.gap_start:sa.sentence.gap_end],
                sa.sentence.variants[sa.variant],
                int(not sa.varian_selected),
                int(sa.both_variants_fit),
                sa.annotator.id,
                sa.time
            ]
            rows.append(row)

        df = pd.DataFrame(rows)
        df.sort('gap_word')
        df.to_csv(out_file, index=None)
