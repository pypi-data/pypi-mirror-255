"""
MeQuery
=======
"""

from deepcrawl_graphql.accounts.fields import AccountFields
from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.query import Query

from .fields import MeFields


class MeQuery(MeFields, Query):
    """| MeQuery class

    Creates a me query instance. "Me" being the authenticated user.
    The instance will be passed to the run_query method in order to execute the query.

    >>> from deepcrawl_graphql.me.me import MeQuery

    >>> me_query = MeQuery(conn)
    >>> me_query.select_me()
    >>> me_query.select_accounts()
    >>> me = conn.run_query(me_query)

    :param conn: Connection.
    :type conn: DeepCrawlConnection
    """

    def __init__(self, conn: DeepCrawlConnection) -> None:
        super().__init__(conn)
        self.query = self.query.me

    def select_me(self, fields=None):
        """Selects user fields.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(*fields or self.fields(self.ds))
        return self

    def select_accounts(self, fields=None):
        """Selects users accounts.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        accounts = self.ds.User.accounts.args(**self.var_pagination, **self.var_ordering)
        account_nodes = self.ds.AccountConnection.nodes.select(*fields or AccountFields.fields(self.ds))
        pagination = self.ds.AccountConnection.pageInfo.select(*self.page_fields())

        self.query.select(accounts.select(account_nodes).select(pagination))
        return self
