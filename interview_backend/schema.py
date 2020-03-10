import graphene
from graphene_django import DjangoObjectType

from .models import Company, User, Problem


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
        company = Company(name=name)
        company.save()
        return CreateCompany(company=company)


class CreateUser(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, name):
        user = User(name=name)
        user.save()
        return CreateUser(user=user)


class CreateProblem(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        text = graphene.String(default_value='')
        code_template = graphene.String(default_value='')

    problem = graphene.Field(ProblemType)

    def mutate(self, info, title, text, code_template):
        problem = Problem.objects.get_or_create(title=title)[0]
        problem.text = text
        problem.code_template = code_template
        problem.save()
        return CreateProblem(problem=problem)


class Query(graphene.ObjectType):
    companies = graphene.List(CompanyType)
    users = graphene.List(UserType)
    problems = graphene.List(ProblemType)

    def resolve_companies(self, info, **kwargs):
        return Company.objects.all()

    def resolve_users(self, info, **kwargs):
        return User.objects.all()

    def resolve_problems(self, info, **kwargs):
        return Problem.objects.all()


class Mutation(graphene.ObjectType):
    create_company = CreateCompany.Field()
    create_user = CreateUser.Field()
    create_problem = CreateProblem.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
