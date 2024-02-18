





DeepCrawl GraphQL Wrapper 1.0.0 documentation




















Welcome to DeepCrawl GraphQL Wrapper’s documentation!¶
======================================================



```
pip install deepcrawl_graphql

```




Authentication¶
===============


To authenticate with the DeepCrawl API you have to first create a connection.





Connection¶
-----------




*class* deepcrawl_graphql.api.DeepCrawlConnection(*user_key_id=None*, *secret=None*, *token=None*)¶

DeepCrawlConnection class

Creates a connection instance used for sending GraphQL queries to DeepCrawl.



```
>>> from deepcrawl_graphql.api import DeepCrawlConnection

```



```
>>> DeepCrawlConnection("user_key_id", "secret")
DeepCrawlConnection instance

```



```
>>> DeepCrawlConnection(token="token")
DeepCrawlConnection instance

```



Parameters:
* **user_key_id** (*int* *or* *str*) – user key, used together with secret for authentication.
* **secret** (*str*) – secret key, used together with user_key_id for authentication.
* **token** (*str*) – authentication token, if used ignores the user_key_id and secret






run_query(*query*, *variables=None*, *var=None*, ***kwargs*)¶
Runs a query.



```
>>> conn = DeepCrawlConnection("user_key_id", "secret")

```


There are 3 possible ways you can run a query


Using a query string. You can use the DeepCrawl explorer to construct the string https://graph-docs.deepcrawl.com/graphql/explorer



```
>>> query = 'query MyQuery {version}'
>>> conn.run_query(query)
{'version': '1.91.1-next.0-en'}

```


Using the gql package to construct a dynamic query.



```
>>> from gql.dsl import DSLQuery
>>> query = DSLQuery(conn.ds.Query.me.select(conn.ds.User.id, conn.ds.User.username))
>>> conn.run_query(query)
{
 'me': {
 'id': 'id',
 'username': 'email@example.com'
 }
}

```



```
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

```


Import a query from the deepcrawl_graphql package and use it’s prebuild queries.



```
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

```



Parameters:
* **query** (*Query* *or* *DSLField* *or* *DSLQuery* *or* *str*) – query object
* **variables** (*dict* *or* *None*) – variables to use in the query.
run_query(… variables={“first”: 1, “after”: “MQ”})
* **var** (*DSLVariableDefinitions*) – gql DSLVariableDefinitions instance to be used in the query.
Works together with variables
* **kwargs** – variables to use in the query.
If variables is not used and the user prefers to send variables as function arguments
run_query(… first=1, after=”MQ”)







get_by_base64_id(*base64_id*, *object_type*, *fields*)¶
Get object by Base64 id



```
>>> conn.get_by_base64_id(
 "TjAxNFJlcG9ydERvd25sb2FkNTk2Njg1MzE",
 "ReportDownload",
 fields=(conn.ds.ReportDownload.id, conn.ds.ReportDownload.fileURL),
 )

```



Parameters:
* **base64_id** (*str*) – Object’s Base64 id
* **object_type** (*str*) – Object’s meta type name
* **fields** (*List**(**DSLField**)*) – Fields to select







run_mutation(*mutation*, *variables=None*, *var=None*, ***kwargs*)¶
Runs a mutation.



```
>>> conn = DeepCrawlConnection("user_key_id", "secret")

```


There are multiple ways you can run a mutation


Import the Mutation class from deepcrawl_graphql package and use it’s prebuild methods.



```
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

```



Parameters:
* **mutation** (*DSLField* *or* *DSLMutation* *or* *str*) – mutation object
* **variables** (*dict* *or* *None*) – variables to use in the query.
run_query(… variables={“input”: {“name”: “name”, …}})
* **var** (*DSLVariableDefinitions*) – gql DSLVariableDefinitions instance to be used in the query.
Works tougether with variables
* **kwargs** – variables to use in the query.
If variables is not used and the user prefers to send variables as function arguments
run_query(… input={“name”: “name”, …})









Special Arguments¶
==================




Pagination¶
-----------


There are some optional arguments which can be used while running the query: first, last, after, before


* first - Number of records to fetch from start
* last - Number of records to fetch from end
* after - Fetch after cursor
* before - Fetch before cursor



```
>>> conn = DeepCrawlConnection("user_key_id", "secret")

```


By default first 100 or less objects are retrieved



```
>>> account_query = AccountQuery(conn, "74910")
>>> account_query.select_projects()
>>> conn.run_query(account_query)

```



```
{
    "getAccount": {
        "projects": {
            "nodes": [
                {"id": "id-1", "name": "name-1", ...},
                {"id": "id-2", "name": "name-2", ...},
                {"id": "id-3", "name": "name-3", ...},
                {"id": "id-4", "name": "name-4", ...},
            ],
            "pageInfo": {
                "startCursor": "MQ",
                "endCursor": "NA",
                "hasNextPage": False,
                "hasPreviousPage": False
            }
        }
    }
}

```


By using the **first** argument you can choose how many object to retrieve per page.



```
>>> conn.run_query(account_query, variables={"first": 2})
OR
>>> conn.run_query(account_query, first=2)

```



```
{
    "me": {
        "accounts": {
            "nodes": [
                {"id": "id-1", "name": "name-1", ...},
                {"id": "id-2", "name": "name-2", ...},
            ],
            "pageInfo": {
                "startCursor": "MQ",
                "endCursor": "Mg",
                "hasNextPage": True,
                "hasPreviousPage": False
            }
        }
    }
}

```


By using the **first** argument combined with the **after** argument you can choose how many object to retrieve per page after the selected cursor.



```
>>> conn.run_query(account_query, variables={"first": 2, "after": "Mg"})
OR
>>> conn.run_query(account_query, first=2, after="Mg")

```



```
{
    "me": {
        "accounts": {
            "nodes": [
                {"id": "id-3", "name": "name-3", ...},
                {"id": "id-4", "name": "name-4", ...},
            ],
            "pageInfo": {
                "startCursor": "Mw",
                "endCursor": "NA",
                "hasNextPage": False,
                "hasPreviousPage": True
            }
        }
    }
}

```


By using the **first** argument combined with the **before** argument you can choose how many object to retrieve per page before the selected cursor.



```
>>> conn.run_query(account_query, variables={"first": 2, "before": "Mg"})
OR
>>> conn.run_query(account_query, first=2, before="Mg")

```



```
{
    "me": {
        "accounts": {
            "nodes": [
                {"id": "id-1", "name": "name-1", ...},
                {"id": "id-2", "name": "name-2", ...},
            ],
            "pageInfo": {
                "startCursor": "MQ",
                "endCursor": "Mg",
                "hasNextPage": True,
                "hasPreviousPage": False
            }
        }
    }
}

```




Ordering¶
---------


There is an optional argument which can be used while running the query: order_by


The order argument can be used to sort the dataset.


It accepts a dictionary with two keys: direction (ASC or DESC) and a field (to sort against)



```
>>> conn = DeepCrawlConnection("user_key_id", "secret")

```



```
>>> account_query = AccountQuery(conn, "74910")
>>> account_query.select_projects()

```


Default result:



```
>>> conn.run_query(account_query)

```



```
{
    "getAccount": {
        "projects": {
            "nodes": [
                {"id": "id-1", "name": "name-1", ...},
                {"id": "id-2", "name": "name-2", ...},
                {"id": "id-3", "name": "name-3", ...},
                {"id": "id-4", "name": "name-4", ...},
            ],
            "pageInfo": {
                "startCursor": "MQ",
                "endCursor": "NA",
                "hasNextPage": False,
                "hasPreviousPage": False
            }
        }
    }
}

```


Using order_by result:



```
>>> conn.run_query(account_query, order_by={"direction": "DESC", "field": "id"})

```



```
{
    "getAccount": {
        "projects": {
            "nodes": [
                {"id": "id-4", "name": "name-4", ...},
                {"id": "id-3", "name": "name-3", ...},
                {"id": "id-2", "name": "name-2", ...},
                {"id": "id-1", "name": "name-1", ...},
            ],
            "pageInfo": {
                "startCursor": "MQ",
                "endCursor": "NA",
                "hasNextPage": False,
                "hasPreviousPage": False
            }
        }
    }
}

```




Select Specific Fields¶
-----------------------


In some cases, you may not need all the returned fields. Maybe you are interested only in a list of project ids and names.


For this kind of scenario, you can use the fields argument implemented for all the select methods.



```
>>> conn = DeepCrawlConnection("user_key_id", "secret")
>>> account_query = AccountQuery(conn, "74910")
>>> account_query.select_projects(fields=(conn.ds.Project.id, conn.ds.Project.name))
>>> conn.run_query(account_query)

```



```
{
    "getAccount": {
        "projects": {
            "nodes": [
                {"id": "id-1", "name": "name-1"},
                {"id": "id-2", "name": "name-2"},
            ],
            "pageInfo": {
                "startCursor": "MQ",
                "endCursor": "NA",
                "hasNextPage": False,
                "hasPreviousPage": False
            }
        }
    }
}

```


Although this is very useful you have to have a pretty good understanding of the schema for using this feature.






Me¶
===




MeQuery¶
--------




*class* deepcrawl_graphql.me.me.MeQuery(*conn: DeepCrawlConnection*)¶

MeQuery class

Creates a me query instance. “Me” being the authenticated user.
The instance will be passed to the run_query method in order to execute the query.



```
>>> from deepcrawl_graphql.me.me import MeQuery

```



```
>>> me_query = MeQuery(conn)
>>> me_query.select_me()
>>> me_query.select_accounts()
>>> me = conn.run_query(me_query)

```



Parameters:
**conn** (*DeepCrawlConnection*) – Connection.






select_me(*fields=None*)¶
Selects user fields.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_accounts(*fields=None*)¶
Selects users accounts.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.










Accounts¶
=========




AccountQuery¶
-------------




*class* deepcrawl_graphql.accounts.account.AccountQuery(*conn: DeepCrawlConnection*, *account_id*)¶

AccountQuery class

Creates an accout query instance.
The instance will be passed to the run_query method in order to execute the query.



```
>>> from deepcrawl_graphql.accounts.account import AccountQuery

```



```
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

```



Parameters:
* **conn** (*DeepCrawlConnection*) – Connection.
* **account_id** (*int* *or* *str*) – account id.






select_account(*fields=None*)¶
Selects account fields.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_settings(*fields=None*)¶
Selects account accountSettings.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_callback_headers(*fields=None*)¶
Selects account apiCallbackHeaders.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_feature_flags(*fields=None*)¶
Selects account featureFlags.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_locations(*fields=None*)¶
Selects account locations.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_package(*fields=None*)¶
Selects account primaryAccountPackage.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_subscription(*include_addons=False*, *integration_type=None*, *fields=None*)¶
Selects account subscription.



Parameters:
* **include_addons** (*bool*) – If true includes the addons available.
* **integration_type** (*str*) – Selects an addon by integration type
* **fields** (*List**(**DSLField**)*) – Select specific fields.







select_projects(*fields=None*)¶
Selects account projects.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_project(*project_id*, *fields=None*)¶
Selects account project by id.



Parameters:
* **project_id** (*bool*) – Project id.
* **fields** (*List**(**DSLField**)*) – Select specific fields.










Projects¶
=========




ProjectQuery¶
-------------




*class* deepcrawl_graphql.projects.project.ProjectQuery(*conn: DeepCrawlConnection*, *project_id*)¶

ProjectQuery class

Creates a project query instance.
The instance will be passed to the run_query method in order to execute the query.



```
>>> from deepcrawl_graphql.projects.project import ProjectQuery

```



```
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

```



Parameters:
* **conn** (*DeepCrawlConnection*) – Connection.
* **project_id** (*int* *or* *str*) – project id.






select_project(*fields=None*)¶
Selects project fields.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_sitemaps(*fields=None*)¶
Selects project sitemaps.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_advanced_crawl_rate(*fields=None*)¶
Selects project maximumCrawlRateAdvanced.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_majestic_configuration(*fields=None*)¶
Selects project majesticConfiguration.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_location(*fields=None*)¶
Selects project location.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_last_finished_crawl(*fields=None*)¶
Selects project lastFinishedCrawl.


Not implemented yet.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_google_search_configuration(*fields=None*)¶
Selects project googleSearchConsoleConfiguration.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_google_analytics_project_view(*fields=None*)¶
Selects project googleAnalyticsProjectView.


Not implemented yet.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_custom_extraction_settings(*fields=None*)¶
Selects project customExtractions.





select_account(*fields=None*)¶
Selects project account.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_crawls(*fields=None*)¶
Selects project crawls.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_schedule(*fields=None*)¶
Selects project Schedule.








Crawls¶
=======




CrawlQuery¶
-----------




*class* deepcrawl_graphql.crawls.crawl.CrawlQuery(*conn: DeepCrawlConnection*, *crawl_id*)¶

CrawlQuery class

Creates a crawl query instance.
The instance will be passed to the run_query method in order to execute the query.



```
>>> from deepcrawl_graphql.crawls.crawl import CrawlQuery

```



```
>>> crawl_query = CrawlQuery(conn, "crawl_id")
>>> crawl_query.select_crawl()
>>> crawl_query.select_parquet_files("datasource_name")
>>> crawl_query.select_compared_to()
>>> crawl = conn.run_query(crawl_query)

```



Parameters:
* **conn** (*DeepCrawlConnection*) – Connection.
* **crawl_id** (*int* *or* *str*) – crawl id.






select_crawl(*fields=None*)¶
Selects crawl fields.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_parquet_files(*datasource_name*, *fields=None*)¶
Selects crawl parquetFiles.



Parameters:
* **datasource_name** (*str*) – Datasource name.
* **fields** (*List**(**DSLField**)*) – Select specific fields.







select_crawl_type_counts(*crawl_types*, *segment_id=None*, *fields=None*)¶
Selects crawl fields.


Not implemented yet.



Parameters:
* **crawl_types** (*str*) – Crawl type.
* **segment_id** (*int* *or* *str*) – Segment id.
* **fields** (*List**(**DSLField**)*) – Select specific fields.







select_crawl_settings(*fields=None*)¶
Selects crawl crawlSetting.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_compared_to(*fields=None*)¶
Selects crawl comparedTo.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_reports(*fields=None*)¶
Selects crawl reports.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_report_downloads(*fields=None*)¶
Selects reports downloads.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.










Reports¶
========




ReportQuery¶
------------




*class* deepcrawl_graphql.reports.report.ReportQuery(*conn: DeepCrawlConnection*, *crawl_id*, *report_tamplate_code*, *report_type_code*, *segment_id=None*)¶

ReportQuery class

Creates a report query instance.
The instance will be passed to the run_query method in order to execute the query.



```
>>> from deepcrawl_graphql.reports.report import ReportQuery

```



```
>>> report_query = ReportQuery(conn, "crawl_id", "report_tamplate_code", "report_type_code")
>>> report_query.select_report()
>>> report_query.select_datasource()
>>> report_query.select_type()
>>> report_query.select_trend()
>>> report_query.select_segment()
>>> report_query.select_report_template()
>>> conn.run_query(report_query)

```



Parameters:
* **conn** (*DeepCrawlConnection*) – Connection.
* **crawl_id** (*int* *or* *str*) – crawl id.
* **report_tamplate_code** (*str*) – report template code.
* **report_type_code** (*str*) – report type code.
* **segment_id** (*int* *or* *str*) – segment id.






select_report(*fields=None*)¶
Selects report fields.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_raw_trends(*fields=None*)¶
Selects report rawTrends.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_datasource(*fields=None*)¶
Selects report datasources.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_type(*fields=None*)¶
Selects report type.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_trend(*fields=None*)¶
Selects report trend.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_segment(*fields=None*)¶
Selects report segment.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_report_template(*fields=None*)¶
Selects report reportTemplate.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.







select_report_downloads(*fields=None*)¶
Selects report reportDownloads.



Parameters:
**fields** (*List**(**DSLField**)*) – Select specific fields.










Mutations¶
==========




Mutations¶
----------




*class* deepcrawl_graphql.mutations.Mutation(*conn: DeepCrawlConnection*)¶
Mutation class




cancel_crawling(*crawl_id*, *fields=None*)¶
Cancel a running Crawl



Parameters:
* **crawl_id** (*int* *or* *str*) – Crawl id
* **fields** (*List**(**DSLField**)*) – Select specific fields.







create_accessibility_project(*project_input*, *fields=None*)¶
Creates an Accessibility Project




GraphQL Input Example




It has to be converted to dict



```
input CreateAccessibilityProjectInput {
  accountId: ObjectID!
  alertEmails: [String!]
  alertSettingCode: AlertSettingCode!
  apiCallbackHeaders: [APICallbackHeaderInput!]!
  apiCallbackUrl: String
  autoFinalizeOnCrawlLimits: Boolean!
  compareToCrawl: CompareToCrawlType!
  crawlDisallowedUrls1stLevel: Boolean!
  crawlHyperlinksExternal: Boolean!
  crawlHyperlinksInternal: Boolean!
  crawlImagesExternal: Boolean!
  crawlImagesInternal: Boolean!
  crawlNofollowHyperlinks: Boolean!
  crawlNonHtml: Boolean!
  crawlNotIncluded1stLevel: Boolean!
  crawlRedirectsExternal: Boolean!
  crawlRedirectsInternal: Boolean!
  crawlRelAmphtmlExternal: Boolean!
  crawlRelAmphtmlInternal: Boolean!
  crawlRelCanonicalsExternal: Boolean!
  crawlRelCanonicalsInternal: Boolean!
  crawlRelHreflangsExternal: Boolean!
  crawlRelHreflangsInternal: Boolean!
  crawlRelMobileExternal: Boolean!
  crawlRelMobileInternal: Boolean!
  crawlRelNextPrevExternal: Boolean!
  crawlRelNextPrevInternal: Boolean!
  crawlRobotsTxtNoindex: Boolean!
  crawlScriptsExternal: Boolean!
  crawlScriptsInternal: Boolean!
  crawlStylesheetsExternal: Boolean!
  crawlStylesheetsInternal: Boolean!
  crawlTestSite: Boolean!
  crawlTypes: [CrawlType!]!
  customDns: [CustomDnsSettingInput!]!
  customExtractions: [CustomExtractionSettingInput!]!
  customRequestHeaders: [CustomRequestHeaderInput!]!
  dataLayerName: String
  dataOnlyCrawlTypes: [CrawlType!]
  discoverSitemapsInRobotsTxt: Boolean!
  duplicatePrecision: Float!
  emptyPageThreshold: Int!
  excludeUrlPatterns: [String!]!
  flattenShadowDom: Boolean!
  gaDateRange: Int!
  ignoreInvalidSSLCertificate: Boolean!
  includeHttpAndHttps: Boolean!
  includeSubdomains: Boolean!
  includeUrlPatterns: [String!]!
  industryCode: String
  limitLevelsMax: Int
  limitUrlsMax: Int
  locationCode: LocationCode!
  logSummaryRequestsHigh: Int!
  logSummaryRequestsLow: Int!
  maxBodyContentLength: Int!
  maxDescriptionLength: Int!
  maxFollowedExternalLinks: Int!
  maxHtmlSize: Int!
  maxLinks: Int!
  maxLoadTime: Float!
  maxRedirections: Int!
  maxTitleWidth: Int!
  maxUrlLength: Int!
  maximumCrawlRate: Float!
  maximumCrawlRateAdvanced: [AdvancedCrawlRateInput!]!
  minDescriptionLength: Int!
  minTitleLength: Int!
  minVisits: Int!
  mobileHomepageUrl: String
  mobileUrlPattern: String
  mobileUserAgentCode: String!
  name: String!
  primaryDomain: String!
  renderTimeout: Int
  rendererBlockAds: Boolean!
  rendererBlockAnalytics: Boolean!
  rendererBlockCustom: [String!]!
  rendererCookies: [RendererCookieInput!]!
  rendererJsString: String
  rendererJsUrls: [String!]!
  renderingRobotsCheckMode: RenderingRobotsCheckMode!
  robotsOverwrite: String
  secondaryDomains: [String!]!
  startUrls: [String!]!
  storeHtml: Boolean!
  targetMaxUncrawledUrlsCount: Int!
  testSiteDomain: String
  testSitePassword: String
  testSiteUsername: String
  thinPageThreshold: Int!
  urlRewriteQueryParameters: [String!]!
  urlRewriteRules: [UrlRewriteRuleInput!]!
  urlRewriteStripFragment: Boolean!
  urlSampling: [UrlSamplingInput!]!
  useMobileSettings: Boolean!
  useRobotsOverwrite: Boolean!
  useStealthMode: Boolean!
  useUrlRewriteRules: Boolean!
  userAgentCode: String!
  userAgentString: String
  userAgentStringMobile: String
  userAgentToken: String
  userAgentTokenMobile: String
}

```




Parameters:
* **project_input** (*dict*) – Project input
* **fields** (*List**(**DSLField**)*) – Select specific fields







create_project(*project_input*, *fields=None*)¶
Creates a Project




GraphQL Input Example




It has to be converted to dict



```
input CreateProjectInput {
  accountId: ObjectID!
  alertEmails: [String!]
  alertSettingCode: AlertSettingCode!
  apiCallbackHeaders: [APICallbackHeaderInput!]!
  apiCallbackUrl: String
  autoFinalizeOnCrawlLimits: Boolean!
  compareToCrawl: CompareToCrawlType!
  crawlDisallowedUrls1stLevel: Boolean!
  crawlHyperlinksExternal: Boolean!
  crawlHyperlinksInternal: Boolean!
  crawlImagesExternal: Boolean!
  crawlImagesInternal: Boolean!
  crawlNofollowHyperlinks: Boolean!
  crawlNonHtml: Boolean!
  crawlNotIncluded1stLevel: Boolean!
  crawlRedirectsExternal: Boolean!
  crawlRedirectsInternal: Boolean!
  crawlRelAmphtmlExternal: Boolean!
  crawlRelAmphtmlInternal: Boolean!
  crawlRelCanonicalsExternal: Boolean!
  crawlRelCanonicalsInternal: Boolean!
  crawlRelHreflangsExternal: Boolean!
  crawlRelHreflangsInternal: Boolean!
  crawlRelMobileExternal: Boolean!
  crawlRelMobileInternal: Boolean!
  crawlRelNextPrevExternal: Boolean!
  crawlRelNextPrevInternal: Boolean!
  crawlRobotsTxtNoindex: Boolean!
  crawlScriptsExternal: Boolean!
  crawlScriptsInternal: Boolean!
  crawlStylesheetsExternal: Boolean!
  crawlStylesheetsInternal: Boolean!
  crawlTestSite: Boolean!
  crawlTypes: [CrawlType!]!
  customDns: [CustomDnsSettingInput!]!
  customExtractions: [CustomExtractionSettingInput!]!
  customRequestHeaders: [CustomRequestHeaderInput!]!
  dataLayerName: String
  dataOnlyCrawlTypes: [CrawlType!]
  discoverSitemapsInRobotsTxt: Boolean!
  duplicatePrecision: Float!
  emptyPageThreshold: Int!
  excludeUrlPatterns: [String!]!
  flattenShadowDom: Boolean!
  gaDateRange: Int!
  ignoreInvalidSSLCertificate: Boolean!
  includeHttpAndHttps: Boolean!
  includeSubdomains: Boolean!
  includeUrlPatterns: [String!]!
  industryCode: String
  limitLevelsMax: Int
  limitUrlsMax: Int
  locationCode: LocationCode!
  logSummaryRequestsHigh: Int!
  logSummaryRequestsLow: Int!
  maxBodyContentLength: Int!
  maxDescriptionLength: Int!
  maxFollowedExternalLinks: Int!
  maxHtmlSize: Int!
  maxLinks: Int!
  maxLoadTime: Float!
  maxRedirections: Int!
  maxTitleWidth: Int!
  maxUrlLength: Int!
  maximumCrawlRate: Float!
  maximumCrawlRateAdvanced: [AdvancedCrawlRateInput!]!
  minDescriptionLength: Int!
  minTitleLength: Int!
  minVisits: Int!
  mobileHomepageUrl: String
  mobileUrlPattern: String
  mobileUserAgentCode: String!
  name: String!
  primaryDomain: String!
  renderTimeout: Int
  rendererBlockAds: Boolean!
  rendererBlockAnalytics: Boolean!
  rendererBlockCustom: [String!]!
  rendererCookies: [RendererCookieInput!]!
  rendererJsString: String
  rendererJsUrls: [String!]!
  renderingRobotsCheckMode: RenderingRobotsCheckMode!
  robotsOverwrite: String
  secondaryDomains: [String!]!
  startUrls: [String!]!
  targetMaxUncrawledUrlsCount: Int!
  testSiteDomain: String
  testSitePassword: String
  testSiteUsername: String
  thinPageThreshold: Int!
  urlRewriteQueryParameters: [String!]!
  urlRewriteRules: [UrlRewriteRuleInput!]!
  urlRewriteStripFragment: Boolean!
  urlSampling: [UrlSamplingInput!]!
  useMobileSettings: Boolean!
  useRenderer: Boolean!
  useRobotsOverwrite: Boolean!
  useStealthMode: Boolean!
  useUrlRewriteRules: Boolean!
  userAgentCode: String!
  userAgentString: String
  userAgentStringMobile: String
  userAgentToken: String
  userAgentTokenMobile: String
}

```




Parameters:
* **project_input** (*dict*) – Project input
* **fields** (*List**(**DSLField**)*) – Select specific fields







create_report_download(*report_download_input*, *fields=None*)¶
Creates a report download.




GraphQL Input Example




It has to be converted to dict



```
input CreateReportDownloadInput {
  crawlDuplicateUrlFilter: CrawlDuplicateUrlConnectionFilterInput
  crawlHreflangsFilter: CrawlHreflangsConnectionFilterInput
  crawlId: ObjectID
  crawlLinkFilter: CrawlLinkConnectionFilterInput
  crawlLinkedDomainFilter: CrawlLinkedDomainConnectionFilterInput
  crawlSitemapFilter: CrawlSitemapConnectionFilterInput
  crawlUncrawledUrlFilter: CrawlUncrawledUrlConnectionFilterInput
  crawlUniqueLinkFilter: CrawlUniqueLinkConnectionFilterInput
  crawlUrlFilter: CrawlUrlConnectionFilterInput
  crawlWebCrawlDepthFilter: CrawlWebCrawlDepthConnectionFilterInput
  fileName: String
  filter: JSONObject
  outputType: ReportDownloadOutputType! = CsvZip
  reportId: ObjectID
  reportTemplateCode: String
  reportTypeCode: ReportTypeCode
  segmentId: ObjectID
  selectedMetrics: [String!]
}

```




Parameters:
* **report_download_input** (*dict*) – Report Download input.
* **fields** (*List**(**DSLField**)*) – Select specific fields.







create_schedule(*schedule_input*, *fields=None*)¶
Creates a Schedule




GraphQL Input Example




It has to be converted to dict



```
input CreateScheduleInput {
  nextRunTime: DateTime!
  projectId: ObjectID!
  scheduleFrequency: ScheduleFrequencyCode!
}

```




Parameters:
* **schedule_input** (*dict*) – CreateScheduleInput
* **fields** (*List**(**DSLField**)*) – Select specific fields







delete_crawl(*crawl_id*, *fields=None*)¶
Deletes a Crawl



Parameters:
* **crawl_id** (*int* *or* *str*) – Crawl id
* **fields** (*List**(**DSLField**)*) – Select specific fields.







delete_project(*project_id*, *fields=None*)¶
Deletes a Project



Parameters:
* **project_id** (*int* *or* *str*) – Project id
* **fields** (*List**(**DSLField**)*) – Select specific fields







delete_report_download(*report_download_id*, *fields=None*)¶
Deletes a report download.



Parameters:
* **report_download_id** (*int* *or* *str*) – Report Download id.
* **fields** (*List**(**DSLField**)*) – Select specific fields.







delete_schedule(*schedule_input*, *fields=None*)¶
Deletes a Schedule




GraphQL Input Example




It has to be converted to dict



```
input DeleteScheduleInput {
  scheduleId: ObjectID!
}

```




Parameters:
* **schedule_input** (*dict*) – DeleteScheduleInput
* **fields** (*List**(**DSLField**)*) – Select specific fields







pause_crawling(*crawl_id*, *fields=None*)¶
Pause a running Crawl



Parameters:
* **crawl_id** (*int* *or* *str*) – Crawl id
* **fields** (*List**(**DSLField**)*) – Select specific fields.







resume_crawling(*crawl_id*, *fields=None*)¶
Resume a Crawl



Parameters:
* **crawl_id** (*int* *or* *str*) – Crawl id
* **fields** (*List**(**DSLField**)*) – Select specific fields.







run_crawl_for_project(*project_id*, *fields=None*)¶
Run a Crawl for a Project



Parameters:
* **project_id** (*int* *or* *str*) – Project id
* **fields** (*List**(**DSLField**)*) – Select specific fields.







unarchive_crawl(*crawl_id*, *fields=None*)¶
Unarchive a Crawl



Parameters:
* **crawl_id** (*int* *or* *str*) – Crawl id
* **fields** (*List**(**DSLField**)*) – Select specific fields.







update_account(*account_input*, *fields=None*)¶
Update Account.




GraphQL Input Example




It has to be converted to dict



```
input UpdateAccountInput {
    accountId: ObjectID!
    apiCallbackHeaders: [APICallbackHeaderInput!]
    apiCallbackUrl: String
    country: String
    customLogo: Upload
    customProxy: String
}

```




Parameters:
* **account_input** (*dict*) – Account input
* **fields** (*List**(**DSLField**)*) – Select specific fields.







update_majestic_configuration(*majestic_configuration_input*, *fields=None*)¶
Updates a MajesticConfiguration




GraphQL Input Example




It has to be converted to dict



```
input UpdateMajesticConfigurationInput {
  enabled: Boolean
  maxRows: Int
  projectId: ObjectID!
  useHistoricData: Boolean
  useRootDomain: Boolean
}

```




Parameters:
* **majestic_configuration_input** (*dict*) – MajesticConfigurationInput
* **fields** (*List**(**DSLField**)*) – Select specific fields







update_project(*project_input*, *fields=None*)¶
Updates a Project




GraphQL Input Example




It has to be converted to dict



```
input UpdateProjectInput {
  alertEmails: [String!]
  alertSettingCode: AlertSettingCode
  apiCallbackHeaders: [APICallbackHeaderInput!]
  apiCallbackUrl: String
  autoFinalizeOnCrawlLimits: Boolean
  compareToCrawl: CompareToCrawl
  crawlDisallowedUrls1stLevel: Boolean
  crawlHyperlinksExternal: Boolean
  crawlHyperlinksInternal: Boolean
  crawlImagesExternal: Boolean
  crawlImagesInternal: Boolean
  crawlNofollowHyperlinks: Boolean
  crawlNonHtml: Boolean
  crawlNotIncluded1stLevel: Boolean
  crawlRedirectsExternal: Boolean
  crawlRedirectsInternal: Boolean
  crawlRelAmphtmlExternal: Boolean
  crawlRelAmphtmlInternal: Boolean
  crawlRelCanonicalsExternal: Boolean
  crawlRelCanonicalsInternal: Boolean
  crawlRelHreflangsExternal: Boolean
  crawlRelHreflangsInternal: Boolean
  crawlRelMobileExternal: Boolean
  crawlRelMobileInternal: Boolean
  crawlRelNextPrevExternal: Boolean
  crawlRelNextPrevInternal: Boolean
  crawlRobotsTxtNoindex: Boolean
  crawlScriptsExternal: Boolean
  crawlScriptsInternal: Boolean
  crawlStylesheetsExternal: Boolean
  crawlStylesheetsInternal: Boolean
  crawlTestSite: Boolean
  crawlTypes: [CrawlType!]
  customDns: [CustomDnsSettingInput!]
  customExtractions: [CustomExtractionSettingInput!]
  customRequestHeaders: [CustomRequestHeaderInput!]
  dataLayerName: String
  dataOnlyCrawlTypes: [CrawlType!]
  discoverSitemapsInRobotsTxt: Boolean
  duplicatePrecision: Float
  emptyPageThreshold: Int
  excludeUrlPatterns: [String!]
  flattenShadowDom: Boolean
  gaDateRange: Int
  ignoreInvalidSSLCertificate: Boolean
  includeHttpAndHttps: Boolean
  includeSubdomains: Boolean
  includeUrlPatterns: [String!]
  industryCode: String
  limitLevelsMax: Int
  limitUrlsMax: Int
  locationCode: LocationCode
  logSummaryRequestsHigh: Int
  logSummaryRequestsLow: Int
  maxBodyContentLength: Int
  maxDescriptionLength: Int
  maxFollowedExternalLinks: Int
  maxHtmlSize: Int
  maxLinks: Int
  maxLoadTime: Float
  maxRedirections: Int
  maxTitleWidth: Int
  maxUrlLength: Int
  maximumCrawlRate: Float
  maximumCrawlRateAdvanced: [AdvancedCrawlRateInput!]
  minDescriptionLength: Int
  minTitleLength: Int
  minVisits: Int
  mobileHomepageUrl: String
  mobileUrlPattern: String
  mobileUserAgentCode: String
  name: String
  primaryDomain: String
  projectId: ObjectID!
  renderTimeout: Int
  rendererBlockAds: Boolean
  rendererBlockAnalytics: Boolean
  rendererBlockCustom: [String!]
  rendererCookies: [RendererCookieInput!]
  rendererJsString: String
  rendererJsUrls: [String!]
  renderingRobotsCheckMode: RenderingRobotsCheckMode
  robotsOverwrite: String
  secondaryDomains: [String!]
  startUrls: [String!]
  targetMaxUncrawledUrlsCount: Int
  testSiteDomain: String
  testSitePassword: String
  testSiteUsername: String
  thinPageThreshold: Int
  urlRewriteQueryParameters: [String!]
  urlRewriteRules: [UrlRewriteRuleInput!]
  urlRewriteStripFragment: Boolean
  urlSampling: [UrlSamplingInput!]
  useMobileSettings: Boolean
  useRenderer: Boolean
  useRobotsOverwrite: Boolean
  useStealthMode: Boolean
  useUrlRewriteRules: Boolean
  userAgentCode: String
  userAgentString: String
  userAgentStringMobile: String
  userAgentToken: String
  userAgentTokenMobile: String
}

```




Parameters:
* **project_input** (*dict*) – Project input
* **fields** (*List**(**DSLField**)*) – Select specific fields







update_schedule(*schedule_input*, *fields=None*)¶
Updates a Schedule




GraphQL Input Example




It has to be converted to dict



```
input UpdateScheduleInput {
  scheduleId: ObjectID!
  nextRunTime: DateTime
  scheduleFrequency: ScheduleFrequencyCode
}

```




Parameters:
* **schedule_input** (*dict*) – UpdateScheduleInput
* **fields** (*List**(**DSLField**)*) – Select specific fields










Shortcuts¶
==========




Shortcuts¶
----------




*class* deepcrawl_graphql.shortcuts.crawl_shortcuts.CrawlShortcuts(*conn: DeepCrawlConnection*, *crawl_id*)¶

Shortcuts class

Creates a shortcuts query instance
The instance will be passed to the run_query method in order to execute the query.



```
>>> from deepcrawl_graphql.shortcuts.crawl_shortcuts import CrawlShortcuts

```



```
>>> query = CrawlShortcuts(conn, "crawl_id")
>>> crawl_query.select_explorer_data("path1", report_filters)

```



Parameters:
* **conn** (*DeepCrawlConnection*) – Connection.
* **crawl_id** (*int* *or* *str*) – crawl id.






select_explorer_data(*path*, *report_filters*, *agregate_filters=None*, *paginate=True*)¶
Select Explorer data



Parameters:
* **path** (*str*) – Path. One of the paths from one to 9 e.g. path1
* **report_filters** (*dict*) – Report filters. reportTemplateCode and reportTypeCode are mandatory
* **agregate_filters** (*dict*) – Filters applied to the aggregation.
* **paginate** (*bool*) – Include pagination or not.










Indices and tables¶
===================


* Index
* Module Index
* Search Page








DeepCrawl GraphQL Wrapper
=========================


### Navigation


* Pagination
* Ordering
* Select Specific Fields


* MeQuery


* AccountQuery


* ProjectQuery


* CrawlQuery


* ReportQuery


* Mutations


* Shortcuts



### Related Topics


* Documentation overview








 ©2022, Andrei Mutu.
 
 |
 Powered by Sphinx 5.0.2
 & Alabaster 0.7.13


