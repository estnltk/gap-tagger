# -*- coding: utf-8 -*-
import random

from django.core.management.base import BaseCommand
from django.db import transaction

from ui.models import *


class Command(BaseCommand):
    help = 'Assigns a corpus to a user'

    def add_arguments(self, parser):
        parser.add_argument('user-name')
        parser.add_argument('corpus-name')

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(24890932579)
        order = list(range(1000000))
        random.shuffle(order)

        user = User.objects.get(username=options['user-name'])
        corpus = Corpus.objects.get(name=options['corpus-name'])
        UserCorpus.objects.create(user=user, corpus=corpus)

        for snt in Sentence.objects.filter(corpus=corpus):
            for i in range(len(snt.variants)):
                SentenceAnnotation.objects.create(annotator=user, sentence=snt, variant=i, order=order.pop())
        self.stdout.write(self.style.SUCCESS('Done!'))
