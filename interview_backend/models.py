from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField(max_length=64, unique=True)


class Problem(models.Model):
    title = models.CharField(max_length=256)
    text = models.TextField()
    code_template = models.TextField()
    duration = models.DurationField(default=timedelta(minutes=30))


class Interview(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    company = models.ForeignKey('Company', null=True,
                                on_delete=models.SET_NULL)
    start_time = models.DateTimeField(auto_now_add=True)
    expired_time = models.DateTimeField(null=False)
    finished_time = models.DateTimeField(null=True)


class TestCase(models.Model):
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE)
    input = models.TextField()
    expected_output = models.TextField()


class ProblemSet(models.Model):
    company = models.ForeignKey('Company', null=True,
                                on_delete=models.CASCADE)
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE)


class Task(models.Model):
    interview = models.ForeignKey('Interview', on_delete=models.CASCADE)
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE)


class Submission(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    language = models.CharField(max_length=32)
    code = models.BinaryField()

    class Judgement(models.IntegerChoices):
        AC = 1
        WA = 2
        CE = 3
        TLE = 4
        MLE = 5

    judgement = models.IntegerField(choices=Judgement.choices)
    failed_at = models.ForeignKey('TestCase', null=True,
                                  on_delete=models.SET_NULL)
    failed_output = models.BinaryField()
