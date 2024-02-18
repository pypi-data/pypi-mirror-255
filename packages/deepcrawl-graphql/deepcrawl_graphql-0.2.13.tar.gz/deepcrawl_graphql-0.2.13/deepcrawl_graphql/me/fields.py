from gql.dsl import DSLMetaField


class MeFields:
    @staticmethod
    def fields(ds):
        return (
            ds.User.id,
            ds.User.username,
            ds.User.email,
            ds.User.firstName,
            ds.User.lastName,
            ds.User.createdAt,
            ds.User.updatedAt,
            ds.User.jobTitle,
            ds.User.overallLimitLevelsMax,
            ds.User.overallLimitPagesMax,
            ds.User.ssoClientId,
            ds.User.termsAgreed,
            ds.User.rawID,
            ds.User.permissions.select(ds.Permission.code),
            DSLMetaField("__typename"),
        )
