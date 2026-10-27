from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    """Represents an online course that learners can enroll in."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    # Many-to-many: learners who have enrolled, via Enrollment through-model
    learners = models.ManyToManyField(
        User,
        through='Enrollment',
        related_name='enrolled_courses',
        blank=True,
    )

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    """Tracks which learner is enrolled in which course and in what mode."""
    AUDIT = 0
    HONOR = 1
    BETA = 2
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'Beta'),
    ]

    learner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    date_enrolled = models.DateTimeField(auto_now_add=True)
    mode = models.SmallIntegerField(choices=COURSE_MODES, default=HONOR)

    def __str__(self):
        return f'{self.learner.username} enrolled in {self.course.name}'


class Lesson(models.Model):
    """A single lesson belonging to a Course."""
    title = models.CharField(max_length=255)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
    )
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.course.name} \u2013 {self.title}'


class Question(models.Model):
    """An exam question associated with a Course (optionally scoped to a Lesson)."""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='questions',
    )
    # Optional: scope the question to a specific lesson
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        related_name='questions',
        null=True,
        blank=True,
    )
    question_text = models.TextField()
    # Contribution of this question to the overall exam grade
    grade = models.FloatField(default=1.0)

    def is_get_score(self, selected_choice_ids):
        """
        Returns True if the set of selected_choice_ids exactly matches
        the set of correct choices for this question (all correct, none wrong).
        """
        correct_ids = set(
            self.choices.filter(is_correct=True).values_list('id', flat=True)
        )
        return correct_ids == set(selected_choice_ids)

    def __str__(self):
        return f'Q({self.id}): {self.question_text[:80]}'


class Choice(models.Model):
    """A selectable answer choice for a Question."""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
    )
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        marker = '\u2713' if self.is_correct else '\u2717'
        return f'[{marker}] {self.choice_text[:80]}'


class Submission(models.Model):
    """
    Records a learner's exam submission linked to an Enrollment.
    The many-to-many `choices` field stores every Choice the learner
    selected, enabling exam score calculation at any point.
    """
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='submissions',
    )
    choices = models.ManyToManyField(
        Choice,
        related_name='submissions',
        blank=True,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'Submission by {self.enrollment.learner.username} '
            f'for {self.enrollment.course.name} at {self.submitted_at}'
        )
