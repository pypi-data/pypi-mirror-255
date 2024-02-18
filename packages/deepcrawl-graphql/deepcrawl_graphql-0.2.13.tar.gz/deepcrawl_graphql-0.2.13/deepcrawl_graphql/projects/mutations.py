from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.projects.fields import ProjectFields


class ProjectMutation:
    def __init__(self, conn: DeepCrawlConnection) -> None:
        self.conn = conn
        self.ds = conn.ds
        self.mutation = self.ds.Mutation

    def create_project(self, project_input, fields=None):
        """Creates a Project

        .. dropdown:: GraphQL Input Example

            It has to be converted to dict

            .. code-block::

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

        :param project_input: Project input
        :type project_input: dict
        :param fields: Select specific fields
        :type fields: List(DSLField)
        """
        mutation = self.mutation.createProject.args(input=project_input).select(
            self.ds.CreateProjectPayload.project.select(*fields or ProjectFields.fields(self.ds))
        )
        return self.conn.run_mutation(mutation)

    def update_project(self, project_input, fields=None):
        """Updates a Project

        .. dropdown:: GraphQL Input Example

            It has to be converted to dict

            .. code-block::

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

        :param project_input: Project input
        :type project_input: dict
        :param fields: Select specific fields
        :type fields: List(DSLField)
        """
        mutation = self.mutation.updateProject.args(input=project_input).select(
            self.ds.UpdateProjectPayload.project.select(*fields or ProjectFields.fields(self.ds))
        )
        return self.conn.run_mutation(mutation)

    def create_accessibility_project(self, project_input, fields=None):
        """Creates an Accessibility Project

        .. dropdown:: GraphQL Input Example

            It has to be converted to dict

            .. code-block::

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

        :param project_input: Project input
        :type project_input: dict
        :param fields: Select specific fields
        :type fields: List(DSLField)
        """
        mutation = self.mutation.createAccessibilityProject.args(input=project_input).select(
            self.ds.CreateProjectPayload.project.select(*fields or ProjectFields.fields(self.ds))
        )
        return self.conn.run_mutation(mutation)

    def delete_project(self, project_id, fields=None):
        """Deletes a Project

        :param project_id: Project id
        :type project_id: int or str
        :param fields: Select specific fields
        :type fields: List(DSLField)
        """
        mutation = self.mutation.deleteProject.args(projectId=project_id).select(
            self.ds.DeleteProjectPayload.project.select(*fields or ProjectFields.fields(self.ds))
        )
        return self.conn.run_mutation(mutation)

    def update_majestic_configuration(self, majestic_configuration_input, fields=None):
        """Updates a MajesticConfiguration

        .. dropdown:: GraphQL Input Example

            It has to be converted to dict

            .. code-block::

                input UpdateMajesticConfigurationInput {
                  enabled: Boolean
                  maxRows: Int
                  projectId: ObjectID!
                  useHistoricData: Boolean
                  useRootDomain: Boolean
                }

        :param majestic_configuration_input: MajesticConfigurationInput
        :type majestic_configuration_input: dict
        :param fields: Select specific fields
        :type fields: List(DSLField)
        """
        mutation = self.mutation.updateMajesticConfiguration.args(input=majestic_configuration_input).select(
            self.ds.UpdateMajesticConfigurationPayload.majesticConfiguration.select(
                *fields or ProjectFields.majestic_configuration_fields(self.ds)
            )
        )
        return self.conn.run_mutation(mutation)

    """
    Schedules
    """

    def create_schedule(self, schedule_input, fields=None):
        """Creates a Schedule

        .. dropdown:: GraphQL Input Example

            It has to be converted to dict

            .. code-block::

                input CreateScheduleInput {
                  nextRunTime: DateTime!
                  projectId: ObjectID!
                  scheduleFrequency: ScheduleFrequencyCode!
                }

        :param schedule_input: CreateScheduleInput
        :type schedule_input: dict
        :param fields: Select specific fields
        :type fields: List(DSLField)
        """
        mutation = self.mutation.createSchedule.args(input=schedule_input).select(
            self.ds.CreateSchedulePayload.schedule.select(
                *fields or ProjectFields.schedule_fields(self.ds)
            )
        )
        return self.conn.run_mutation(mutation)

    def update_schedule(self, schedule_input, fields=None):
        """Updates a Schedule

        .. dropdown:: GraphQL Input Example

            It has to be converted to dict

            .. code-block::

                input UpdateScheduleInput {
                  scheduleId: ObjectID!
                  nextRunTime: DateTime
                  scheduleFrequency: ScheduleFrequencyCode
                }

        :param schedule_input: UpdateScheduleInput
        :type schedule_input: dict
        :param fields: Select specific fields
        :type fields: List(DSLField)
        """
        mutation = self.mutation.updateSchedule.args(input=schedule_input).select(
            self.ds.UpdateSchedulePayload.schedule.select(
                *fields or ProjectFields.schedule_fields(self.ds)
            )
        )
        return self.conn.run_mutation(mutation)

    def delete_schedule(self, schedule_input, fields=None):
        """Deletes a Schedule

        .. dropdown:: GraphQL Input Example

            It has to be converted to dict

            .. code-block::

                input DeleteScheduleInput {
                  scheduleId: ObjectID!
                }

        :param schedule_input: DeleteScheduleInput
        :type schedule_input: dict
        :param fields: Select specific fields
        :type fields: List(DSLField)
        """
        mutation = self.mutation.deleteSchedule.args(input=schedule_input).select(
            self.ds.DeleteSchedulePayload.schedule.select(
                *fields or ProjectFields.schedule_fields(self.ds)
            )
        )
        return self.conn.run_mutation(mutation)
