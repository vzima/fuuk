from django.conf import settings
from django.contrib import admin
from django.db.models import TextField
from django.utils.translation import ugettext_lazy as _
from markdownx.widgets import AdminMarkdownxWidget
from modeltranslation.admin import TranslationAdmin

from .forms import FlatpageForm
from .models import FlatPage


class FlatPageAdmin(TranslationAdmin):
    form = FlatpageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {'classes': ('collapse',),
                                 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )
    list_display = ('url', 'title')
    list_filter = ('sites', 'enable_comments', 'registration_required')
    search_fields = ['url'] + ['title_%s' % l for l, _ in settings.LANGUAGES]

    # Use markdownx for flatpages
    formfield_overrides = {
        TextField: {'widget': AdminMarkdownxWidget},
    }


admin.site.register(FlatPage, FlatPageAdmin)
