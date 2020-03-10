import graphene
from django.core.exceptions import PermissionDenied
from graphene_django import DjangoObjectType

from django.contrib.auth.models import User
from .models import Company, Problem


class CompanyType(DjangoObjectType):
    class Meta:
        model = Company


class UserType(DjangoObjectType):
    class Meta:
        model = User


class ProblemType(DjangoObjectType):
    class Meta:
        model = Problem


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


schema = graphene.Schema(query=Query, mutation=Mutation)
