# coding: utf-8
from django.contrib.admin import ModelAdmin, TabularInline
from django.db import models
from multilingual import MultilingualModelAdmin

from fuuk.people.admin.fields import NullCharField
from fuuk.people.admin.forms import ArticleArticleForm, ArticleBookForm, ArticleConferenceForm
from fuuk.people.models import Attachment, Author


class DepartmentAdmin(MultilingualModelAdmin):
    list_display = ('name', 'fax')
    search_fields = ('translations__name', )

    formfield_overrides = {
        models.CharField: {'form_class': NullCharField},
    }


class PlaceAdmin(MultilingualModelAdmin):
    list_display = ('name', 'phone', 'department')
    search_fields = ('translations__name', )

    formfield_overrides = {
        models.CharField: {'form_class': NullCharField},
    }


class HumanAdmin(MultilingualModelAdmin):
    list_display = ('nickname', 'email', 'birth_date', 'birth_place')
    ordering = ('nickname',)
    search_fields = ('nickname', 'email')

    formfield_overrides = {
        models.CharField: {'form_class': NullCharField},
    }

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields

        fields = list(self.readonly_fields)
        fields.extend(['user', 'nickname', 'subtitle', 'birth_place', 'birth_date', 'email'])
        return tuple(fields)

    def has_change_permission(self, request, obj=None):
        """
        If `obj` is None, this should return True if the given request has
        permission to delete *any* object of the given type.
        """
        if request.user.is_superuser:
            return True

        if obj:
            if request.user == getattr(obj, 'user', None):
                return True
            return False

        return super(HumanAdmin, self).has_change_permission(request, obj)

    def queryset(self, request):
        queryset = super(HumanAdmin, self).queryset(request)
        if request.user.is_superuser:
            return queryset

        human = request.user.human
        return queryset.filter(
            pk=human.pk
        )


class PersonAdmin(ModelAdmin):
    list_display = ('last_name', 'first_name', 'is_active', 'type')
    list_filter = ('type', 'is_active')
    ordering = ('last_name', )
    search_fields = ('human__nickname', 'first_name', 'last_name')

    filter_horizontal = ('place',)
    formfield_overrides = {
        models.CharField: {'form_class': NullCharField},
    }

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields

        fields = list(self.readonly_fields)
        fields.extend(['human', 'is_active', 'type'])
        return tuple(fields)


class AttachmentAdmin(ModelAdmin):
    list_display = ('course', 'title')
    search_fields = ('title', 'course__translations__name')


class AttachmentInlineAdmin(TabularInline):
    model = Attachment
    extra = 3


class CourseAdmin(MultilingualModelAdmin):
    list_display = ('name', 'ls', 'zs', 'code')
    ordering = ('code', )
    search_fields = ('code', 'translations__name')

    filter_horizontal = ('lectors', 'practical_lectors')
    formfield_overrides = {
        models.CharField: {'form_class': NullCharField},
    }
    inlines = (AttachmentInlineAdmin, )

    def has_change_permission(self, request, obj=None):
        """
        If `obj` is None, this should return True if the given request has
        permission to delete *any* object of the given type.
        """
        if request.user.is_superuser:
            return True

        if obj:
            for lector in obj.lectors.all():
                if request.user == getattr(lector.human, 'user', None):
                    return True
            for lector in obj.practical_lectors.all():
                if request.user == getattr(lector.human, 'user', None):
                    return True
            return False

        return super(CourseAdmin, self).has_change_permission(request, obj)

    def queryset(self, request):
        queryset = super(CourseAdmin, self).queryset(request)
        if request.user.is_superuser:
            return queryset
        human = request.user.human
        return queryset.filter(
            pk__in=queryset.filter(lectors__human=human) | queryset.filter(practical_lectors__human=human)
        )


class AgencyAdmin(MultilingualModelAdmin):
    list_display = ('shortcut', 'name')
    search_fields = ('translations__shortcut', 'translations__name')


class GrantAdmin(MultilingualModelAdmin):
    list_display = ('author', 'number', 'title', 'start', 'end')
    list_filter = ('agency', 'start')
    ordering = ('-end', )
    search_fields = ('number', 'translations__title')

    filter_horizontal = ('co_authors',)

    def has_change_permission(self, request, obj=None):
        """
        If `obj` is None, this should return True if the given request has
        permission to delete *any* object of the given type.
        """
        if request.user.is_superuser:
            return True

        if obj:
            if request.user == getattr(obj.author.human, 'user', None):
                return True
            for author in obj.co_authors.all():
                if request.user == getattr(author.human, 'user', None):
                    return True
            return False

        return super(GrantAdmin, self).has_change_permission(request, obj)

    def queryset(self, request):
        queryset = super(GrantAdmin, self).queryset(request)
        if request.user.is_superuser:
            return queryset
        human = request.user.human
        return queryset.filter(
            pk__in=queryset.filter(author__human=human) | queryset.filter(co_authors__human=human)
        )


class ThesisAdmin(MultilingualModelAdmin):
    list_display = ('type', 'title', 'author', 'advisor', 'year')
    list_filter = ('type', 'year', 'defended')
    ordering = ('-year', )
    search_fields = ('translations__title', 'translations__keywords', 'author__first_name', 'author__last_name')

    filter_horizontal = ('consultants',)
    formfield_overrides = {
        models.CharField: {'form_class': NullCharField},
    }

    def has_change_permission(self, request, obj=None):
        """
        If `obj` is None, this should return True if the given request has
        permission to delete *any* object of the given type.
        """
        if request.user.is_superuser:
            return True

        if obj:
            if request.user == getattr(obj.author.human, 'user', None):
                return True
            if request.user == getattr(obj.advisor.human, 'user', None):
                return True
            return False

        return super(ThesisAdmin, self).has_change_permission(request, obj)

    def queryset(self, request):
        queryset = super(ThesisAdmin, self).queryset(request)
        if request.user.is_superuser:
            return queryset
        human = request.user.human
        return queryset.filter(
            pk__in=queryset.filter(author__human=human) | queryset.filter(advisor__human=human)
        )


class NewsAdmin(MultilingualModelAdmin):
    list_display = ('title', 'start', 'end')
    ordering = ('-end', )
    search_fields = ('translations__title', 'hyperlink')

    formfield_overrides = {
        models.CharField: {'form_class': NullCharField},
    }


class AuthorInlineAdmin(TabularInline):
    model = Author
    extra = 3
    fields = ('order', 'person')
    readonly_fields = ('order',)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        defaults = {
            'queryset': db_field.rel.to.objects.order_by('last_name', 'first_name')
        }
        defaults.update(kwargs)
        return super(AuthorInlineAdmin, self).formfield_for_foreignkey(db_field, request, **defaults)

    def queryset(self, request):
        # Return ordered authors
        return super(AuthorInlineAdmin, self).queryset(request).order_by('order')


###############################################################################
# Articles
class BaseProxyArticleAdmin(ModelAdmin):
    list_display = ('title', 'year')
    list_filter = ('year', 'accepted')
    search_fields = ('identification', 'title', 'publication')

    inlines = [AuthorInlineAdmin, ]
    formfield_overrides = {
        models.CharField: {'form_class': NullCharField},
    }

    def has_change_permission(self, request, obj=None):
        """
        If `obj` is None, this should return True if the given request has
        permission to delete *any* object of the given type.
        """
        if request.user.is_superuser:
            return True

        if obj:
            for author in obj.author_set.all():
                if request.user == getattr(author.person.human, 'user', None):
                    return True
            return False

        return super(BaseProxyArticleAdmin, self).has_change_permission(request, obj)

    def queryset(self, request):
        queryset = super(BaseProxyArticleAdmin, self).queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(author__person__human__user=request.user)


class ArticleBookAdmin(BaseProxyArticleAdmin):
    form = ArticleBookForm

    def queryset(self, request):
        return super(ArticleBookAdmin, self).queryset(request).filter(type='BOOK')


class ArticleArticleAdmin(BaseProxyArticleAdmin):
    form = ArticleArticleForm

    def queryset(self, request):
        return super(ArticleArticleAdmin, self).queryset(request).filter(type='ARTICLE')


class ArticleConferenceAdmin(BaseProxyArticleAdmin):
    list_display = ('title', 'type', 'year')
    list_filter = ('year', 'accepted', 'type')

    form = ArticleConferenceForm

    def queryset(self, request):
        return super(ArticleConferenceAdmin, self).queryset(request).filter(type__in=('TALK', 'INVITED', 'POSTER'))
