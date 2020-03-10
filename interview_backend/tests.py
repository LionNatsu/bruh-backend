import json

from graphene_django.utils.testing import GraphQLTestCase
from .schema import schema


class EntityTestCase(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

    def test_create_company(self):
        resp = self.query('''
            mutation {
                createCompany(name: "cp1") { company { name } }
            }
            ''')
        self.assertResponseNoErrors(resp)
        resp = self.query('{ companies { id } }')
        self.assertResponseNoErrors(resp)
        content = json.loads(resp.content)
        self.assertDictEqual(content, {'data': {'companies': [{'id': '1'}]}})

    def test_create_user(self):
        resp = self.query('''
            mutation {
                createUser(name: "bigcat") { user { name } }
            }
            ''')
        self.assertResponseNoErrors(resp)
        resp = self.query('{ users { id } }')
        self.assertResponseNoErrors(resp)
        content = json.loads(resp.content)
        self.assertDictEqual(content, {'data': {'users': [{'id': '1'}]}})

    def test_create_problem(self):
        resp = self.query('''
            mutation {
                createProblem(title: "Title") { problem { title }  }
            }
            ''')
        self.assertResponseNoErrors(resp)
        resp = self.query('{ problems { id } }')
        self.assertResponseNoErrors(resp)
        content = json.loads(resp.content)
        self.assertDictEqual(content, {'data': {'problems': [{'id': '1'}]}})
