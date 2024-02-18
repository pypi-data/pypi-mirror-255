from gql.dsl import DSLMetaField


class ProjectFields:
    @staticmethod
    def fields(ds):
        return (
            ds.Project.id,
            ds.Project.alertEmails,
            ds.Project.allPagesTotal,
            ds.Project.apiCallbackUrl,
            ds.Project.autoFinalizeOnCrawlLimits,
            ds.Project.compareToCrawl,
            ds.Project.coreUIUrl,
            ds.Project.crawlDisallowedUrls1stLevel,
            ds.Project.crawlHyperlinksExternal,
            ds.Project.crawlHyperlinksInternal,
            ds.Project.crawlImagesExternal,
            ds.Project.crawlImagesInternal,
            ds.Project.crawlNofollowHyperlinks,
            ds.Project.crawlNonHtml,
            ds.Project.crawlNotIncluded1stLevel,
            ds.Project.crawlOtherRelExternal,
            ds.Project.crawlOtherRelInternal,
            ds.Project.crawlRate,
            ds.Project.crawlRedirectsExternal,
            ds.Project.crawlRedirectsInternal,
            ds.Project.crawlRelAmphtmlInternal,
            ds.Project.crawlRelAmphtmlExternal,
            ds.Project.crawlRelCanonicalsExternal,
            ds.Project.crawlRelCanonicalsInternal,
            ds.Project.crawlRelHreflangsExternal,
            ds.Project.crawlRelHreflangsInternal,
            ds.Project.crawlRelMobileExternal,
            ds.Project.crawlRelMobileInternal,
            ds.Project.crawlRelNextPrevExternal,
            ds.Project.crawlRelNextPrevInternal,
            ds.Project.crawlRobotsTxtNoindex,
            ds.Project.crawlScriptsExternal,
            ds.Project.crawlScriptsInternal,
            ds.Project.crawlSitemapsExternal,
            ds.Project.crawlSitemapsInternal,
            ds.Project.crawlStylesheetsExternal,
            ds.Project.crawlStylesheetsInternal,
            ds.Project.crawlTestSite,
            ds.Project.crawlTypes,
            ds.Project.crawlingAt,
            ds.Project.crawlsTotalCount,
            ds.Project.createdAt,
            ds.Project.customHeaderUserAgent,
            ds.Project.customHeaderUserAgentShort,
            ds.Project.customRequestHeaders,
            ds.Project.discoverSitemapsInRobotsTxt,
            ds.Project.duplicatePrecision,
            ds.Project.emptyPageThreshold,
            ds.Project.excludeUrlPatterns,
            ds.Project.finishedAt,
            ds.Project.forceMonitorApp,
            ds.Project.gaDateRange,
            ds.Project.hasTestSitePassword,
            ds.Project.highLogSummaryRequests,
            ds.Project.ignoreInvalidSSLCertificate,
            ds.Project.includeHttpAndHttps,
            ds.Project.includeSubdomains,
            ds.Project.includeUrlPatterns,
            ds.Project.isTestSuite,
            ds.Project.lastCrawlCrawlingAt,
            ds.Project.lastCrawlStatus,
            ds.Project.legacyTasksTotalCount,
            ds.Project.limitLevelsMax,
            ds.Project.limitPagesMax,
            ds.Project.limitUrlsMax,
            ds.Project.logSummaryRequestsHigh,
            ds.Project.logSummaryRequestsLow,
            ds.Project.lowLogSummaryRequests,
            ds.Project.maxBodyContentLength,
            ds.Project.maxContentSize,
            ds.Project.maxDescriptionLength,
            ds.Project.maxExternalLinks,
            ds.Project.maxHtmlSize,
            ds.Project.maxLinks,
            ds.Project.maxLinksProcessed,
            ds.Project.maxLoadTime,
            ds.Project.maxRedirections,
            ds.Project.maxTitleWidth,
            ds.Project.maxUrlLength,
            ds.Project.maximumCrawlRate,
            ds.Project.minContentRatio,
            ds.Project.minDescriptionLength,
            ds.Project.minTitleLength,
            ds.Project.minVisits,
            ds.Project.mobileHomepageUrl,
            ds.Project.mobileUrlPattern,
            ds.Project.name,
            ds.Project.primaryDomain,
            ds.Project.rawID,
            ds.Project.rendererBlockAds,
            ds.Project.rendererBlockAnalytics,
            ds.Project.rendererBlockCustom,
            ds.Project.rendererJsString,
            ds.Project.rendererJsUrls,
            ds.Project.robotsOverwrite,
            ds.Project.schedulesTotalCount,
            ds.Project.secondaryDomains,
            ds.Project.segmentsTotalCount,
            ds.Project.sitePrimary,
            ds.Project.siteTest,
            ds.Project.siteTestUser,
            ds.Project.sitemapUrls,
            ds.Project.startUrls,
            ds.Project.testSiteDomain,
            ds.Project.testSiteUsername,
            ds.Project.testsTotalCount,
            ds.Project.thinPageThreshold,
            ds.Project.totalSteps,
            ds.Project.updatedAt,
            ds.Project.urlRewriteQueryParameters,
            ds.Project.urlRewriteStripFragment,
            ds.Project.urlsExcluded,
            ds.Project.urlsIncluded,
            ds.Project.useMobileSettings,
            ds.Project.useRenderer,
            ds.Project.useRobotsOverwrite,
            ds.Project.useStealthMode,
            ds.Project.useUrlRewriteRules,
            ds.Project.userAgentString,
            ds.Project.userAgentStringMobile,
            ds.Project.userAgentToken,
            ds.Project.userAgentTokenMobile,
            ds.Project.userAgent.select(ds.UserAgent.code, ds.UserAgent.name),
            ds.Project.urlSampling.select(
                ds.UrlSampling.name,
                ds.UrlSampling.regexPattern,
                ds.UrlSampling.samplePercentage,
            ),
            ds.Project.urlRewriteRules.select(
                ds.UrlRewriteRule.caseOption, ds.UrlRewriteRule.matchFrom, ds.UrlRewriteRule.rewriteTo
            ),
            ds.Project.mobileUserAgent.select(ds.UserAgent.code, ds.UserAgent.name),
            ds.Project.customDns.select(ds.CustomDnsSetting.hostname, ds.CustomDnsSetting.ipAddress),
            ds.Project.apiCallbackHeaders.select(ds.APICallbackHeader.key, ds.APICallbackHeader.value),
            ds.Project.alertSetting.select(ds.AlertSetting.code, ds.AlertSetting.name),
            DSLMetaField("__typename"),
        )

    @staticmethod
    def sitemaps_fields(ds):
        return (
            ds.Sitemap.enabled,
            ds.Sitemap.level,
            ds.Sitemap.linksOut,
            ds.Sitemap.parent,
            ds.Sitemap.status,
            ds.Sitemap.type,
            ds.Sitemap.url,
            ds.Sitemap.urlDigest,
            DSLMetaField("__typename"),
        )

    @staticmethod
    def advanced_crawl_rate_fields(ds):
        return (
            ds.AdvancedCrawlRate.type,
            ds.AdvancedCrawlRate.maximumCrawlRate,
            ds.AdvancedCrawlRate.start.select(ds.AdvancedCrawlRateTime.hour),
            ds.AdvancedCrawlRate.end.select(ds.AdvancedCrawlRateTime.day),
            DSLMetaField("__typename"),
        )

    @staticmethod
    def majestic_configuration_fields(ds):
        return (
            ds.MajesticConfiguration.createdAt,
            ds.MajesticConfiguration.updatedAt,
            ds.MajesticConfiguration.enabled,
            ds.MajesticConfiguration.maxRows,
            ds.MajesticConfiguration.useHistoricData,
            ds.MajesticConfiguration.useRootDomain,
            DSLMetaField("__typename"),
        )

    @staticmethod
    def location_fields(ds):
        return (
            ds.Location.id,
            ds.Location.name,
            ds.Location.code,
            ds.Location.enabled,
            ds.Location.rawID,
            ds.Location.type,
            DSLMetaField("__typename"),
        )

    @staticmethod
    def google_search_configuration_fields(ds):
        return (
            ds.GoogleSearchConsoleConfiguration.country,
            ds.GoogleSearchConsoleConfiguration.createdAt,
            ds.GoogleSearchConsoleConfiguration.excludeQueries,
            ds.GoogleSearchConsoleConfiguration.includeQueries,
            ds.GoogleSearchConsoleConfiguration.inheritFromSchedulePeriodOverride,
            ds.GoogleSearchConsoleConfiguration.lastNDays,
            ds.GoogleSearchConsoleConfiguration.minClicks,
            ds.GoogleSearchConsoleConfiguration.searchType,
            ds.GoogleSearchConsoleConfiguration.updatedAt,
            ds.GoogleSearchConsoleConfiguration.useSearchConsolePropertyDomainsAsStartUrls,
            DSLMetaField("__typename"),
        )

    @staticmethod
    def custom_extraction_setting_fields(ds):
        return (
            ds.CustomExtractionSetting.cleanHtmlTags,
            ds.CustomExtractionSetting.label,
            ds.CustomExtractionSetting.matchNumberFrom,
            ds.CustomExtractionSetting.matchNumberTo,
            ds.CustomExtractionSetting.regex,
            ds.CustomExtractionSetting.regexFilter,
            ds.CustomExtractionSetting.reportTemplateCode,
            DSLMetaField("__typename"),
        )

    @staticmethod
    def schedule_fields(ds):
        return (
            ds.Schedule.id,
            ds.Schedule.rawID,
            ds.Schedule.createdAt,
            ds.Schedule.updatedAt,
            ds.Schedule.latestRunTime,
            ds.Schedule.nextRunTime,
            ds.Schedule.scheduleFrequency.select(
                ds.ScheduleFrequency.code,
                ds.ScheduleFrequency.name
            ),
        )
