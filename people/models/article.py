from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

import multilingual
from people.models import Person

ARTICLE_TYPES = (
    ('BOOK', _('Book')),
    ('ARTICLE', _('Article')),
    ('TALK', _('Talk')),
    ('POSTER', _('Poster')),
)

page_validator = RegexValidator(r'^[A-Z]?[0-9]+$') # numbers or form 'A1857'


class Article(models.Model):

    ### ARTICLE INFO
    type = models.CharField(max_length=10, choices=ARTICLE_TYPES)
    # DOI for ARTICLE (required); ISBN for BOOK (required)
    identification = models.CharField(max_length=100, blank=True, null=True, unique=True)
    year = models.SmallIntegerField(validators=[MinValueValidator(1990)])
    title = models.CharField(max_length=200)

    ### PUBLICATION INFO
    # journal for ARTICLE (required)
    # book title for BOOK (required)
    # abstract collection for TALK, POSTER (not required)
    publication = models.CharField(max_length=100, blank=True, null=True)
    # only ARTICLE
    volume = models.CharField(max_length=10, blank=True, null=True) #TODO: integer?
    # required for BOOK, ARTICLE
    page_from = models.CharField(max_length=10, blank=True, null=True, validators=[page_validator])
    page_to = models.CharField(max_length=10, blank=True, null=True, validators=[page_validator])
    # editors for TALK, POSTER (not required)
    # publishers for BOOK (required)
    editors = models.CharField(max_length=200, blank=True, null=True)
    # only BOOK, TALK, POSTER
    place = models.CharField(max_length=200, blank=True, null=True)

    ### PRESENTATION INFO
    # only TALK, in minutes
    length = models.SmallIntegerField(blank=True, null=True)
    # only TALK, POSTER
    presenter = models.ForeignKey(Person, blank=True, null=True)

    class Meta:
        app_label = 'people'
        unique_together = (
            ('year', 'publication', 'volume', 'page_from', 'page_to'),
        )

    def __unicode__(self):
        return self.title

    def clean(self):
        if self.type == 'BOOK':
            if not self.identification:
                raise ValidationError(_('Book has to have ISBN number.'))
            if not self.publication:
                raise ValidationError(_('Book has to have book title.'))
            if self.volume:
                raise ValidationError(_('Book can not have volume.'))
            if not self.page_from:
                raise ValidationError(_('Book has to have page(s).'))
            if not self.editors:
                raise ValidationError(_('Book has to have publishers.'))
            if self.length:
                raise ValidationError(_('Book can not have length.'))
            if self.presenter:
                raise ValidationError(_('Book can not have presenter.'))
        elif self.type == 'ARTICLE':
            if not self.identification:
                raise ValidationError(_('Article has to have DOI number.'))
            if not self.publication:
                raise ValidationError(_('Article has to have journal.'))
            if not self.volume:
                raise ValidationError(_('Article has to have volume.'))
            if not self.page_from:
                raise ValidationError(_('Article has to have page(s).'))
            if self.editors:
                raise ValidationError(_('Article can not have editors.'))
            if self.place:
                raise ValidationError(_('Article can not have place.'))
            if self.length:
                raise ValidationError(_('Article can not have length.'))
            if self.presenter:
                raise ValidationError(_('Article can not have presenter.'))
        elif self.type == 'TALK':
            if self.identification:
                raise ValidationError(_('Talk can not have ISBN/DOI number.'))
            if self.volume:
                raise ValidationError(_('Talk can not have volume.'))
            if not self.page_from and self.page_to:
                raise ValidationError(_('Page from must be filled if pages are specified.'))
        elif self.type == 'POSTER':
            if self.identification:
                raise ValidationError(_('Poster can not have ISBN/DOI number.'))
            if self.volume:
                raise ValidationError(_('Poster can not have volume.'))
            if not self.page_from and self.page_to:
                raise ValidationError(_('Page from must be filled if pages are specified.'))
            if self.length:
                raise ValidationError(_('Poster can not have length.'))
        if self.presenter and self.presenter not in self.author_set.all():
            raise ValidationError(_('Presenter must be among authors.'))

    @property
    def citation(self):
        #TODO: would be inclusion tag better, when html tags will be used?
        authors = [author.person.name for author in self.author_set.select_related('person').order_by('order')]
        details = []
        if self.publication:
            details.append(u" %s" % self.publication)
        if self.volume:
            details.append(u" %s" % self.volume)
        if self.place:
            details.append(u"%s" % self.place)
        details.append(u"%s" % self.year)
        if self.page_from:
            if self.page_to:
                details.append(u"%s-%s" % (self.page_from, self.page_to))
            else:
                details.append(unicode(self.page_from))

        return u"%s: %s. %s" % (
            u', '.join(authors),
            self.title,
            u', '.join(details)
        )


class Author(models.Model):
    person = models.ForeignKey(Person)
    article = models.ForeignKey(Article)
    order = models.SmallIntegerField()

    class Meta:
        app_label = 'people'
        unique_together = (
            ('person', 'article'),
            ('article', 'order'),
        )

    def __unicode__(self):
        return u'%s %s (%s)' % (self.person, self.article, self.order)

    def clean(self):
        if self.order > 1 \
        and self.article.author_set.exclude(pk=self.pk).filter(order__lt=self.order).count() != (self.order - 1):
            raise ValidationError('Authors must be added in order.')


### Article proxy models

class ArticleBook(Article):
    class Meta:
        app_label = 'publications'
        proxy = True
        verbose_name = _('Book')
        verbose_name_plural = _('Books')


class ArticleArticle(Article):
    class Meta:
        app_label = 'publications'
        proxy = True
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')


class ArticleTalk(Article):
    class Meta:
        app_label = 'publications'
        proxy = True
        verbose_name = _('Talk')
        verbose_name_plural = _('Talks')


class ArticlePoster(Article):
    class Meta:
        app_label = 'publications'
        proxy = True
        verbose_name = _('Poster')
        verbose_name_plural = _('Posters')
