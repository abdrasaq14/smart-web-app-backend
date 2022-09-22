import awswrangler as wr
from django.conf import settings

# AWS Redis Client
ARC = wr.data_api.rds.connect(
    resource_arn=settings.AWS_ARN_RESOURCE,
    database=settings.AWS_RDS_DATABASE,
    secret_arn=settings.AWS_SECRET_ARN
)
