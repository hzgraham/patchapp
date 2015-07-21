from django.contrib import admin

# Register your models here.
from autopatch.models import Question, Choice, Post, Category, Page

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    
#class QuestionAdmin(admin.ModelAdmin):
#    fields = ['pub_date', 'question_text']

class QuestionAdmin(admin.ModelAdmin):
    # fieldsets = [
    #     (None,               {'fields': ['question_text']}),
    #     ('Date Information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    # ]
    # inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']
    
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Page)
