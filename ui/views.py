import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, render_to_response
from django.db.models import F
from django.template import RequestContext

from ui.models import Corpus, Sentence, SentenceAnnotation, UserCorpus

SENTENCE_BATCH_SIZE = 5


@login_required
def corpus_list_view(request):
    corpus_list = []
    for user_corpus in UserCorpus.objects.filter(user=request.user).select_related('corpus'):
        corpus = user_corpus.corpus
        corpus_list.append(corpus)
        corpus.sentence_count = SentenceAnnotation.objects.filter(annotator=request.user,
                                                                  sentence__corpus=corpus).count()
        corpus.unprocessed_sentence_count = SentenceAnnotation.objects.filter(annotator=request.user,
                                                                              sentence__corpus=corpus,
                                                                              variant_selected__isnull=True).count()
    return render_to_response('corpus.html', RequestContext(request, {'corpus_list': corpus_list, 'page': 'corpus'}))


@login_required
def load_sentences_view(request):
    """
    Sample response:
    [{
            "id": 1,
            "sentence": "Tallinn on Eesti pealinn .",
            "gap_start": 17,
            "gap_end": 25,
            "gap_correct":  "Eesti",
            "gap_variant":  "Rootsi",
    },
    ...
    ]
    """
    corpus_id = request.POST['corpus_id']
    annotations = SentenceAnnotation.objects \
                      .filter(sentence__corpus_id=corpus_id) \
                      .filter(variant_selected__isnull=True) \
                      .filter(annotator=request.user) \
                      .select_related('sentence') \
                      .order_by('order')[:SENTENCE_BATCH_SIZE]
    for a in annotations:
        a.gap_correct = a.sentence.text[a.sentence.gap_start:a.sentence.gap_end]
        a.gap_variant = a.sentence.variants[a.variant]
    return render(request, 'annotations.html', {'annotations': annotations},
                  content_type='application/json; charset=utf-8')


@login_required
def submit_sentences_view(request):
    """
    Request should contain sentence annotations in json format:
    [
        {
            "id": 1,
            "correct_variant_selected": true,
            "time": 10,
            "corpus_id": 35
        },
        ...
    ]

    Response contains the next portion of sentences to process.
    """
    sentences = json.loads(request.body.decode('utf-8'))
    for snt in sentences:
        sa = SentenceAnnotation(id=snt['id'],
                                variant_selected=not snt['correct_variant_selected'],
                                time=snt['time'])
        sa.save(force_update=True, update_fields=['variant_selected', 'time'])

    request.POST = request.POST.copy()
    request.POST['corpus_id'] = int(sentences[0]["corpus_id"])
    return load_sentences_view(request)
