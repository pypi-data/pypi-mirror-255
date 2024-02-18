from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.crawls.fields import CrawlFields


class CrawlMutation:
    def __init__(self, conn: DeepCrawlConnection) -> None:
        self.conn = conn
        self.ds = conn.ds
        self.mutation = self.ds.Mutation

    def run_crawl_for_project(self, project_id, fields=None):
        """Run a Crawl for a Project

        :param project_id: Project id
        :type project_id: int or str
        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        mutation = self.mutation.runCrawlForProject.args(input={"projectId": project_id}).select(
            self.ds.RunCrawlForProjectPayload.crawl.select(*fields or (self.ds.Crawl.id,))
        )
        return self.conn.run_mutation(mutation)

    def pause_crawling(self, crawl_id, fields=None):
        """Pause a running Crawl

        :param crawl_id: Crawl id
        :type crawl_id: int or str
        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        mutation = self.mutation.pauseCrawling.args(input={"crawlId": crawl_id}).select(
            self.ds.PauseCrawlingPayload.crawl.select(*fields or CrawlFields.fields(self.ds))
        )
        return self.conn.run_mutation(mutation)

    def resume_crawling(self, crawl_id, fields=None):
        """Resume a Crawl

        :param crawl_id: Crawl id
        :type crawl_id: int or str
        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        mutation = self.mutation.resumeCrawling.args(input={"crawlId": crawl_id}).select(
            self.ds.ResumeCrawlingPayload.crawl.select(*fields or CrawlFields.fields(self.ds))
        )
        return self.conn.run_mutation(mutation)

    def cancel_crawling(self, crawl_id, fields=None):
        """Cancel a running Crawl

        :param crawl_id: Crawl id
        :type crawl_id: int or str
        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        mutation = self.mutation.cancelCrawling.args(input={"crawlId": crawl_id}).select(
            self.ds.CancelCrawlingPayload.crawl.select(*fields or CrawlFields.fields(self.ds))
        )
        return self.conn.run_mutation(mutation)

    def unarchive_crawl(self, crawl_id, fields=None):
        """Unarchive a Crawl

        :param crawl_id: Crawl id
        :type crawl_id: int or str
        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        mutation = self.mutation.unarchiveCrawl.args(input={"crawlId": crawl_id}).select(
            self.ds.RunCrawlForProjectPayload.crawl.select(
                *fields or CrawlFields.fields(self.ds)
            )
        )
        return self.conn.run_mutation(mutation)

    def delete_crawl(self, crawl_id, fields=None):
        """Deletes a Crawl

        :param crawl_id: Crawl id
        :type crawl_id: int or str
        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        mutation = self.mutation.deleteCrawl.args(input={"crawlId": crawl_id}).select(
            self.ds.DeleteCrawlPayload.crawl.select(
                *fields or CrawlFields.fields(self.ds)
            )
        )
        return self.conn.run_mutation(mutation)
