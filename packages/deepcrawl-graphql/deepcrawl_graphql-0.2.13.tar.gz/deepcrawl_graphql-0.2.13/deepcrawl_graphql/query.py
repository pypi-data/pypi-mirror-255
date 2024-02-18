"""
Base Query
==========
"""

from gql.dsl import DSLVariableDefinitions

from deepcrawl_graphql.api import DeepCrawlConnection


class Query:
    """Query class"""

    def __init__(self, conn: DeepCrawlConnection) -> None:
        self.ds = conn.ds
        self.query = self.ds.Query
        self.var = DSLVariableDefinitions()
        self.var_pagination = {
            "first": self.var.first.default(100),
            "last": self.var.last,
            "after": self.var.after,
            "before": self.var.before,
        }
        self.var_first_after_pagination = {
            "first": self.var.first.default(100),
            "after": self.var.after,
        }
        self.var_ordering = {
            "orderBy": self.var.order_by,
        }

    def page_fields(self):
        """Returns a tule of PageInfo fields."""
        return (
            self.ds.PageInfo.startCursor,
            self.ds.PageInfo.endCursor,
            self.ds.PageInfo.hasNextPage,
            self.ds.PageInfo.hasPreviousPage,
        )
