import graphene
from graphene_django import DjangoObjectType

from .models import Company


class CompanyType(DjangoObjectType):
    class Meta:
        model = Company


class CreateCompany(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    company = graphene.Field(CompanyType)

    def mutate(self, info, name):
        company = Company(name=name)
        company.save()
        return company.save()


class Query(graphene.ObjectType):
    companies = graphene.List(CompanyType)

    def resolve_companies(self, info, **kwargs):
        return Company.objects.all()


class Mutation(graphene.ObjectType):
    create_company = CreateCompany.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
