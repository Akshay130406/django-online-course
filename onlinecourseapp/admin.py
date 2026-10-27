from django.contrib import admin

from .models import Course, Enrollment, Lesson, Question, Choice, Submission


# ---------------------------------------------------------------------------
# Inlines
# ---------------------------------------------------------------------------

class ChoiceInline(admin.TabularInline):
    """
    Manage Choice objects directly on the Question change page.
    Choice has a ForeignKey to Question, so Question is the correct parent.
    """
    model = Choice
    extra = 2  # show 2 blank choice rows by default


class QuestionInline(admin.TabularInline):
    """
    Display Questions inline on the Course change page.
    Question has a ForeignKey to Course, so Course is the correct parent.
    """
    model = Question
    extra = 1  # show 1 blank question row by default


# ---------------------------------------------------------------------------
# ModelAdmin classes
# ---------------------------------------------------------------------------

class QuestionAdmin(admin.ModelAdmin):
    """Admin view for Questions, with inline choice management."""
    inlines = [ChoiceInline]
    list_display = ['id', 'question_text', 'course', 'lesson', 'grade']
    list_filter = ['course']
    search_fields = ['question_text']


class LessonAdmin(admin.ModelAdmin):
    """Admin view for Lessons."""
    list_display = ['id', 'title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title']
    ordering = ['course', 'order']


class CourseAdmin(admin.ModelAdmin):
    """Admin view for Courses, with inline question management."""
    inlines = [QuestionInline]
    list_display = ['id', 'name', 'pub_date']
    search_fields = ['name']


# ---------------------------------------------------------------------------
# Registrations
# ---------------------------------------------------------------------------

admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Enrollment)
admin.site.register(Submission)
