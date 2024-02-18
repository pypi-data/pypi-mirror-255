from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.query import Query

from .fields import ReportTypeFields


class ReportTypeQuery(ReportTypeFields, Query):
    def __init__(self, conn: DeepCrawlConnection) -> None:
        super().__init__(conn)
        self.query = self.query.getReportTypes

    def select_report_type(self):
        self.query.select(*self.fields(self.ds))
        return self
