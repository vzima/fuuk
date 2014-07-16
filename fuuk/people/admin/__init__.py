from django.contrib import admin

from fuuk.people.admin.options import PlaceAdmin, DepartmentAdmin, PersonAdmin, HumanAdmin, CourseAdmin, AttachmentAdmin, \
    GrantAdmin, ThesisAdmin, AgencyAdmin, NewsAdmin, \
    ArticleBookAdmin, ArticleArticleAdmin, ArticleConferenceAdmin
from fuuk.people.models import Department, Place, Human, Person, Course, Attachment, Grant, Author, Thesis, Agency, \
    ArticleBook, ArticleArticle, ArticleConference, News


admin.site.register(Place, PlaceAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Human, HumanAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Grant, GrantAdmin)
admin.site.register(Thesis, ThesisAdmin)
admin.site.register(Agency, AgencyAdmin)
admin.site.register(News, NewsAdmin)

# administration of publications - article proxy models
admin.site.register(ArticleBook, ArticleBookAdmin)
admin.site.register(ArticleArticle, ArticleArticleAdmin)
admin.site.register(ArticleConference, ArticleConferenceAdmin)
