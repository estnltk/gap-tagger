from django.contrib import admin

# Register your models here.
from ui.models import *


class SentenceAnnotationAdmin(admin.ModelAdmin):
    list_display = ('variant_txt', 'variant', 'variant_selected', 'both_variants_fit', 'time', 'annotator', 'sentence')
    list_filter = ('annotator', 'sentence__corpus', 'variant_selected', 'both_variants_fit')

    def variant_txt(self, obj):
        return obj.sentence.variants[obj.variant]


class SentenceAdmin(admin.ModelAdmin):
    list_display = ('sentence_as_text', 'variants',)
    list_filter = ('corpus', )

    def sentence_as_text(self, obj):
        return str(obj)


class CorpusAdmin(admin.ModelAdmin):
    list_display = ('name', 'timestamp')


class UserCorpusAdmin(admin.ModelAdmin):
    list_display = ('user', 'corpus')


admin.site.register(Corpus, CorpusAdmin)
admin.site.register(UserCorpus, UserCorpusAdmin)
admin.site.register(SentenceAnnotation, SentenceAnnotationAdmin)
admin.site.register(Sentence, SentenceAdmin)
