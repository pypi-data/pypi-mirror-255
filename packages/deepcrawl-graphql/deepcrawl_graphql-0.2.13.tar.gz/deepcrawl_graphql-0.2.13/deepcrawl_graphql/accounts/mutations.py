from deepcrawl_graphql.accounts.fields import AccountFields
from deepcrawl_graphql.api import DeepCrawlConnection


class AccountMutation:
    def __init__(self, conn: DeepCrawlConnection) -> None:
        self.conn = conn
        self.ds = conn.ds
        self.mutation = self.ds.Mutation

    def update_account(self, account_input, fields=None):
        """Update Account.

        .. dropdown:: GraphQL Input Example

            It has to be converted to dict

            .. code-block::

                input UpdateAccountInput {
                    accountId: ObjectID!
                    apiCallbackHeaders: [APICallbackHeaderInput!]
                    apiCallbackUrl: String
                    country: String
                    customLogo: Upload
                    customProxy: String
                }

        :param account_input: Account input
        :type account_input: dict
        :param fields: Select specific fields.
        :type fields: List(DSLField)
        """
        mutation = self.mutation.updateAccount.args(input=account_input).select(
            self.ds.UpdateAccountPayload.account.select(
                *fields or AccountFields.fields(self.ds)
            )
        )
        return self.conn.run_mutation(mutation)
