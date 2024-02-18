"""
Crawl Shortcuts
===============
"""

from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.query import Query


class CrawlShortcuts(Query):
    """| Shortcuts class

    Creates a shortcuts query instance
    The instance will be passed to the run_query method in order to execute the query.

    >>> from deepcrawl_graphql.shortcuts.crawl_shortcuts import CrawlShortcuts

    >>> query = CrawlShortcuts(conn, "crawl_id")
    >>> crawl_query.select_explorer_data("path1", report_filters)

    :param conn: Connection.
    :type conn: DeepCrawlConnection
    :param crawl_id: crawl id.
    :type crawl_id: int or str
    """

    def __init__(self, conn: DeepCrawlConnection, crawl_id) -> None:
        super().__init__(conn)
        self.query = self.query.getCrawl.args(id=crawl_id)

    def select_explorer_data(self, path, report_filters, agregate_filters=None, paginate=True):
        """Select Explorer data

        :param path: Path. One of the paths from one to 9 e.g. path1
        :type path: str
        :param report_filters: Report filters. reportTemplateCode and reportTypeCode are mandatory
        :type report_filters: dict
        :param agregate_filters: Filters applied to the aggregation.
        :type agregate_filters: dict
        :param paginate: Include pagination or not.
        :type paginate: bool
        """
        # Crawl
        self.query.select(self.ds.Crawl.id)

        # Aggregations
        aggregate_nodes = self.ds.CrawlUrlAggregateConnection.nodes.select(
            getattr(self.ds.CrawlUrlAggregate, path),
            self.ds.CrawlUrlAggregate.count.select(self.ds.CrawlUrlCountCalculation.url),
            self.ds.CrawlUrlAggregate.avg.select(self.ds.CrawlUrlAvgCalculation.deeprank),
            self.ds.CrawlUrlAggregate.sum.select(self.ds.CrawlUrlSumCalculation.linksInCount),
        )

        # Filtering
        paginated_crawl_aggregates = self.ds.Report.paginatedCrawlUrlsAggregates.args(
            dimensions=[path], filter=agregate_filters
        )
        paginated_crawl_aggregates.select(aggregate_nodes)

        # Pagination
        if paginate:
            pagination = self.ds.CrawlUrlAggregateConnection.pageInfo.select(*self.page_fields())
            paginated_crawl_aggregates.args(**self.var_first_after_pagination)
            paginated_crawl_aggregates.select(pagination)

        # Report Node
        report_nodes = self.ds.ReportConnection.nodes.select(self.ds.Report.id, paginated_crawl_aggregates)
        self.query.select(self.ds.Crawl.reports.args(filter=report_filters).select(report_nodes))

        return self
