import datetime
import functools
import random
from django.core.exceptions import PermissionDenied
from django.utils import timezone

import graphene
from graphene_django import DjangoObjectType

from django.db import transaction
from django.contrib.auth.models import User
from .models import Company, Problem
from .models import Interview, Task, Submission, TestCase, ProblemSet


class CompanyType(DjangoObjectType):
    class Meta:
        model = Company


class UserType(DjangoObjectType):
    class Meta:
        model = User


class ProblemType(DjangoObjectType):
    class Meta:
        model = Problem


class InterviewType(DjangoObjectType):
    class Meta:
        model = Interview


class CreateCompany(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    company = graphene.Field(CompanyType)

    def mutate(self, info, name):
        if not info.context.user.is_staff:
            raise PermissionDenied()
        company = Company(name=name)
        company.save()
        return CreateCompany(company=company)


class CreateProblem(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        text = graphene.String(default_value='')
        code_template = graphene.String(default_value='')

    problem = graphene.Field(ProblemType)

    def mutate(self, info, title, text, code_template):
        if not info.context.user.is_staff:
            raise PermissionDenied()
        problem = Problem.objects.get_or_create(title=title)[0]
        problem.text = text
        problem.code_template = code_template
        problem.save()
        return CreateProblem(problem=problem)


class StartInterview(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    id = graphene.ID()

    @transaction.atomic
    def mutate(self, info, id=None):
        # company = Company.objects.get(id=id)
        # # FIXME: performance issue. use Redis cache
        # print(company)
        # problems = ProblemSet.objects.get(company=company)
        # problems = random.choices(problems, k=company.problems_per_interview)
        # duration_total = functools.reduce(
        #     lambda x, y: x.problem.duration + y.problem.duration, problems
        # )
        problems = Problem.objects.all()
        problems = random.choices(problems, k=3)
        duration_total = functools.reduce(
            lambda x, y: x + y.duration, problems, datetime.timedelta()
        )
        print(duration_total, timezone.now(), timezone.now() + duration_total)
        interview = Interview(
            user=info.context.user,
            company=None,
            expired_time=timezone.now() + duration_total
        )
        interview.save()
        for problem in problems:
            task = Task(problem=problem, interview=interview)
            task.save()

        return StartInterview(id=interview.id)


class Query(graphene.ObjectType):
    current_user = graphene.Field(UserType)
    all_users = graphene.List(UserType)
    all_companies = graphene.List(CompanyType)
    all_problems = graphene.List(ProblemType)

    def resolve_current_user(self, info, **kwargs):
        return info.context.user

    def resolve_all_users(self, info, **kwargs):
        if not info.context.user.is_staff:
            raise PermissionDenied
        return User.objects.all()

    def resolve_all_companies(self, info, **kwargs):
        return Company.objects.all()

    def resolve_all_problems(self, info, **kwargs):
        if not info.context.user.is_staff:
            raise PermissionDenied
        return Problem.objects.all()


class Mutation(graphene.ObjectType):
    create_company = CreateCompany.Field()
    create_problem = CreateProblem.Field()
    # assign_problem = AssignProblem.Field()
    start_interview = StartInterview.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
