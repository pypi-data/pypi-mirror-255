'''
# RedshiftServerlessNamespace

A [Redshift Serverless Namespace](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-workgroup-namespace.html) with secrets manager integration for admin credentials management and rotation.

## Overview

`RedshiftServerlessNamespace` is a [Redshift Serverless Namespace](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-workgroup-namespace.html) with the following options:

* Encrypt data with a customer managed KMS Key.
* Create Redshift superuser credentials managed by Redshift service: stored in Secrets Manager, encrypted with a KMS Key, and with automatic rotation.
* Attach multiple IAM roles that can be used by Redshift Serverless users to interact with other AWS services.
* Set an [IAM role as default](https://docs.aws.amazon.com/redshift/latest/mgmt/default-iam-role.html)

## Usage

```python
class ExampleDefaultRedshiftServerlessNamespaceStack(Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)
        dsf.consumption.RedshiftServerlessNamespace(self, "RedshiftServerlessNamespace",
            db_name="database",
            name="example-namespace"
        )
```

## Attaching IAM Roles to Redshift Serverless Namespace

To allow Redshift Serverless to access other AWS services on your behalf (eg. data ingestion from S3 via the COPY command, accessing data in S3 via Redshift Spectrum, exporting data from Redshift to S3 via the UNLOAD command.), the preferred method is to specify an IAM role. High-level steps are as follows:

1. Create an IAM role with a trust relationship of `redshift.amazonaws.com`.
2. Attach policy/permissions to the role to give it access to specific AWS services.
3. Configure the role when creating the Redshift Serverless Namespace
4. Run the relevant SQL command referencing the attached IAM role via its ARN (or the `default` keyword if a default IAM role is configured)

```python
class ExampleRedshiftServerlessNamespaceRolesStack(Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        bucket = Bucket(self, "ExampleBucket")

        ingestion_role = Role(self, "IngestionRole",
            assumed_by=ServicePrincipal("redshift.amazonaws.com"),
            managed_policies=[
                ManagedPolicy.from_aws_managed_policy_name("AmazonRedshiftAllCommandsFullAccess")
            ]
        )

        bucket.grant_read(ingestion_role)

        dsf.consumption.RedshiftServerlessNamespace(self, "RedshiftServerlessNamespace",
            db_name="database",
            name="example-namespace",
            default_iAMRole=ingestion_role
        )
```

# RedshiftServerlessWorkgroup

A [Redshift Serverless Workgroup](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-workgroup-namespace.html) with helpers method for Redshift administration.

## Overview

`RedshiftServerlessWorkgroup` is a [Redshift Serverless Workgroup](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-workgroup-namespace.html) with the following options/capabilities:

* Deployed in a VPC in private subnets. The network configuation can be customized.
* Provide helper methods for running SQL commands via the Redshift Data API. Commands can be custom or predefined for common administration tasks like creating and granting roles.
* Initialize a Glue Data Catalog integration with auto crawling via Glue Crawlers. This would allow tables in Redshift Serverless to appear in the [Glue Data Catalog](https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html) for the purposes of discovery and integration.

## Usage

```python
class ExampleDefaultRedshiftServerlessWorkgroupStack(Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        namespace = dsf.consumption.RedshiftServerlessNamespace(self, "DefaultRedshiftServerlessNamespace",
            name="default",
            db_name="defaultdb"
        )

        dsf.consumption.RedshiftServerlessWorkgroup(self, "DefaultRedshiftServerlessWorkgroup",
            name="default",
            namespace=namespace
        )
```

## Bootstrapping Redshift Serverless w/ RedshiftData Construct

The `RedshiftData` construct allows custom SQLs to run against the `RedshiftServerlessWorkgroup` via the Data API. This allows users to bootstrap Redshift directly from CDK.

The `RedshitData` construct provides the following helpers for bootstrapping Redshift databases:

* Run a custom SQL command
* Create Redshift roles
* Grant Redshift roles full access to schemas
* Grant Redshift roles read only access
* Run a COPY command to load data

```python
workgroup = dsf.consumption.RedshiftServerlessWorkgroup(self, "DefaultRedshiftServerlessWorkgroup",
    name="default",
    namespace=namespace
)

# Initialize the Redshift Data API
data_access = workgroup.access_data("DataApi", True)

# Run a custom SQL to create a customer table
create_table = data_access.run_custom_sQL("CreateCustomerTable", "defaultdb", """
          CREATE TABLE customer(
            customer_id varchar(50),
            salutation varchar(5),
            first_name varchar(50),
            last_name varchar(50),
            email_address varchar(100)
          )
          diststyle even
          """, "drop table customer")

# Run a COPY command to load data into the customer table
ingestion = data_access.ingest_data("ExampleCopy", "defaultdb", "customer", bucket, "data-products/customer/", "csv ignoreheader 1")

# Add dependencies between Redshift Data API commands because CDK cannot infer them
ingestion.node.add_dependency(create_table)

# Create an engineering role in the defaultdb
db_role = data_access.create_db_role("EngineeringRole", "defaultdb", "engineering")

# Grant the engineering role full access to the public schema in the defaultdb
db_schema = data_access.grant_db_schema_to_role("EngineeringGrant", "defaultdb", "public", "engineering")

# Enforce dependencies
db_schema.node.add_dependency(db_role)
```

## Cataloging Redshift Serverless Tables

Redshift tables and databases can also be automatically catalog in Glue Data Catalog using an helper method. This method creates a Glue Catalog database as well as a crawler to populate the database with table metadata from your Redshift database.

The default value of the path that the crawler would use is `<databaseName>/public/%` which translates to all the tables in the public schema. Please refer to the [crawler documentation](https://docs.aws.amazon.com/glue/latest/dg/define-crawler.html#define-crawler-choose-data-sources) for more information for JDBC data sources.

```python
class ExampleRedshiftServerlessWorkgroupCatalogStack(Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        namespace = dsf.consumption.RedshiftServerlessNamespace(self, "DefaultRedshiftServerlessNamespace",
            name="default",
            db_name="defaultdb"
        )

        workgroup = dsf.consumption.RedshiftServerlessWorkgroup(self, "DefaultRedshiftServerlessWorkgroup",
            name="default",
            namespace=namespace
        )

        workgroup.catalog_tables("RedshiftCatalog", "example-redshift-db", "defaultdb/public/%")
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from .._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_glue as _aws_cdk_aws_glue_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_redshiftserverless as _aws_cdk_aws_redshiftserverless_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8
from ..governance import DataCatalogDatabase as _DataCatalogDatabase_8a7a02f0


class RedshiftData(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-dsf.consumption.RedshiftData",
):
    '''Creates an asynchronous custom resource that handles the execution of SQL using Redshift's Data API.

    If ``vpc`` and ``vpcSubnets`` are passed, this construct would also create the Redshift Data Interface VPC endpoint and configure the custom resource in the same VPC subnet.

    Example::

        namespace = dsf.consumption.RedshiftServerlessNamespace(self, "RedshiftNamespace",
            name="default",
            db_name="defaultdb"
        )
        
        workgroup = dsf.consumption.RedshiftServerlessWorkgroup(self, "RedshiftWorkgroup",
            name="redshift-workgroup",
            namespace=namespace
        )
        
        rs_data = workgroup.access_data("DataApi")
        rs_data.create_db_role("EngineeringRole", "defaultdb", "engineering")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        cluster_id: typing.Optional[builtins.str] = None,
        create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
        execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        workgroup_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param secret: The Secrets Manager Secret containing the admin credentials for the Redshift cluster / namespace.
        :param cluster_id: The name of the Redshift provisioned to query. It must be configured if the ``workgroupId`` is not. Default: - The ``workgroupId`` is used
        :param create_interface_vpc_endpoint: If set to true, create the Redshift Data Interface VPC Endpoint in the configured VPC/Subnets. Default: - false
        :param execution_timeout: The timeout for the query execution. Default: - 5mins
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param secret_key: The KMS Key used to encrypt the admin credentials for the Redshift cluster / namespace. Default: - no secret key is used
        :param subnets: The subnets where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the subnets. Default: - No subnets are used. The Custom Resource runs in the Redshift service team subnets.
        :param vpc: The VPC where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the VPC. Default: - No VPC is used. The Custom Resource runs in the Redshift service team VPC
        :param workgroup_id: The ``workgroupId`` for the Redshift Serverless Workgroup to query. It must be configured if the ``clusterId`` is not. Default: - The ``clusterId`` is used
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6c16f956219fc8fdb9e784a5a3d784e55725facb2f1757631dd017f3942a5eb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedshiftDataProps(
            secret=secret,
            cluster_id=cluster_id,
            create_interface_vpc_endpoint=create_interface_vpc_endpoint,
            execution_timeout=execution_timeout,
            removal_policy=removal_policy,
            secret_key=secret_key,
            subnets=subnets,
            vpc=vpc,
            workgroup_id=workgroup_id,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="assignDbRolesToIAMRole")
    def assign_db_roles_to_iam_role(
        self,
        db_roles: typing.Sequence[builtins.str],
        target_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    ) -> None:
        '''Assigns Redshift DB roles to IAM role vs the ``RedshiftDbRoles`` tag.

        :param db_roles: List of Redshift DB roles to assign to IAM role.
        :param target_role: The IAM role to assign the Redshift DB roles to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70746f1f6784f2381f3504370ee6af95f7ac82990574454ab8ed576bf5688c59)
            check_type(argname="argument db_roles", value=db_roles, expected_type=type_hints["db_roles"])
            check_type(argname="argument target_role", value=target_role, expected_type=type_hints["target_role"])
        return typing.cast(None, jsii.invoke(self, "assignDbRolesToIAMRole", [db_roles, target_role]))

    @jsii.member(jsii_name="createDbRole")
    def create_db_role(
        self,
        id: builtins.str,
        database_name: builtins.str,
        role_name: builtins.str,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Creates a new DB role.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param role_name: The name of the role to create.

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1270ad3991e26b90cece045ea41b63111e3fe01f953c4bed18c350197e5ba21e)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "createDbRole", [id, database_name, role_name]))

    @jsii.member(jsii_name="grantDbAllPrivilegesToRole")
    def grant_db_all_privileges_to_role(
        self,
        id: builtins.str,
        database_name: builtins.str,
        schema: builtins.str,
        role_name: builtins.str,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Grants both read and write permissions on all the tables in the ``schema`` to the DB role.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param schema: The schema where the tables are located in.
        :param role_name: The DB role to grant the permissions to.

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3676187b92f6742c03d35124ee5d7c1c4e0328311a5857a012dfcf4cafa2b1f6)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "grantDbAllPrivilegesToRole", [id, database_name, schema, role_name]))

    @jsii.member(jsii_name="grantDbSchemaToRole")
    def grant_db_schema_to_role(
        self,
        id: builtins.str,
        database_name: builtins.str,
        schema: builtins.str,
        role_name: builtins.str,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Grants access to the schema to the DB role.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param schema: The schema where the tables are located in.
        :param role_name: The DB role to grant the permissions to.

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c34f05895e0ec9a0153244a7039d1fe2a3838d022d1e84b4e7a920837fee0544)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "grantDbSchemaToRole", [id, database_name, schema, role_name]))

    @jsii.member(jsii_name="grantSchemaReadToRole")
    def grant_schema_read_to_role(
        self,
        id: builtins.str,
        database_name: builtins.str,
        schema: builtins.str,
        role_name: builtins.str,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Grants read permission on all the tables in the ``schema`` to the DB role.

        :param id: -
        :param database_name: The name of the database to run this command.
        :param schema: The schema where the tables are located in.
        :param role_name: The DB role to grant the permissions to.

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9300eec9bcc19e7791cba4dab6f5f59896db2f1c50740eb39fcfcf25dbebad4a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "grantSchemaReadToRole", [id, database_name, schema, role_name]))

    @jsii.member(jsii_name="ingestData")
    def ingest_data(
        self,
        id: builtins.str,
        database_name: builtins.str,
        target_table: builtins.str,
        source_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        source_prefix: builtins.str,
        ingest_additional_options: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Ingest data from S3 into a Redshift table.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param target_table: The target table to load the data into.
        :param source_bucket: The bucket where the source data would be coming from.
        :param source_prefix: The location inside the bucket where the data would be ingested from.
        :param ingest_additional_options: Optional. Additional options to pass to the ``COPY`` command. For example, ``delimiter '|'`` or ``ignoreheader 1``
        :param role: Optional. The IAM Role to use to access the data in S3. If not provided, it would use the default IAM role configured in the Redshift Namespace
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9e19236fe69bfe81295a236db19041243888528841ce8ea4c1421a81fd3b55d)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument target_table", value=target_table, expected_type=type_hints["target_table"])
            check_type(argname="argument source_bucket", value=source_bucket, expected_type=type_hints["source_bucket"])
            check_type(argname="argument source_prefix", value=source_prefix, expected_type=type_hints["source_prefix"])
            check_type(argname="argument ingest_additional_options", value=ingest_additional_options, expected_type=type_hints["ingest_additional_options"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "ingestData", [id, database_name, target_table, source_bucket, source_prefix, ingest_additional_options, role]))

    @jsii.member(jsii_name="mergeToTargetTable")
    def merge_to_target_table(
        self,
        id: builtins.str,
        database_name: builtins.str,
        source_table: builtins.str,
        target_table: builtins.str,
        source_column_id: typing.Optional[builtins.str] = None,
        target_column_id: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Run the ``MERGE`` query using simplified mode.

        This command would do an upsert into the target table.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param source_table: The source table name. Schema can also be included using the following format: ``schemaName.tableName``
        :param target_table: The target table name. Schema can also be included using the following format: ``schemaName.tableName``
        :param source_column_id: The column in the source table that's used to determine whether the rows in the ``sourceTable`` can be matched with rows in the ``targetTable``. Default is ``id``
        :param target_column_id: The column in the target table that's used to determine whether the rows in the ``sourceTable`` can be matched with rows in the ``targetTable``. Default is ``id``

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be9c53641644b2e9b800be6da305025e12da93b6613fa02521951fb2d96cdf74)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument source_table", value=source_table, expected_type=type_hints["source_table"])
            check_type(argname="argument target_table", value=target_table, expected_type=type_hints["target_table"])
            check_type(argname="argument source_column_id", value=source_column_id, expected_type=type_hints["source_column_id"])
            check_type(argname="argument target_column_id", value=target_column_id, expected_type=type_hints["target_column_id"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "mergeToTargetTable", [id, database_name, source_table, target_table, source_column_id, target_column_id]))

    @jsii.member(jsii_name="retrieveVersion")
    def retrieve_version(self) -> typing.Any:
        '''Retrieve DSF package.json version.'''
        return typing.cast(typing.Any, jsii.invoke(self, "retrieveVersion", []))

    @jsii.member(jsii_name="runCustomSQL")
    def run_custom_sql(
        self,
        id: builtins.str,
        database_name: builtins.str,
        sql: builtins.str,
        delete_sql: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_ceddda9d.CustomResource:
        '''Runs a custom SQL.

        Once the custom resource finishes execution, the attribute ``Data`` contains an attribute ``execId`` which contains the Redshift Data API execution ID. You can then use this to retrieve execution results via the ``GetStatementResult`` API.

        :param id: The CDK Construct ID.
        :param database_name: The name of the database to run this command.
        :param sql: The sql to run.
        :param delete_sql: Optional. The sql to run when this resource gets deleted

        :return: ``CustomResource``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d11c2e475c18cec3a62ed59e67e9a866dc268e471dc7ec9c6a283dac47f3954)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument sql", value=sql, expected_type=type_hints["sql"])
            check_type(argname="argument delete_sql", value=delete_sql, expected_type=type_hints["delete_sql"])
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.invoke(self, "runCustomSQL", [id, database_name, sql, delete_sql]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_OWNED_TAG")
    def DSF_OWNED_TAG(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_OWNED_TAG"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_TRACKING_CODE")
    def DSF_TRACKING_CODE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_TRACKING_CODE"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM Role for the Redshift Data API execution.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "executionRole"))

    @builtins.property
    @jsii.member(jsii_name="statusFunction")
    def status_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda Function for the Redshift Data API status checks.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "statusFunction"))

    @builtins.property
    @jsii.member(jsii_name="statusLogGroup")
    def status_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Log Group for the Redshift Data API status checks.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "statusLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="submitFunction")
    def submit_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda Function for the Redshift Data submission.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "submitFunction"))

    @builtins.property
    @jsii.member(jsii_name="submitLogGroup")
    def submit_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Log Group for the Redshift Data API submission.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "submitLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="taggingManagedPolicy")
    def tagging_managed_policy(self) -> _aws_cdk_aws_iam_ceddda9d.IManagedPolicy:
        '''The managed IAM policy allowing IAM Role to retrieve tag information.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IManagedPolicy, jsii.get(self, "taggingManagedPolicy"))

    @builtins.property
    @jsii.member(jsii_name="targetArn")
    def target_arn(self) -> builtins.str:
        '''The ARN of the target cluster or workgroup.'''
        return typing.cast(builtins.str, jsii.get(self, "targetArn"))

    @builtins.property
    @jsii.member(jsii_name="targetId")
    def target_id(self) -> builtins.str:
        '''The ID of the target cluster or workgroup.'''
        return typing.cast(builtins.str, jsii.get(self, "targetId"))

    @builtins.property
    @jsii.member(jsii_name="cleanUpFunction")
    def clean_up_function(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''The Lambda function for the S3 data copy cleaning up lambda.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], jsii.get(self, "cleanUpFunction"))

    @builtins.property
    @jsii.member(jsii_name="cleanUpLogGroup")
    def clean_up_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The CloudWatch Log Group for the Redshift Data cleaning up lambda.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "cleanUpLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="cleanUpRole")
    def clean_up_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM Role for the the S3 data copy cleaning up lambda.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "cleanUpRole"))

    @builtins.property
    @jsii.member(jsii_name="customResourceSecurityGroup")
    def custom_resource_security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The Security Group used by the Custom Resource when deployed in a VPC.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "customResourceSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="vpcEndpoint")
    def vpc_endpoint(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpoint]:
        '''The created Redshift Data API interface vpc endpoint when deployed in a VPC.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpoint], jsii.get(self, "vpcEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="vpcEndpointSecurityGroup")
    def vpc_endpoint_security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The Security Group used by the VPC Endpoint when deployed in a VPC.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], jsii.get(self, "vpcEndpointSecurityGroup"))


@jsii.data_type(
    jsii_type="aws-dsf.consumption.RedshiftDataProps",
    jsii_struct_bases=[],
    name_mapping={
        "secret": "secret",
        "cluster_id": "clusterId",
        "create_interface_vpc_endpoint": "createInterfaceVpcEndpoint",
        "execution_timeout": "executionTimeout",
        "removal_policy": "removalPolicy",
        "secret_key": "secretKey",
        "subnets": "subnets",
        "vpc": "vpc",
        "workgroup_id": "workgroupId",
    },
)
class RedshiftDataProps:
    def __init__(
        self,
        *,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        cluster_id: typing.Optional[builtins.str] = None,
        create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
        execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        workgroup_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''The properties for the ``RedshiftData`` construct.

        :param secret: The Secrets Manager Secret containing the admin credentials for the Redshift cluster / namespace.
        :param cluster_id: The name of the Redshift provisioned to query. It must be configured if the ``workgroupId`` is not. Default: - The ``workgroupId`` is used
        :param create_interface_vpc_endpoint: If set to true, create the Redshift Data Interface VPC Endpoint in the configured VPC/Subnets. Default: - false
        :param execution_timeout: The timeout for the query execution. Default: - 5mins
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param secret_key: The KMS Key used to encrypt the admin credentials for the Redshift cluster / namespace. Default: - no secret key is used
        :param subnets: The subnets where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the subnets. Default: - No subnets are used. The Custom Resource runs in the Redshift service team subnets.
        :param vpc: The VPC where the Custom Resource Lambda Function would be created in. A Redshift Data API Interface VPC Endpoint is created in the VPC. Default: - No VPC is used. The Custom Resource runs in the Redshift service team VPC
        :param workgroup_id: The ``workgroupId`` for the Redshift Serverless Workgroup to query. It must be configured if the ``clusterId`` is not. Default: - The ``clusterId`` is used
        '''
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SelectedSubnets(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d6dbe1316db9272b5422946107575b24310dd5cc4078f9c3d5cab4440f25756)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument create_interface_vpc_endpoint", value=create_interface_vpc_endpoint, expected_type=type_hints["create_interface_vpc_endpoint"])
            check_type(argname="argument execution_timeout", value=execution_timeout, expected_type=type_hints["execution_timeout"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument secret_key", value=secret_key, expected_type=type_hints["secret_key"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument workgroup_id", value=workgroup_id, expected_type=type_hints["workgroup_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "secret": secret,
        }
        if cluster_id is not None:
            self._values["cluster_id"] = cluster_id
        if create_interface_vpc_endpoint is not None:
            self._values["create_interface_vpc_endpoint"] = create_interface_vpc_endpoint
        if execution_timeout is not None:
            self._values["execution_timeout"] = execution_timeout
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if secret_key is not None:
            self._values["secret_key"] = secret_key
        if subnets is not None:
            self._values["subnets"] = subnets
        if vpc is not None:
            self._values["vpc"] = vpc
        if workgroup_id is not None:
            self._values["workgroup_id"] = workgroup_id

    @builtins.property
    def secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''The Secrets Manager Secret containing the admin credentials for the Redshift cluster / namespace.'''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

    @builtins.property
    def cluster_id(self) -> typing.Optional[builtins.str]:
        '''The name of the Redshift provisioned to query.

        It must be configured if the ``workgroupId`` is not.

        :default: - The ``workgroupId`` is used
        '''
        result = self._values.get("cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_interface_vpc_endpoint(self) -> typing.Optional[builtins.bool]:
        '''If set to true, create the Redshift Data Interface VPC Endpoint in the configured VPC/Subnets.

        :default: - false
        '''
        result = self._values.get("create_interface_vpc_endpoint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def execution_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The timeout for the query execution.

        :default: - 5mins
        '''
        result = self._values.get("execution_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise, the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def secret_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS Key used to encrypt the admin credentials for the Redshift cluster / namespace.

        :default: - no secret key is used
        '''
        result = self._values.get("secret_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets]:
        '''The subnets where the Custom Resource Lambda Function would be created in.

        A Redshift Data API Interface VPC Endpoint is created in the subnets.

        :default: - No subnets are used. The Custom Resource runs in the Redshift service team subnets.
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC where the Custom Resource Lambda Function would be created in.

        A Redshift Data API Interface VPC Endpoint is created in the VPC.

        :default: - No VPC is used. The Custom Resource runs in the Redshift service team VPC
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def workgroup_id(self) -> typing.Optional[builtins.str]:
        '''The ``workgroupId`` for the Redshift Serverless Workgroup to query.

        It must be configured if the ``clusterId`` is not.

        :default: - The ``clusterId`` is used
        '''
        result = self._values.get("workgroup_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftDataProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftServerlessNamespace(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-dsf.consumption.RedshiftServerlessNamespace",
):
    '''Create a Redshift Serverless Namespace with the admin credentials stored in Secrets Manager.

    Example::

        namespace = dsf.consumption.RedshiftServerlessNamespace(self, "DefaultServerlessNamespace",
            db_name="defaultdb",
            name="default"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        db_name: builtins.str,
        name: builtins.str,
        admin_secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        admin_username: typing.Optional[builtins.str] = None,
        data_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        default_iam_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        iam_roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
        log_exports: typing.Optional[typing.Sequence["RedshiftServerlessNamespaceLogExport"]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param db_name: The name of the primary database that would be created in the Redshift Serverless Namespace.
        :param name: The name of the Redshift Serverless Namespace.
        :param admin_secret_key: The KMS Key used by the managed Secrets Manager Secret storing admin credentials. Default: - A new KMS Key is created
        :param admin_username: The admin username to be used. Default: - The default username is "admin"
        :param data_key: The KMS Key used to encrypt the data. Default: - A new KMS Key is created
        :param default_iam_role: Default IAM Role associated to the Redshift Serverless Namespace. Default: - No default IAM Role is associated with the Redshift Serverless Namespace
        :param iam_roles: List of IAM Roles attached to the Redshift Serverless Namespace. This list of Roles must also contain the ``defaultIamRole``. Default: - No IAM roles are associated with the Redshift Serverless Namespace
        :param log_exports: The type of logs to be exported. Default: - No logs are exported
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f9c7878838fb6a2d2369d6cb06e7f6babfef4ed727eeebb9bef3b2b4d54eb37)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedshiftServerlessNamespaceProps(
            db_name=db_name,
            name=name,
            admin_secret_key=admin_secret_key,
            admin_username=admin_username,
            data_key=data_key,
            default_iam_role=default_iam_role,
            iam_roles=iam_roles,
            log_exports=log_exports,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="retrieveVersion")
    def retrieve_version(self) -> typing.Any:
        '''Retrieve DSF package.json version.'''
        return typing.cast(typing.Any, jsii.invoke(self, "retrieveVersion", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_OWNED_TAG")
    def DSF_OWNED_TAG(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_OWNED_TAG"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_TRACKING_CODE")
    def DSF_TRACKING_CODE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_TRACKING_CODE"))

    @builtins.property
    @jsii.member(jsii_name="adminSecret")
    def admin_secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''The created Secrets Manager secret containing the admin credentials.'''
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, jsii.get(self, "adminSecret"))

    @builtins.property
    @jsii.member(jsii_name="adminSecretKey")
    def admin_secret_key(self) -> _aws_cdk_aws_kms_ceddda9d.IKey:
        '''The KMS Key used to encrypt the admin credentials secret.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.IKey, jsii.get(self, "adminSecretKey"))

    @builtins.property
    @jsii.member(jsii_name="createFunction")
    def create_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda Function for the Redshift Serverless creation.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "createFunction"))

    @builtins.property
    @jsii.member(jsii_name="createLogGroup")
    def create_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Logs Log Group for the Redshift Serverless creation.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "createLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="createRole")
    def create_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM Role for the Redshift Serverless creation.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "createRole"))

    @builtins.property
    @jsii.member(jsii_name="customResource")
    def custom_resource(self) -> _aws_cdk_ceddda9d.CustomResource:
        '''The custom resource that creates the Namespace.'''
        return typing.cast(_aws_cdk_ceddda9d.CustomResource, jsii.get(self, "customResource"))

    @builtins.property
    @jsii.member(jsii_name="dataKey")
    def data_key(self) -> _aws_cdk_aws_kms_ceddda9d.Key:
        '''KMS key used by the namespace to encrypt the data.'''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.Key, jsii.get(self, "dataKey"))

    @builtins.property
    @jsii.member(jsii_name="dbName")
    def db_name(self) -> builtins.str:
        '''The name of the database.'''
        return typing.cast(builtins.str, jsii.get(self, "dbName"))

    @builtins.property
    @jsii.member(jsii_name="namespaceArn")
    def namespace_arn(self) -> builtins.str:
        '''The ARN of the created namespace.'''
        return typing.cast(builtins.str, jsii.get(self, "namespaceArn"))

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        '''The ID of the created namespace.'''
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @builtins.property
    @jsii.member(jsii_name="namespaceName")
    def namespace_name(self) -> builtins.str:
        '''The name of the created namespace.'''
        return typing.cast(builtins.str, jsii.get(self, "namespaceName"))

    @builtins.property
    @jsii.member(jsii_name="roles")
    def roles(self) -> typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The roles attached to the namespace in the form of ``{RoleArn: IRole}``.

        These roles are used to access other AWS services for ingestion, federated query, and data catalog access.

        :see: https://docs.aws.amazon.com/redshift/latest/mgmt/redshift-iam-authentication-access-control.html
        '''
        return typing.cast(typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "roles"))

    @builtins.property
    @jsii.member(jsii_name="statusFunction")
    def status_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda Function for the creation status check.'''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "statusFunction"))

    @builtins.property
    @jsii.member(jsii_name="statusLogGroup")
    def status_log_group(self) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''The CloudWatch Logs Log Group for the creation status check.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.get(self, "statusLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="statusRole")
    def status_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''The IAM Role for the creation status check.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "statusRole"))


@jsii.enum(jsii_type="aws-dsf.consumption.RedshiftServerlessNamespaceLogExport")
class RedshiftServerlessNamespaceLogExport(enum.Enum):
    '''Namespace log export types.'''

    USER_LOG = "USER_LOG"
    CONNECTION_LOG = "CONNECTION_LOG"
    USER_ACTIVITY_LOG = "USER_ACTIVITY_LOG"


@jsii.data_type(
    jsii_type="aws-dsf.consumption.RedshiftServerlessNamespaceProps",
    jsii_struct_bases=[],
    name_mapping={
        "db_name": "dbName",
        "name": "name",
        "admin_secret_key": "adminSecretKey",
        "admin_username": "adminUsername",
        "data_key": "dataKey",
        "default_iam_role": "defaultIAMRole",
        "iam_roles": "iamRoles",
        "log_exports": "logExports",
        "removal_policy": "removalPolicy",
    },
)
class RedshiftServerlessNamespaceProps:
    def __init__(
        self,
        *,
        db_name: builtins.str,
        name: builtins.str,
        admin_secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        admin_username: typing.Optional[builtins.str] = None,
        data_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
        default_iam_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        iam_roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
        log_exports: typing.Optional[typing.Sequence[RedshiftServerlessNamespaceLogExport]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''RedshiftServerlessNamespace properties.

        :param db_name: The name of the primary database that would be created in the Redshift Serverless Namespace.
        :param name: The name of the Redshift Serverless Namespace.
        :param admin_secret_key: The KMS Key used by the managed Secrets Manager Secret storing admin credentials. Default: - A new KMS Key is created
        :param admin_username: The admin username to be used. Default: - The default username is "admin"
        :param data_key: The KMS Key used to encrypt the data. Default: - A new KMS Key is created
        :param default_iam_role: Default IAM Role associated to the Redshift Serverless Namespace. Default: - No default IAM Role is associated with the Redshift Serverless Namespace
        :param iam_roles: List of IAM Roles attached to the Redshift Serverless Namespace. This list of Roles must also contain the ``defaultIamRole``. Default: - No IAM roles are associated with the Redshift Serverless Namespace
        :param log_exports: The type of logs to be exported. Default: - No logs are exported
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e20665211aa4f58835ebf3bf5be69c645727ef2afc7e6ba3f7e14b7cd4e9508)
            check_type(argname="argument db_name", value=db_name, expected_type=type_hints["db_name"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument admin_secret_key", value=admin_secret_key, expected_type=type_hints["admin_secret_key"])
            check_type(argname="argument admin_username", value=admin_username, expected_type=type_hints["admin_username"])
            check_type(argname="argument data_key", value=data_key, expected_type=type_hints["data_key"])
            check_type(argname="argument default_iam_role", value=default_iam_role, expected_type=type_hints["default_iam_role"])
            check_type(argname="argument iam_roles", value=iam_roles, expected_type=type_hints["iam_roles"])
            check_type(argname="argument log_exports", value=log_exports, expected_type=type_hints["log_exports"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "db_name": db_name,
            "name": name,
        }
        if admin_secret_key is not None:
            self._values["admin_secret_key"] = admin_secret_key
        if admin_username is not None:
            self._values["admin_username"] = admin_username
        if data_key is not None:
            self._values["data_key"] = data_key
        if default_iam_role is not None:
            self._values["default_iam_role"] = default_iam_role
        if iam_roles is not None:
            self._values["iam_roles"] = iam_roles
        if log_exports is not None:
            self._values["log_exports"] = log_exports
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def db_name(self) -> builtins.str:
        '''The name of the primary database that would be created in the Redshift Serverless Namespace.'''
        result = self._values.get("db_name")
        assert result is not None, "Required property 'db_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Redshift Serverless Namespace.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def admin_secret_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''The KMS Key used by the managed Secrets Manager Secret storing admin credentials.

        :default: - A new KMS Key is created
        '''
        result = self._values.get("admin_secret_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def admin_username(self) -> typing.Optional[builtins.str]:
        '''The admin username to be used.

        :default: - The default username is "admin"
        '''
        result = self._values.get("admin_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key]:
        '''The KMS Key used to encrypt the data.

        :default: - A new KMS Key is created
        '''
        result = self._values.get("data_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key], result)

    @builtins.property
    def default_iam_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Default IAM Role associated to the Redshift Serverless Namespace.

        :default: - No default IAM Role is associated with the Redshift Serverless Namespace
        '''
        result = self._values.get("default_iam_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def iam_roles(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IRole]]:
        '''List of IAM Roles attached to the Redshift Serverless Namespace.

        This list of Roles must also contain the ``defaultIamRole``.

        :default: - No IAM roles are associated with the Redshift Serverless Namespace
        '''
        result = self._values.get("iam_roles")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IRole]], result)

    @builtins.property
    def log_exports(
        self,
    ) -> typing.Optional[typing.List[RedshiftServerlessNamespaceLogExport]]:
        '''The type of logs to be exported.

        :default: - No logs are exported
        '''
        result = self._values.get("log_exports")
        return typing.cast(typing.Optional[typing.List[RedshiftServerlessNamespaceLogExport]], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise, the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftServerlessNamespaceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_aws_ec2_ceddda9d.IConnectable)
class RedshiftServerlessWorkgroup(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-dsf.consumption.RedshiftServerlessWorkgroup",
):
    '''Create a Redshift Serverless Workgroup.

    A default namespace would be created if none is provided.

    Example::

        workgroup = dsf.consumption.RedshiftServerlessWorkgroup(self, "RedshiftWorkgroup",
            name="example-workgroup",
            namespace=dsf.consumption.RedshiftServerlessNamespace(self, "RedshiftNamespace",
                name="example-namespace",
                db_name="defaultdb"
            )
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        namespace: RedshiftServerlessNamespace,
        base_capacity: typing.Optional[jsii.Number] = None,
        extra_security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]] = None,
        port: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: The name of the Redshift Serverless Workgroup.
        :param namespace: The Redshift Serverless Namespace associated with the Workgroup.
        :param base_capacity: The base capacity of the Redshift Serverless Workgroup in RPU. Default: - 128 RPU
        :param extra_security_groups: The extra EC2 Security Groups to associate with the Redshift Serverless Workgroup (in addition to the primary Security Group). Default: - No extra security groups are used
        :param port: The custom port to use when connecting to workgroup. Valid port ranges are 5431-5455 and 8191-8215. Default: - 5439
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param subnets: The subnets where the Redshift Serverless Workgroup is deployed. Default: - Use the private subnets of the VPC
        :param vpc: The VPC where the Redshift Serverless Workgroup is deployed. Default: - A default VPC is created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c43cdfb5b8e7c61a117237108a5d769da1e1bb98ea6ed13d0c63db6d35692af)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedshiftServerlessWorkgroupProps(
            name=name,
            namespace=namespace,
            base_capacity=base_capacity,
            extra_security_groups=extra_security_groups,
            port=port,
            removal_policy=removal_policy,
            subnets=subnets,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="accessData")
    def access_data(
        self,
        id: builtins.str,
        create_vpc_endpoint: typing.Optional[builtins.bool] = None,
    ) -> RedshiftData:
        '''Creates an instance of ``RedshiftData`` to send custom SQLs to the workgroup.

        :param id: -
        :param create_vpc_endpoint: if set to true, create interface VPC endpoint for Redshift Data API.

        :return: ``RedshiftData``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15af8a4d37e777221b9261e3079f7d2904a0c62f22da6fa88c7c574d17e8b444)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument create_vpc_endpoint", value=create_vpc_endpoint, expected_type=type_hints["create_vpc_endpoint"])
        return typing.cast(RedshiftData, jsii.invoke(self, "accessData", [id, create_vpc_endpoint]))

    @jsii.member(jsii_name="catalogTables")
    def catalog_tables(
        self,
        id: builtins.str,
        catalog_db_name: builtins.str,
        path_to_crawl: typing.Optional[builtins.str] = None,
    ) -> _DataCatalogDatabase_8a7a02f0:
        '''Creates a new Glue data catalog database with a crawler using JDBC target type to connect to the Redshift Workgroup.

        :param id: The CDK ID of the resource.
        :param catalog_db_name: The name of the Glue Database to create.
        :param path_to_crawl: The path of Redshift tables to crawl.

        :default: `/public/%``

        :return: The DataCatalogDatabase created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5587995525d675980b395c3af99fd28104185ac3a14f7902d3ab7d48bb64526f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument catalog_db_name", value=catalog_db_name, expected_type=type_hints["catalog_db_name"])
            check_type(argname="argument path_to_crawl", value=path_to_crawl, expected_type=type_hints["path_to_crawl"])
        return typing.cast(_DataCatalogDatabase_8a7a02f0, jsii.invoke(self, "catalogTables", [id, catalog_db_name, path_to_crawl]))

    @jsii.member(jsii_name="retrieveVersion")
    def retrieve_version(self) -> typing.Any:
        '''Retrieve DSF package.json version.'''
        return typing.cast(typing.Any, jsii.invoke(self, "retrieveVersion", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_OWNED_TAG")
    def DSF_OWNED_TAG(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_OWNED_TAG"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DSF_TRACKING_CODE")
    def DSF_TRACKING_CODE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "DSF_TRACKING_CODE"))

    @builtins.property
    @jsii.member(jsii_name="cfnResource")
    def cfn_resource(self) -> _aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroup:
        '''The created Redshift Serverless Workgroup.'''
        return typing.cast(_aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroup, jsii.get(self, "cfnResource"))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''Connections used by Workgroup security group.

        Used this to enable access from clients connecting to the workgroup
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="glueConnection")
    def glue_connection(self) -> _aws_cdk_aws_glue_ceddda9d.CfnConnection:
        '''The Glue Connection associated with the workgroup.

        This can be used by Glue ETL Jobs to read/write data from/to Redshift workgroup
        '''
        return typing.cast(_aws_cdk_aws_glue_ceddda9d.CfnConnection, jsii.get(self, "glueConnection"))

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> RedshiftServerlessNamespace:
        '''The associated Redshift Serverless Namespace.'''
        return typing.cast(RedshiftServerlessNamespace, jsii.get(self, "namespace"))

    @builtins.property
    @jsii.member(jsii_name="primarySecurityGroup")
    def primary_security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        '''The primary EC2 Security Group associated with the Redshift Serverless Workgroup.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "primarySecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="selectedSubnets")
    def selected_subnets(self) -> _aws_cdk_aws_ec2_ceddda9d.SelectedSubnets:
        '''The subnets where the Redshift Serverless Workgroup is deployed.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, jsii.get(self, "selectedSubnets"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC where the Redshift Serverless Workgroup is deployed.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="aws-dsf.consumption.RedshiftServerlessWorkgroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "namespace": "namespace",
        "base_capacity": "baseCapacity",
        "extra_security_groups": "extraSecurityGroups",
        "port": "port",
        "removal_policy": "removalPolicy",
        "subnets": "subnets",
        "vpc": "vpc",
    },
)
class RedshiftServerlessWorkgroupProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        namespace: RedshiftServerlessNamespace,
        base_capacity: typing.Optional[jsii.Number] = None,
        extra_security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]] = None,
        port: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
    ) -> None:
        '''RedshiftServerlessWorkgroup properties.

        :param name: The name of the Redshift Serverless Workgroup.
        :param namespace: The Redshift Serverless Namespace associated with the Workgroup.
        :param base_capacity: The base capacity of the Redshift Serverless Workgroup in RPU. Default: - 128 RPU
        :param extra_security_groups: The extra EC2 Security Groups to associate with the Redshift Serverless Workgroup (in addition to the primary Security Group). Default: - No extra security groups are used
        :param port: The custom port to use when connecting to workgroup. Valid port ranges are 5431-5455 and 8191-8215. Default: - 5439
        :param removal_policy: The removal policy when deleting the CDK resource. If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true. Otherwise, the removalPolicy is reverted to RETAIN. Default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        :param subnets: The subnets where the Redshift Serverless Workgroup is deployed. Default: - Use the private subnets of the VPC
        :param vpc: The VPC where the Redshift Serverless Workgroup is deployed. Default: - A default VPC is created
        '''
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__814334cc71c2ed316971444d75b5d1500222e931b560701b175032b0f53a6acb)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument base_capacity", value=base_capacity, expected_type=type_hints["base_capacity"])
            check_type(argname="argument extra_security_groups", value=extra_security_groups, expected_type=type_hints["extra_security_groups"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "namespace": namespace,
        }
        if base_capacity is not None:
            self._values["base_capacity"] = base_capacity
        if extra_security_groups is not None:
            self._values["extra_security_groups"] = extra_security_groups
        if port is not None:
            self._values["port"] = port
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if subnets is not None:
            self._values["subnets"] = subnets
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Redshift Serverless Workgroup.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> RedshiftServerlessNamespace:
        '''The Redshift Serverless Namespace associated with the Workgroup.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(RedshiftServerlessNamespace, result)

    @builtins.property
    def base_capacity(self) -> typing.Optional[jsii.Number]:
        '''The base capacity of the Redshift Serverless Workgroup in RPU.

        :default: - 128 RPU
        '''
        result = self._values.get("base_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def extra_security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]]:
        '''The extra EC2 Security Groups to associate with the Redshift Serverless Workgroup (in addition to the primary Security Group).

        :default: - No extra security groups are used
        '''
        result = self._values.get("extra_security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''The custom port to use when connecting to workgroup.

        Valid port ranges are 5431-5455 and 8191-8215.

        :default: - 5439
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy when deleting the CDK resource.

        If DESTROY is selected, context value ``@data-solutions-framework-on-aws/removeDataOnDestroy`` needs to be set to true.
        Otherwise, the removalPolicy is reverted to RETAIN.

        :default: - The resources are not deleted (``RemovalPolicy.RETAIN``).
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets where the Redshift Serverless Workgroup is deployed.

        :default: - Use the private subnets of the VPC
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc]:
        '''The VPC where the Redshift Serverless Workgroup is deployed.

        :default: - A default VPC is created
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftServerlessWorkgroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "RedshiftData",
    "RedshiftDataProps",
    "RedshiftServerlessNamespace",
    "RedshiftServerlessNamespaceLogExport",
    "RedshiftServerlessNamespaceProps",
    "RedshiftServerlessWorkgroup",
    "RedshiftServerlessWorkgroupProps",
]

publication.publish()

def _typecheckingstub__d6c16f956219fc8fdb9e784a5a3d784e55725facb2f1757631dd017f3942a5eb(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    cluster_id: typing.Optional[builtins.str] = None,
    create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
    execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    workgroup_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70746f1f6784f2381f3504370ee6af95f7ac82990574454ab8ed576bf5688c59(
    db_roles: typing.Sequence[builtins.str],
    target_role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1270ad3991e26b90cece045ea41b63111e3fe01f953c4bed18c350197e5ba21e(
    id: builtins.str,
    database_name: builtins.str,
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3676187b92f6742c03d35124ee5d7c1c4e0328311a5857a012dfcf4cafa2b1f6(
    id: builtins.str,
    database_name: builtins.str,
    schema: builtins.str,
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c34f05895e0ec9a0153244a7039d1fe2a3838d022d1e84b4e7a920837fee0544(
    id: builtins.str,
    database_name: builtins.str,
    schema: builtins.str,
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9300eec9bcc19e7791cba4dab6f5f59896db2f1c50740eb39fcfcf25dbebad4a(
    id: builtins.str,
    database_name: builtins.str,
    schema: builtins.str,
    role_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9e19236fe69bfe81295a236db19041243888528841ce8ea4c1421a81fd3b55d(
    id: builtins.str,
    database_name: builtins.str,
    target_table: builtins.str,
    source_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    source_prefix: builtins.str,
    ingest_additional_options: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be9c53641644b2e9b800be6da305025e12da93b6613fa02521951fb2d96cdf74(
    id: builtins.str,
    database_name: builtins.str,
    source_table: builtins.str,
    target_table: builtins.str,
    source_column_id: typing.Optional[builtins.str] = None,
    target_column_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d11c2e475c18cec3a62ed59e67e9a866dc268e471dc7ec9c6a283dac47f3954(
    id: builtins.str,
    database_name: builtins.str,
    sql: builtins.str,
    delete_sql: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d6dbe1316db9272b5422946107575b24310dd5cc4078f9c3d5cab4440f25756(
    *,
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    cluster_id: typing.Optional[builtins.str] = None,
    create_interface_vpc_endpoint: typing.Optional[builtins.bool] = None,
    execution_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SelectedSubnets, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    workgroup_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f9c7878838fb6a2d2369d6cb06e7f6babfef4ed727eeebb9bef3b2b4d54eb37(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    db_name: builtins.str,
    name: builtins.str,
    admin_secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    admin_username: typing.Optional[builtins.str] = None,
    data_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    default_iam_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    iam_roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
    log_exports: typing.Optional[typing.Sequence[RedshiftServerlessNamespaceLogExport]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e20665211aa4f58835ebf3bf5be69c645727ef2afc7e6ba3f7e14b7cd4e9508(
    *,
    db_name: builtins.str,
    name: builtins.str,
    admin_secret_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    admin_username: typing.Optional[builtins.str] = None,
    data_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.Key] = None,
    default_iam_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    iam_roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
    log_exports: typing.Optional[typing.Sequence[RedshiftServerlessNamespaceLogExport]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c43cdfb5b8e7c61a117237108a5d769da1e1bb98ea6ed13d0c63db6d35692af(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    namespace: RedshiftServerlessNamespace,
    base_capacity: typing.Optional[jsii.Number] = None,
    extra_security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]] = None,
    port: typing.Optional[jsii.Number] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15af8a4d37e777221b9261e3079f7d2904a0c62f22da6fa88c7c574d17e8b444(
    id: builtins.str,
    create_vpc_endpoint: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5587995525d675980b395c3af99fd28104185ac3a14f7902d3ab7d48bb64526f(
    id: builtins.str,
    catalog_db_name: builtins.str,
    path_to_crawl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__814334cc71c2ed316971444d75b5d1500222e931b560701b175032b0f53a6acb(
    *,
    name: builtins.str,
    namespace: RedshiftServerlessNamespace,
    base_capacity: typing.Optional[jsii.Number] = None,
    extra_security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.SecurityGroup]] = None,
    port: typing.Optional[jsii.Number] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
) -> None:
    """Type checking stubs"""
    pass
