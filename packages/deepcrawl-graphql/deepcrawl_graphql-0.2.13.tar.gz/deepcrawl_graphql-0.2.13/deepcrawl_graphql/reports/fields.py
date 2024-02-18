from gql.dsl import DSLMetaField


class ReportFields:
    @staticmethod
    def fields(ds):
        return (
            ds.Report.id,
            ds.Report.change,
            ds.Report.changeWeight,
            ds.Report.coreUIUrl,
            ds.Report.crawlId,
            ds.Report.createdAt,
            ds.Report.hasChanges,
            ds.Report.projectId,
            ds.Report.queryVersion,
            ds.Report.rawID,
            ds.Report.reportTemplateCode,
            ds.Report.reportTypeCode,
            ds.Report.reportTypeCodeEnum,
            ds.Report.segmentVersion,
            ds.Report.totalRows,
            ds.Report.totalWeight,
            ds.Report.typeCode,
            DSLMetaField("__typename"),
        )

    @staticmethod
    def raw_trends(ds):
        return (
            ds.Report.rawTrends,
            DSLMetaField("__typename"),
        )

    @staticmethod
    def datasource_fields(ds):
        return (
            ds.Report.datasourceCode,
            ds.Report.datasourceCodeEnum,
            DSLMetaField("__typename"),
        )

    @staticmethod
    def segment_fields(ds):
        return (
            ds.Segment.id,
            ds.Segment.name,
            ds.Segment.crawlUrlFilter,
            ds.Segment.createdAt,
            ds.Segment.filter,
            ds.Segment.lastFailedAt,
            ds.Segment.lastGeneratedAt,
            ds.Segment.rawID,
            ds.Segment.updatedAt,
            ds.Segment.version,
            DSLMetaField("__typename"),
        )

    @staticmethod
    def report_template_fields(ds):
        return (
            ds.ReportTemplate.allowedOutputTypes,
            ds.ReportTemplate.automatorSummary,
            ds.ReportTemplate.beta,
            ds.ReportTemplate.categories,
            ds.ReportTemplate.changeSign,
            ds.ReportTemplate.changeWeight,
            ds.ReportTemplate.code,
            ds.ReportTemplate.createdAt,
            ds.ReportTemplate.datasourceCode,
            ds.ReportTemplate.datasourceCodeEnum,
            ds.ReportTemplate.defaultMetrics,
            ds.ReportTemplate.defaultOrderBy,
            ds.ReportTemplate.deletedAt,
            ds.ReportTemplate.description,
            ds.ReportTemplate.healthscoreCategory,
            ds.ReportTemplate.healthscoreSubcategories,
            ds.ReportTemplate.id,
            ds.ReportTemplate.name,
            ds.ReportTemplate.position,
            ds.ReportTemplate.queryVersion,
            ds.ReportTemplate.rawID,
            ds.ReportTemplate.reportTypes,
            ds.ReportTemplate.summary,
            ds.ReportTemplate.tags,
            ds.ReportTemplate.totalSign,
            ds.ReportTemplate.totalWeight,
            ds.ReportTemplate.updatedAt,
            ds.ReportTemplate.reportCategories.select(
                ds.ReportCategory.code,
                ds.ReportCategory.healthScore,
                ds.ReportCategory.name,
                ds.ReportCategory.parentCode,
                ds.ReportCategory.position,
            ),
            DSLMetaField("__typename"),
            # TODO Add metricsGroupings somewhere
        )


class ReportTypeFields:
    @staticmethod
    def fields(ds):
        return (
            ds.ReportType.code,
            ds.ReportType.id,
            ds.ReportType.name,
            ds.ReportType.position,
            ds.ReportType.rawID,
            DSLMetaField("__typename"),
        )


class ReportDownloadFields:
    @staticmethod
    def fields(ds):
        return (
            ds.ReportDownload.id,
            ds.ReportDownload.rawID,
            ds.ReportDownload.createdAt,
            ds.ReportDownload.fileURL,
            ds.ReportDownload.filter,
            ds.ReportDownload.outputType,
            ds.ReportDownload.reportedAt,
            ds.ReportDownload.reportingAt,
            ds.ReportDownload.selectedMetrics,
            ds.ReportDownload.status,
            ds.ReportDownload.totalRows,
            ds.ReportDownload.updatedAt,
        )
