import datetime
import functools
import random

from django.utils import timezone

import graphene
from graphene_django import DjangoObjectType

from django.db import transaction
from django.contrib.auth.models import User
from graphql import GraphQLError

from .models import Company, Problem
from .models import Interview, Task, Submission, TestCase, ProblemSet
from .cache_models import CurrentInterview

PermissionError = GraphQLError('permission denied')


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


class TaskType(DjangoObjectType):
    class Meta:
        model = Task


class SubmissionType(DjangoObjectType):
    class Meta:
        model = Submission


class CreateCompany(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    company = graphene.Field(CompanyType)

    def mutate(self, info, name):
        if not info.context.user.is_staff:
            raise PermissionError
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
            raise PermissionError
        problem = Problem.objects.get_or_create(title=title)[0]
        problem.text = text
        problem.code_template = code_template
        problem.save()
        return CreateProblem(problem=problem)


class StartInterview(graphene.Mutation):
    class Arguments:
        company_id = graphene.ID()

    id = graphene.ID()

    @transaction.atomic
    def mutate(self, info, company_id=None):
        # FIXME: performance issue. use Redis cache
        # company = Company.objects.get(id=company_id)
        # print(company)
        # problems = ProblemSet.objects.get(company=company)
        # problems = random.choices(problems, k=company.problems_per_interview)
        # duration_total = functools.reduce(
        #     lambda x, y: x.problem.duration + y.problem.duration, problems
        # )
        if company_id is not None:
            raise NotImplementedError

        user = info.context.user
        current_interview = CurrentInterview(user_id=user.id)

        if current_interview.get() is not None:
            raise GraphQLError('another interview is ongoing')
        problems = Problem.objects.all()
        problems = random.choices(problems, k=3)
        duration_total = functools.reduce(
            lambda x, y: x + y.duration, problems, datetime.timedelta()
        )
        interview = Interview(
            user=user,
            company=None,
            expired_time=timezone.now() + duration_total
        )
        interview.save()
        for problem in problems:
            task = Task(problem=problem, interview=interview)
            task.save()

        CurrentInterview(user_id=user.id).set(interview, timeout=3600 * 24)
        return StartInterview(id=interview.id)


class FinishInterview(graphene.Mutation):
    id = graphene.ID()

    def mutate(self, info, **kwargs):
        user = info.context.user
        current_interview = CurrentInterview(user_id=user.id)
        interview = current_interview.get()
        if interview is None:
            raise GraphQLError('no interview is ongoing')
        interview.finished_time = timezone.now()
        interview.save()

        current_interview.unset()
        return FinishInterview(id=interview.id)


class Query(graphene.ObjectType):
    current_user = graphene.Field(UserType)
    current_interview = graphene.Field(InterviewType)
    interview = graphene.Field(InterviewType, id=graphene.ID())
    my_interviews = graphene.List(InterviewType)
    all_users = graphene.List(UserType)
    all_companies = graphene.List(CompanyType)
    all_problems = graphene.List(ProblemType)
    all_interviews = graphene.List(InterviewType)

    def resolve_current_user(self, info, **kwargs):
        return info.context.user

    def resolve_current_interview(self, info, **kwargs):
        user = info.context.user
        current_interview = CurrentInterview(user_id=user.id)
        return current_interview.get()

    def resolve_interview(self, info, id):
        user = info.context.user
        interview = Interview.objects.get(id=id)
        if interview.user != user:
            return None
        return interview

    def resolve_all_users(self, info, **kwargs):
        if not info.context.user.is_staff:
            raise PermissionError
        return User.objects.all()

    def resolve_all_companies(self, info, **kwargs):
        return Company.objects.all()

    def resolve_all_problems(self, info, **kwargs):
        if not info.context.user.is_staff:
            raise PermissionError
        return Problem.objects.all()

    def resolve_all_interviews(self, info, **kwargs):
        if not info.context.user.is_staff:
            raise PermissionError
        return Interview.objects.all()


class Mutation(graphene.ObjectType):
    create_company = CreateCompany.Field()
    create_problem = CreateProblem.Field()
    # assign_problem = AssignProblem.Field()
    start_interview = StartInterview.Field()
    finish_interview = FinishInterview.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
