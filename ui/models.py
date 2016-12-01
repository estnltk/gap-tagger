from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Corpus(models.Model):
    name = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserCorpus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    corpus = models.ForeignKey(Corpus, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'corpus')


class Sentence(models.Model):
    corpus = models.ForeignKey(Corpus, on_delete=models.CASCADE, db_index=True)
    text = models.TextField()
    variants = ArrayField(models.TextField())
    gap_start = models.PositiveSmallIntegerField()
    gap_end = models.PositiveSmallIntegerField()

    def __str__(self):
        return "{}<GAP>{}</GAP>{}".format(self.text[:self.gap_start],
                                          self.text[self.gap_start:self.gap_end],
                                          self.text[self.gap_end:])


class SentenceAnnotation(models.Model):
    annotator = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, db_index=True)
    variant = models.PositiveSmallIntegerField(help_text='Index of the variant in sentence.variants array')
    variant_selected = models.NullBooleanField(help_text='Null is annotation is not yet processed by annotator')
    both_variants_fit = models.NullBooleanField()
    time = models.IntegerField(null=True)
    order = models.IntegerField(db_index=True)
