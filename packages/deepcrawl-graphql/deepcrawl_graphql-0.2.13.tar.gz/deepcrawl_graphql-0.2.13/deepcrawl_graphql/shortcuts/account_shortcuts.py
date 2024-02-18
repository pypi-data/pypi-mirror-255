"""
Account Shortcuts
=================
"""
import logging

from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.query import Query

logger = logging.getLogger(__name__)


class AccountShortcuts(Query):
    """| Account Shortcuts class

    Creates an account shortcuts query instance
    The instance will be passed to the run_query method in order to execute the query.

    >>> from deepcrawl_graphql.shortcuts.account_shortcuts import AccountShortcuts

    >>> query = AccountShortcuts(conn, "account_id")
    >>> query.select_all_error_reports()

    :param conn: Connection.
    :type conn: DeepCrawlConnection
    :param account_id: crawl id.
    :type account_id: int or str
    """

    def __init__(self, conn: DeepCrawlConnection, account_id) -> None:
        super().__init__(conn)
        self.query = self.query.getAccount.args(id=account_id)

        self.default_reports_filters = {
            "totalWeight": {
                "lt": 0
            },
            "totalRows": {
                "gt": 0
            }
        }

    def select_all_error_reports(self, projects_filters=None, reports_filters=None):
        """Selects all error reports associated to an account

        :param projects_filters: Filters applied to the projects, defaults to ``{}``
        :type projects_filters: dict
        :param reports_filters: Filters applied to the reports , defaults to ``{"totalWeight": {"lt": 0},"totalRows": {"gt": 0}}``
        :type reports_filters: dict
        """
        projects_filters = projects_filters or {}
        reports_filters = reports_filters or self.default_reports_filters

        (
            self.query
            .select(
                self.ds.Account.id,
                self.ds.Account.rawID
            )
            .select(
                self.ds.Account.projects
                .args(
                    filter=projects_filters,
                    **self.var_first_after_pagination
                )
                .select(
                    self.ds.ProjectConnection.nodes.select(
                        self.ds.Project.id,
                        self.ds.Project.rawID,
                        self.ds.Project.name,
                        self.ds.Project.lastFinishedCrawl
                        .select(
                            self.ds.Crawl.id,
                            self.ds.Crawl.rawID,
                            self.ds.Crawl.finishedAt,
                        )
                        .select(
                            self.ds.Crawl.reports.args(
                                filter=reports_filters
                            ).select(
                                self.ds.ReportConnection.totalCount,
                                self.ds.ReportConnection.nodes.select(
                                    self.ds.Report.reportTemplateCode,
                                    self.ds.Report.reportTemplate.select(
                                        self.ds.ReportTemplate.name
                                    ),
                                    self.ds.Report.totalRows
                                )
                            )
                        )
                    )
                )
                .select(
                    self.ds.ProjectConnection.pageInfo.select(
                        *self.page_fields()
                    )
                )
            )
        )

        return self


def paginate_select_all_error_reports(
        conn: DeepCrawlConnection, account_id, projects_filters=None, reports_filters=None
):
    """Selects all error reports associated to an account

    >>> from deepcrawl_graphql.shortcuts.account_shortcuts import paginate_select_all_error_reports

    >>> paginate_select_all_error_reports(conn, account_id)

    .. dropdown:: Response Example

        .. code-block:: python

            [
                {
                    "account_id": "account_id",
                    "project_id": "project_id",
                    "project_name": "project_name",
                    "crawl_id": "crawl_id",
                    "crawl_finished_at": "2023-12-07T18:42:24.000Z",
                    "report_template_code": "http_pages",
                    "report_template_name": "HTTP Pages",
                    "total_rows": 87
                },
                {
                    "account_id": "account_id",
                    "project_id": "project_id",
                    "project_name": "project_name",
                    "crawl_id": "crawl_id",
                    "crawl_finished_at": "2023-12-07T18:42:24.000Z",
                    "report_template_code": "http_pages",
                    "report_template_name": "HTTP Pages",
                    "total_rows": 1
                }
            ]

    Observations:
        This method includes a warning logger which tells the user if there are more reports than fetched for a crawl.
        If keeping the default filters the logger should not be triggered.

    :param conn: Connection.
    :type conn: DeepCrawlConnection
    :param account_id: crawl id.
    :type account_id: int or str
    :param projects_filters: Filters applied to the projects, defaults to ``{}``
    :type projects_filters: dict
    :param reports_filters: Filters applied to the reports , defaults to ``{"totalWeight": {"lt": 0},"totalRows": {"gt": 0}}``
    :type reports_filters: dict
    """
    query = AccountShortcuts(conn, account_id)
    query.select_all_error_reports(projects_filters, reports_filters)

    projects_has_next_page = True
    end_cursor = ""
    reports = []

    while projects_has_next_page:
        response = conn.run_query(query, after=end_cursor)

        account_id = response.get("getAccount", {}).get("id")

        for project in response.get("getAccount", {}).get("projects", []).get("nodes"):
            crawl = project.get("lastFinishedCrawl", {})
            if not crawl:
                continue

            project_id = project.get("id")
            project_name = project.get("name")

            crawl_id = crawl.get("id")
            crawl_finished_at = crawl.get("finishedAt")

            if crawl.get("reports", {}).get("totalCount") > 1000:
                logger.warning(
                    "Found more than 1000 reports for project_id %s and crawl_id %s",
                    project_id, crawl_id
                )

            for report in crawl.get("reports", {}).get("nodes", []):
                reports.append(
                    {
                        "account_id": account_id,
                        "project_id": project_id,
                        "project_name": project_name,
                        "crawl_id": crawl_id,
                        "crawl_finished_at": crawl_finished_at,
                        "report_template_code": report.get("reportTemplateCode"),
                        "report_template_name": report.get("reportTemplate", {}).get("name"),
                        "total_rows": report.get("totalRows")
                    }
                )

        projects_has_next_page = (
            response
            .get("getAccount", {})
            .get("projects", {})
            .get("pageInfo")
            .get("hasNextPage")
        )
        end_cursor = (
            response.get("getAccount", {})
            .get("projects", {})
            .get("pageInfo")
            .get("endCursor")
        )

    return reports
