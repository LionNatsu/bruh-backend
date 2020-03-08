import json

from graphene_django.utils.testing import GraphQLTestCase
from .schema import schema


class UserTestCase(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

    def test_create_company(self):
        resp = self.query('''
            mutation {
                createCompany(name: "cp1") {}
            }
            ''')
        print(resp.content)
        self.assertResponseNoErrors(resp)
        resp = self.query('{ companies { id } }')
        self.assertResponseNoErrors(resp)
