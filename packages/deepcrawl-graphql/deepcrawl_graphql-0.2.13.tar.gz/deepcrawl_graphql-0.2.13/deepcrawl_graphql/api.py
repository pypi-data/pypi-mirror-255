"""
Connection
==========
"""

import pathlib

from gql import Client, gql
from gql.dsl import DSLField, DSLInlineFragment, DSLMutation, DSLQuery, DSLSchema, dsl_gql
from gql.transport.requests import RequestsHTTPTransport

from deepcrawl_graphql.exceptions import MissingCredentials

ENDPOINT = "https://api.lumar.io/graphql"
SCHMEA_PATH = pathlib.Path(__file__).parent.resolve() / "deepcrawl_schema.graphql"
with open(SCHMEA_PATH, "r", encoding="utf-8") as f:
    SCHEMA = f.read()


class DeepCrawlConnection:
    """| DeepCrawlConnection class

    Creates a connection instance used for sending GraphQL queries to DeepCrawl.

    >>> from deepcrawl_graphql.api import DeepCrawlConnection

    >>> DeepCrawlConnection("user_key_id", "secret")
    DeepCrawlConnection instance

    >>> DeepCrawlConnection(token="token")
    DeepCrawlConnection instance

    :param user_key_id: user key, used together with secret for authentication.
    :type user_key_id: int or str
    :param secret: secret key, used together with user_key_id for authentication.
    :type secret: str
    :param token: authentication token, if used ignores the user_key_id and secret
    :type token: str
    """

    def __init__(self, user_key_id=None, secret=None, token=None) -> None:
        if not token:
            if not user_key_id or not secret:
                raise MissingCredentials("Eighter token or user_key_id and secret pair must be provided")
            token = self._get_token(user_key_id, secret)

        self.headers = {"x-auth-token": token}
        self.transport = RequestsHTTPTransport(url=ENDPOINT, headers=self.headers)
        self.client = Client(transport=self.transport, schema=SCHEMA)
        self.ds = DSLSchema(self.client.schema)

    def __str__(self) -> str:
        return "DeepCrawlConnection instance"

    def __repr__(self) -> str:
        return "DeepCrawlConnection instance"

    def run_query(self, query, variables=None, var=None, **kwargs):
        """Runs a query.

        >>> conn = DeepCrawlConnection("user_key_id", "secret")

        There are 3 possible ways you can run a query

        Using a query string. You can use the DeepCrawl explorer to construct the string https://graph-docs.deepcrawl.com/graphql/explorer

        >>> query = 'query MyQuery {version}'
        >>> conn.run_query(query)
        {'version': '1.91.1-next.0-en'}

        Using the gql package to construct a dynamic query.

        >>> from gql.dsl import DSLQuery
        >>> query = DSLQuery(conn.ds.Query.me.select(conn.ds.User.id, conn.ds.User.username))
        >>> conn.run_query(query)
        {
            'me': {
                'id': 'id',
                'username': 'email@example.com'
            }
        }

        >>> from gql.dsl import DSLVariableDefinitions
        >>> from gql.dsl import DSLQuery
        >>> var = DSLVariableDefinitions()
        >>> query = conn.ds.Query.me.select(
                conn.ds.User.accounts.args(first=var.first, after=var.after)
                .select(
                    conn.ds.AccountConnection.nodes.select(
                        conn.ds.Account.id,
                        conn.ds.Account.name,
                    )
                )
                .select(
                    conn.ds.AccountConnection.pageInfo.select(
                        conn.ds.PageInfo.startCursor,
                        conn.ds.PageInfo.endCursor,
                        conn.ds.PageInfo.hasNextPage,
                        conn.ds.PageInfo.hasPreviousPage,
                    )
                )
            )
        >>> conn.run_query(query, variables={"first": 1, "after": "MQ"}, var=var)
        {
            "me": {
                "accounts": {
                    "nodes": [
                        {
                            "id": "id",
                            "name": "name"
                        }
                    ],
                    "pageInfo": {
                        "startCursor": "Mg",
                        "endCursor": "Mg",
                        "hasNextPage": false,
                        "hasPreviousPage": true
                    }
                }
            }
        }
        # For more information about constructing queries with dsl
        # see https://gql.readthedocs.io/en/stable/advanced/dsl_module.html

        Import a query from the deepcrawl_graphql package and use it's prebuild queries.

        >>> from deepcrawl_graphql.me.me import MeQuery
        >>> me_query = MeQuery(conn)
        >>> me_query.select_me()
        >>> conn.run_query(me_query)
        {
            'me': {
                'id': 'id',
                'username': 'email@example.com',
                'email': 'email@example.com',
                'firstName': 'FirstName',
                'lastName': 'LastName',
                'createdAt': '2019-10-27T17:11:17.000Z',
                'updatedAt': '2022-01-15T10:10:38.000Z',
                'jobTitle': None,
                'overallLimitLevelsMax': 1000,
                'overallLimitPagesMax': 10000000,
                'ssoClientId': None,
                'termsAgreed': True,
                'rawID': 'id',
                'permissions': []
            }
        }


        :param query: query object
        :type query: Query or DSLField or DSLQuery or str
        :param variables: variables to use in the query.
            run_query(... variables={"first": 1, "after": "MQ"})
        :type variables: dict or None
        :param var: gql DSLVariableDefinitions instance to be used in the query.
            Works together with variables
        :type var: DSLVariableDefinitions
        :param kwargs: variables to use in the query.
            If variables is not used and the user prefers to send variables as function arguments
            run_query(... first=1, after="MQ")
        """
        from deepcrawl_graphql.query import Query  # pylint: disable=import-outside-toplevel

        if isinstance(query, Query):
            _query = DSLQuery(query.query)
            _query.variable_definitions = query.var
            query = dsl_gql(_query)
        elif isinstance(query, DSLField):
            if var:
                _query = DSLQuery(query)
                _query.variable_definitions = var
                query = dsl_gql(_query)
            else:
                query = dsl_gql(DSLQuery(query))
        elif isinstance(query, DSLQuery):
            query = dsl_gql(query)
        elif isinstance(query, str):
            query = gql(query)
        return self.client.execute(query, variables or kwargs)

    def get_by_base64_id(self, base64_id, object_type, fields):
        """Get object by Base64 id

        >>> conn.get_by_base64_id(
                "TjAxNFJlcG9ydERvd25sb2FkNTk2Njg1MzE",
                "ReportDownload",
                fields=(conn.ds.ReportDownload.id, conn.ds.ReportDownload.fileURL),
            )

        :param base64_id: Object's Base64 id
        :type base64_id: str
        :param object_type: Object's meta type name
        :type object_type: str
        :param fields: Fields to select
        :type fields: List(DSLField)
        """
        fragment = DSLInlineFragment()
        fragment.on(getattr(self.ds, object_type))
        fragment.select(*fields)
        query = self.ds.Query.node.args(id=base64_id).select(fragment)
        return self.run_query(query)

    def run_mutation(self, mutation, variables=None, var=None, **kwargs):
        """Runs a mutation.

        >>> conn = DeepCrawlConnection("user_key_id", "secret")

        There are multiple ways you can run a mutation

        Import the Mutation class from deepcrawl_graphql package and use it's prebuild methods.

        >>> from deepcrawl_graphql.mutation import Mutation
        >>> mutation = Mutation(conn)
        >>> project_input = {"accountId": "acount_id", "name": "Create-Project-0", "primaryDomain": "domain"}
        >>> mutation.create_project(project_input)  # Automatically runs this method
        {
            "createProject": {
                "project": {
                    "id": "id",
                    "name": "Create-Project-0",
                    "primaryDomain": "http://python.deepcrawl.com/",
                    ...
                }
            }
        }

        :param mutation: mutation object
        :type mutation: DSLField or DSLMutation or str
        :param variables: variables to use in the query.
            run_query(... variables={"input": {"name": "name", ...}})
        :type variables: dict or None
        :param var: gql DSLVariableDefinitions instance to be used in the query.
            Works tougether with variables
        :type var: DSLVariableDefinitions
        :param kwargs: variables to use in the query.
            If variables is not used and the user prefers to send variables as function arguments
            run_query(... input={"name": "name", ...})
        """

        if isinstance(mutation, DSLField):
            if var:
                _mutation = DSLMutation(mutation)
                _mutation.variable_definitions = var
                mutation = dsl_gql(_mutation)
            else:
                mutation = dsl_gql(DSLMutation(mutation))
        elif isinstance(mutation, DSLMutation):
            mutation = dsl_gql(mutation)
        elif isinstance(mutation, str):
            mutation = gql(mutation)
        return self.client.execute(mutation, variables or kwargs)

    @staticmethod
    def _get_token(user_key_id, secret) -> str:
        """Get access token using the key id and secret"""
        transport = RequestsHTTPTransport(url=ENDPOINT)
        client = Client(transport=transport, schema=SCHEMA)
        ds = DSLSchema(client.schema)
        query = dsl_gql(
            DSLMutation(
                ds.Mutation.createSessionUsingUserKey.args(
                    input={
                        "userKeyId": user_key_id,
                        "secret": secret,
                    }
                ).select(ds.Session.token)
            )
        )
        response = client.execute(query)
        return response.get("createSessionUsingUserKey", {}).get("token")
