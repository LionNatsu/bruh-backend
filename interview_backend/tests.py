import json

from graphene_django.utils.testing import GraphQLTestCase
from django.contrib.auth.models import User
from .schema import schema


class StaffTestCase(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

    def setUp(self):
        super(StaffTestCase, self).setUp()
        User.objects.create_user(
            username='john', password='secret')
        User.objects.create_user(
            username='staff', password='secret', is_staff=True)

    def test_non_staff_create_company(self):
        self._client.login(username='john', password='secret')
        resp = self.query('''
            mutation {
                createCompany(name: "cp1") { company { name } }
            }
            ''')
        self.assertResponseHasErrors(resp)

    def test_staff_create_company(self):
        self._client.login(username='staff', password='secret')
        resp = self.query('''
            mutation {
                createCompany(name: "cp1") { company { name } }
            }
            ''')
        self.assertResponseNoErrors(resp)

    def test_non_staff_all_companies(self):
        self._client.login(username='john', password='secret')
        resp = self.query('''
            {
                allCompanies{ name }
            }
            ''')
        self.assertResponseNoErrors(resp)

    def test_staff_all_companies(self):
        self._client.login(username='staff', password='secret')
        resp = self.query('''
            {
                allCompanies{ name }
            }
            ''')
        self.assertResponseNoErrors(resp)


class EntityTestCase(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

    def setUp(self):
        super(EntityTestCase, self).setUp()
        User.objects.create_user(
            username='staff', password='secret', is_staff=True)
        self._client.login(username='staff', password='secret')

    def test_create_company(self):
        resp = self.query('''
            mutation {
                createCompany(name: "cp1") { company { name } }
            }
            ''')
        self.assertResponseNoErrors(resp)
        resp = self.query('{ allCompanies { id } }')
        self.assertResponseNoErrors(resp)
        content = json.loads(resp.content)
        self.assertDictEqual(content, {'data': {'allCompanies': [{'id': '1'}]}})

    def test_create_problem(self):
        resp = self.query('''
            mutation {
                createProblem(title: "Title", text: "<p>hello</p>") {
                    problem { title } 
                }
            }
            ''')
        self.assertResponseNoErrors(resp)
        resp = self.query('{ allProblems { id } }')
        self.assertResponseNoErrors(resp)
        content = json.loads(resp.content)
        self.assertDictEqual(content, {'data': {'allProblems': [{'id': '1'}]}})


class InterviewTestCase(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

    def setUp(self):
        super(InterviewTestCase, self).setUp()
        User.objects.create_user(
            username='john', password='secret')
        User.objects.create_user(
            username='staff', password='secret', is_staff=True)

    def test_interview(self):
        self._client.login(username='staff', password='secret')
        resp = self.query('''
            mutation {
                createProblem(title: "Title", text: "<p>hello</p>") {
                    problem { title } 
                }
            }
            ''')
        self.assertResponseNoErrors(resp)
        self._client.login(username='john', password='secret')
        resp = self.query('''
            mutation {
                startInterview { id }
            }
            ''')
        self.assertResponseNoErrors(resp)
        resp = self.query('''
            {
                currentInterview {
                    expiredAt
                    tasks {
                        title
                        text
                        code_template
                        submission {
                            state
                        }
                    }
                }
            }
            ''')
        self.assertResponseNoErrors(resp)
