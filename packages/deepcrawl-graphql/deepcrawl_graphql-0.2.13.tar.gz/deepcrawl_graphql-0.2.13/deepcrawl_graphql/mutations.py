"""
Mutations
=========
"""

from deepcrawl_graphql.accounts.mutations import AccountMutation
from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.crawls.mutations import CrawlMutation
from deepcrawl_graphql.projects.mutations import ProjectMutation
from deepcrawl_graphql.reports.mutations import ReportDownloadMutation


class Mutation(AccountMutation, ProjectMutation, CrawlMutation, ReportDownloadMutation):
    """Mutation class"""

    def __init__(self, conn: DeepCrawlConnection):
        self.conn = conn
        self.ds = conn.ds
        self.mutation = self.ds.Mutation
