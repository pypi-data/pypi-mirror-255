"""
ProjectQuery
============
"""

from deepcrawl_graphql.accounts.fields import AccountFields
from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.crawls.fields import CrawlFields
from deepcrawl_graphql.query import Query

from .fields import ProjectFields


class ProjectQuery(ProjectFields, Query):
    """| ProjectQuery class

    Creates a project query instance.
    The instance will be passed to the run_query method in order to execute the query.

    >>> from deepcrawl_graphql.projects.project import ProjectQuery

    >>> project_query = ProjectQuery(conn, "project_id")
    >>> project_query.select_project()
    >>> project_query.select_sitemaps()
    >>> project_query.select_advanced_crawl_rate()
    >>> project_query.select_majestic_configuration()
    >>> project_query.select_location()
    >>> project_query.select_google_search_configuration()
    >>> project_query.select_custom_extraction_settings()
    >>> project_query.select_account()
    >>> project_query.select_crawls()
    >>> project = conn.run_query(project_query)

    :param conn: Connection.
    :type conn: DeepCrawlConnection
    :param project_id: project id.
    :type project_id: int or str
    """

    def __init__(self, conn: DeepCrawlConnection, project_id) -> None:
        super().__init__(conn)
        self.query = self.query.getProject.args(id=project_id)

    """
    Project
    """

    def select_project(self, fields=None):
        """Selects project fields.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(*fields or self.fields(self.ds))
        return self

    def select_sitemaps(self, fields=None):
        """Selects project sitemaps.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(self.ds.Project.sitemaps.select(*fields or self.sitemaps_fields(self.ds)))
        return self

    def select_advanced_crawl_rate(self, fields=None):
        """Selects project maximumCrawlRateAdvanced.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(
            self.ds.Project.maximumCrawlRateAdvanced.select(*fields or self.advanced_crawl_rate_fields(self.ds))
        )
        return self

    def select_majestic_configuration(self, fields=None):
        """Selects project majesticConfiguration.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(
            self.ds.Project.majesticConfiguration.select(*fields or self.majestic_configuration_fields(self.ds))
        )
        return self

    def select_location(self, fields=None):
        """Selects project location.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(self.ds.Project.location.select(*fields or self.location_fields(self.ds)))
        return self

    def select_last_finished_crawl(self, fields=None):
        """Selects project lastFinishedCrawl.

        :param fields: Select Crawl specific fields.
        :type fields: List(DSLField)
        """
        fields = fields or (
            self.ds.Crawl.id,
            self.ds.Crawl.rawID,
            self.ds.Crawl.finishedAt
        )
        self.query.select(
            self.ds.Project.lastFinishedCrawl.select(
                *fields
            )
        )
        return self

    def select_google_search_configuration(self, fields=None):
        """Selects project googleSearchConsoleConfiguration.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(
            self.ds.Project.googleSearchConsoleConfiguration.select(
                *fields or self.google_search_configuration_fields(self.ds)
            )
        )
        return self

    def select_google_analytics_project_view(self, fields=None):
        """Selects project googleAnalyticsProjectView.

        Not implemented yet.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        raise NotImplementedError()

    def select_custom_extraction_settings(self, fields=None):
        """Selects project customExtractions."""
        self.query.select(
            self.ds.Project.customExtractions.select(*fields or self.custom_extraction_setting_fields(self.ds))
        )
        return self

    """
    Account
    """

    def select_account(self, fields=None):
        """Selects project account.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(self.ds.Project.account.select(*fields or AccountFields.fields(self.ds)))
        return self

    """
    Crawl
    """

    def select_crawls(self, fields=None):
        """Selects project crawls.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        crawls = self.ds.Project.crawls.args(**self.var_pagination, **self.var_ordering)
        crawl_nodes = self.ds.CrawlConnection.nodes.select(*fields or CrawlFields.fields(self.ds))
        pagination = self.ds.CrawlConnection.pageInfo.select(*self.page_fields())

        self.query.select(crawls.select(crawl_nodes).select(pagination))
        return self

    """
    Schedule
    """

    def select_schedule(self, fields=None):
        """Selects project Schedule."""
        self.query.select(
            self.ds.Project.schedule.select(*fields or self.schedule_fields(self.ds))
        )
        return self
