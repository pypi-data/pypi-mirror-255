"""
AccountQuery
============
"""

from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.projects.fields import ProjectFields
from deepcrawl_graphql.query import Query

from .fields import AccountFields


class AccountQuery(AccountFields, Query):
    """| AccountQuery class

    Creates an accout query instance.
    The instance will be passed to the run_query method in order to execute the query.

    >>> from deepcrawl_graphql.accounts.account import AccountQuery

    >>> account_query = AccountQuery(conn, "id")
    >>> account_query.select_account()
    >>> account_query.select_settings()
    >>> account_query.select_callback_headers()
    >>> account_query.select_feature_flags()
    >>> account_query.select_locations()
    >>> account_query.select_package()
    >>> account_query.select_subscription()
    >>> account_query.select_projects()
    >>> account_query.select_project("project_id")
    >>> account = conn.run_query(account_query)

    :param conn: Connection.
    :type conn: DeepCrawlConnection
    :param account_id: account id.
    :type account_id: int or str
    """

    def __init__(self, conn: DeepCrawlConnection, account_id) -> None:
        super().__init__(conn)
        self.query = self.query.getAccount.args(id=account_id)

    """
    Account
    """

    def select_account(self, fields=None):
        """Selects account fields.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(*fields or self.fields(self.ds))
        return self

    def select_settings(self, fields=None):
        """Selects account accountSettings.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(self.ds.Account.accountSettings.select(*fields or self.settings_fields(self.ds)))
        return self

    def select_callback_headers(self, fields=None):
        """Selects account apiCallbackHeaders.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(
            self.ds.Account.apiCallbackHeaders.select(*fields or self.api_callback_headers_fields(self.ds))
        )
        return self

    def select_feature_flags(self, fields=None):
        """Selects account featureFlags.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(self.ds.Account.featureFlags.select(*fields or self.feature_flag_fields(self.ds)))
        return self

    def select_locations(self, fields=None):
        """Selects account locations.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(self.ds.Account.locations.select(*fields or self.locations_fields(self.ds)))
        return self

    def select_package(self, fields=None):
        """Selects account primaryAccountPackage.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(self.ds.Account.primaryAccountPackage.select(*fields or self.account_package_fields(self.ds)))
        return self

    def select_subscription(self, include_addons=False, integration_type=None, fields=None):
        """Selects account subscription.

        :param include_addons: If true includes the addons available.
        :type include_addons: bool
        :param integration_type: Selects an addon by integration type
        :type integration_type: str
        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(self.ds.Account.subscription.select(*fields or self.subscription_fields(self.ds)))
        if include_addons:
            self.query.select(
                self.ds.Account.subscription.select(
                    self.ds.AccountSubscription.addons.select(*self.subscription_addons_fields(self.ds))
                )
            )
        if integration_type:
            self.query.select(
                self.ds.Account.subscription.select(
                    self.ds.AccountSubscription.addonByIntegrationType.args(integrationType=integration_type).select(
                        *self.subscription_addons_fields(self.ds)
                    )
                )
            )
        return self

    """
    Project
    """

    def select_projects(self, fields=None):
        """Selects account projects.

        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        projects = self.ds.Account.projects.args(**self.var_pagination, **self.var_ordering)
        projects_nodes = self.ds.ProjectConnection.nodes.select(*fields or ProjectFields.fields(self.ds))
        pagination = self.ds.ProjectConnection.pageInfo.select(*self.page_fields())

        self.query.select(projects.select(projects_nodes).select(pagination))
        return self

    def select_project(self, project_id, fields=None):
        """Selects account project by id.

        :param project_id: Project id.
        :type project_id: bool
        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        self.query.select(self.ds.Account.project.args(id=project_id).select(*fields or ProjectFields.fields(self.ds)))
        return self
