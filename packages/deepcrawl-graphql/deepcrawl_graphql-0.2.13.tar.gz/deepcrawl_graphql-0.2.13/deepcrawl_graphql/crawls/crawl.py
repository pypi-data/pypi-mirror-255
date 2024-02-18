"""
CrawlQuery
==========
"""

from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.query import Query
from deepcrawl_graphql.reports.fields import ReportDownloadFields, ReportFields

from .fields import CrawlFields


class CrawlQuery(CrawlFields, Query):
    """| CrawlQuery class

    Creates a crawl query instance.
    The instance will be passed to the run_query method in order to execute the query.

    >>> from deepcrawl_graphql.crawls.crawl import CrawlQuery

    >>> crawl_query = CrawlQuery(conn, "crawl_id")
    >>> crawl_query.select_crawl()
    >>> crawl_query.select_parquet_files("datasource_name")
    >>> crawl_query.select_compared_to()
    >>> crawl = conn.run_query(crawl_query)

    :param conn: Connection.
    :type conn: DeepCrawlConnection
    :param crawl_id: crawl id.
    :type crawl_id: int or str
    """

    def __init__(self, conn: DeepCrawlConnection, crawl_id) -> None:
        super().__init__(conn)
        self.query = self.query.getCrawl.args(id=crawl_id)

    """
    Crawl
    """

    def select_crawl(self, fields=None):
        """Selects crawl fields.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(*fields or self.fields(self.ds))
        return self

    def select_parquet_files(self, datasource_name, fields=None):
        """Selects crawl parquetFiles.

        :param datasource_name: Datasource name.
        :type datasource_name: str
        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(
            self.ds.Crawl.parquetFiles.args(datasourceName=datasource_name).select(
                *fields or self.parquet_files_fields(self.ds)
            )
        )
        return self

    def select_crawl_type_counts(self, crawl_types, segment_id=None, fields=None):
        """Selects crawl fields.

        Not implemented yet.

        :param crawl_types: Crawl type.
        :type crawl_types: str
        :param segment_id: Segment id.
        :type segment_id: int or str
        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        # Having issues with sending the crawlTypes input.
        raise NotImplementedError()
        args = {"input": {"crawlTypes": crawl_types}}
        if segment_id:
            args["input"]["segmentId"] = segment_id
        self.query.select(
            self.ds.Crawl.crawlTypeCounts.args(**args).select(*fields or self.crawl_type_counts_fields(self.ds))
        )
        return self

    def select_crawl_settings(self, fields=None):
        """Selects crawl crawlSetting.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        # common fields with ProjectQuery
        raise NotImplementedError()

    def select_compared_to(self, fields=None):
        """Selects crawl comparedTo.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(self.ds.Crawl.comparedTo.select(*fields or self.fields(self.ds)))
        return self

    """
    Report
    """

    def select_reports(self, fields=None):
        """Selects crawl reports.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        reports = self.ds.Crawl.reports.args(**self.var_pagination, **self.var_ordering)
        report_nodes = self.ds.ReportConnection.nodes.select(*fields or ReportFields.fields(self.ds))
        pagination = self.ds.ReportConnection.pageInfo.select(*self.page_fields())

        self.query.select(reports.select(report_nodes).select(pagination))
        return self

    def select_report_downloads(self, fields=None):
        """Selects reports downloads.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        report_downloads = self.ds.Crawl.reportDownloads.args(**self.var_pagination, **self.var_ordering)
        report_downloads_nodes = self.ds.ReportDownloadConnection.nodes.select(
            *fields or ReportDownloadFields.fields(self.ds)
        )
        pagination = self.ds.ReportDownloadConnection.pageInfo.select(*self.page_fields())

        self.query.select(report_downloads.select(report_downloads_nodes).select(pagination))
        return self
