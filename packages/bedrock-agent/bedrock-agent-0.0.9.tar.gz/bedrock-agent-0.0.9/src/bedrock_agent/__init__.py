'''
> [!NOTE]
> This is an expiremental construct and is not affiliated with AWS Bedrock team. Things can break so do not use in production. Currently there is no suppor for `updates` of the construct but it is planned to be added soon.
> All classes are under active development and subject to non-backward compatible changes or removal in any future version. These are not subject to the Semantic Versioning model. This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

# Bedrock Agent and Bedrock Knowledge Base Constructs

See [API.md](API.md) for more information about construct.

Also see TypeScript deployment examples below. All of the examples assume you have appropriate IAM permissions for provisioning resources in AWS.

# Example - deploy agent only

This example will create an agent without Action Group and with default IAM role. If `agentResourceRoleArn` is not specified a default IAM role with no policies attached to it will be provisioned for your agent.

```python
import * as cdk from 'aws-cdk-lib';
import { BedrockAgent } from 'bedrock-agents-cdk';

const app = new cdk.App();
const stack = new cdk.Stack(app, 'BedrockAgentStack');

const agent = new BedrockAgent(stack, "BedrockAgent", {
  agentName: "BedrockAgent",
  instruction: "This is a test instruction. You were built by AWS CDK construct to answer all questions.",
})

// You can retrieve `agentId` and `agentArn` of the created agent
// back from the construct.

// const agentId = agent.agentId
// const agentArn = agent.agentArn
```

# Example - deploy knowledge base only

This example will create a knowledge base backed by Amazon OpenSearch Serverless collection that could be used without an agent. This example assumes you have already created Amazon OpenSearch Serverless collection (`collectionArn`).

**Note: The IAM role creation in this example is for illustration only. Always provion IAM roles with the least required priviliges.**

```python
import * as cdk from 'aws-cdk-lib';
import { BedrockKnowledgeBase } from 'bedrock-agents-cdk';

const app = new cdk.App();
const stack = new cdk.Stack(app, 'BedrockKnowledgeBaseStack');

const kbName = 'MyTestKnowledgeBase';
const dataSourceName = 'MyDataSource';
const collectionArn = 'arn:aws:aoss:yourCollectionRegion:yourAWSAccountId:collection/yourCollectionId';
const vectorIndexName = 'my-test-index';
const vectorFieldName = 'my-test-vector';
const textField = 'text-field';
const metadataField = 'metadata-field';
const storageConfigurationType = 'OPENSEARCH_SERVERLESS';
const dataSourceType = 'S3';
const dataSourceBucketArn = 'yourDataSourceBucketArn';

// Bedrock Knowledge Base IAM role
const kbRoleArn = new iam.Role(stack, 'BedrockKnowledgeBaseRole', {
  roleName: 'AmazonBedrockExecutionRoleForKnowledgeBase_kb_test',
  assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
  managedPolicies: [iam.ManagedPolicy.fromAwsManagedPolicyName('AdministratorAccess')],
}).roleArn;

// Create Bedrock Knowledge Base backed by OpenSearch Servereless
const knowledgeBase = new BedrockKnowledgeBase(stack, 'BedrockOpenSearchKnowledgeBase', {
  name: kbName,
  roleArn: kbRoleArn,
  storageConfiguration: {
    opensearchServerlessConfiguration: {
      collectionArn: collectionArn,
      fieldMapping: {
        metadataField: metadataField,
        textField: textField,
        vectorField: vectorFieldName,
      },
      vectorIndexName: vectorIndexName,
    },
    type: storageConfigurationType,
  },
  dataSource: {
    name: dataSourceName,
    dataSourceConfiguration: {
      s3Configuration: {
        bucketArn: dataSourceBucketArn,
      },
      type: dataSourceType,
    },
  },
});

// You can retrieve `knowledgeBaseId`, `knowledgeBaseArn`
// and `dataSourceId` of the created knowledge base
// and data source back from the construct.

// const knowledgeBaseId = knowledgeBase.knowledgeBaseId
// const knowledgeBaseArn = knowledgeBase.knowledgeBaseArn
// const dataSourceId = knowledgeBase.dataSourceId
```

# Example - deploy agent with a single action group

This example will create an agent with an Action Group and with your IAM role (`agentResourceRoleArn`). It assumes that you already have an S3 bucket and a stored JSON or yml Open API schema file that will be included in your action group. Additionaly, `pathToLambdaFile` should contain path to your function code file inside your cdk project that you want to be attached to your agent's action group. Resource-based policy statement will be attached to your Lambda function allowing Bedrock Agent to invoke it.

**Note: The IAM role creation in this example is for illustration only. Always provion IAM roles with the least required priviliges.**

```python
import * as path from 'path';
import * as cdk from 'aws-cdk-lib';
import { BedrockAgent } from 'bedrock-agents-cdk';

const app = new cdk.App();
const stack = new cdk.Stack(app, 'BedrockAgentStack');

const pathToLambdaFile = 'pathToYourLambdaFunctionFile';
const s3BucketName = 'nameOfYourS3Bucket';
const s3ObjectKey = 'nameOfYourOpenAPISchemaFileInS3Bucket';

const agentResourceRoleArn = new cdk.aws_iam.Role(stack, 'BedrockAgentRole', {
  roleName: 'AmazonBedrockExecutionRoleForAgents_agent_test',
  assumedBy: new cdk.aws_iam.ServicePrincipal('bedrock.amazonaws.com'),
  managedPolicies: [cdk.aws_iam.ManagedPolicy.fromAwsManagedPolicyName('AdministratorAccess')],
}).roleArn;

const lambdaFunctionRole = new cdk.aws_iam.Role(stack, 'BedrockAgentLambdaFunctionRole', {
  roleName: 'BedrockAgentLambdaFunctionRole',
  assumedBy: new cdk.aws_iam.ServicePrincipal('lambda.amazonaws.com'),
  managedPolicies: [cdk.aws_iam.ManagedPolicy.fromAwsManagedPolicyName('AdministratorAccess')],
});

const actionGroupExecutor = new cdk.aws_lambda.Function(stack, 'BedrockAgentActionGroupExecutor', {
  runtime: cdk.aws_lambda.Runtime.PYTHON_3_10,
  handler: 'youLambdaFileName.nameOfYourHandler',
  code: cdk.aws_lambda.Code.fromAsset(path.join(__dirname, pathToLambdaFile)),
  timeout: cdk.Duration.seconds(600),
  role: lambdaFunctionRole,
});

new BedrockAgent(stack, "BedrockAgentStack", {
  agentName: "BedrockAgent",
  instruction: "This is a test instruction. You were built by AWS CDK construct to answer all questions.",
  agentResourceRoleArn: agentResourceRoleArn,
  actionGroups: [{
    actionGroupName: "BedrockAgentActionGroup",
    actionGroupExecutor: actionGroupExecutor.functionArn,
    s3BucketName: s3BucketName,
    s3ObjectKey: s3ObjectKey,
  }]
})
```

# Example - create an agent with 2 action groups, and 2 knowledge bases that you associate with the agent

Below is an example of how you can create 2 Amazon Bedrock Knowledge Bases (1 backed by OpenSearch Serverless and 1 backed by Pinecone), Amazon Bedrock Agent with 2 action groups, and associate 2 knowledge bases to the agent.

This example assumes you have AWS Lambda function(s) ARN (`actionGroupLambdaArn`), Amazon S3 bucket name (`actionGroupS3BucketName`) with Open API json or yaml files (`actionGroupS3ObjectKey1` and `actionGroupS3ObjectKey1`) that you want your agent to use, as well as Amazon S3 bucket ARN (`dataSourceBucketArn`) where you have files that you want the Knowledge Base to perform ebeddings on. It also assumes that you already have OpenSearch Serverless ARN collection (`openSearchCollectionArn`), Pinecone index created and copied it's host name (`pineconeConnectionString`) and created and stored an API key in AWS Secrets Manager (`pineconeCredentialsSecretArn`).

Using 2 Knowledge Bases and/or 2 agent action groups is not required, this is just an example. Feel free to experiment with as many Knowledge Bases or Action Groups as you'd like.

**Note: The IAM role creation in this example is for illustration only. Always provion IAM roles with the least required priviliges.**

```python
import * as cdk from 'aws-cdk-lib';
import { BedrockAgent, BedrockKnowledgeBase } from 'bedrock-agents-cdk';

const app = new cdk.App();
const stack = new cdk.Stack(app, 'BedrockKnowledgeBaseStack');

const agentName = 'MyTestAgent';
const openSearchKbName = 'MyTestOpenSearchKnowledgeBase';
const pineconeKbName = 'MyTestPineconeKnowledgeBase';
const actionGroupName1 = 'MyTestActionGroup1';
const actionGroupName2 = 'MyTestActionGroup2';
const foundationModel = 'anthropic.claude-instant-v1';
const agentInstruction = 'This is a template instruction for my agent. You were created by AWS CDK.';
const kbInstruction = 'This is a template instruction for my knowledge base. You were created by AWS CDK.';
const openSearchCollectionArn = 'arn:aws:aoss:yourCollectionRegion:yourAWSAccountId:collection/yourCollectionId';
const pineconeCredentialsSecretArn = 'arn:aws:secretsmanager:yourSecretRegion:yourAWSAccountId:secret:yourSecretName';
const pineconeConnectionString = 'https://name-index-aa12345.svc.pineconeRegion.pinecone.io';
const vectorIndexName = 'my-test-index';
const vectorFieldName = 'my-test-vector';
const textField = 'text-field';
const metadataField = 'metadata-field';
const openSearchStorageConfigurationType = 'OPENSEARCH_SERVERLESS';
const pineconeStorageConfigurationType = 'PINECONE';
const dataSourceBucketArn = 'yourDataSourceBucketArn';
const inclusionPrefix = 'yourFolder/';
const actionGroupLambdaArn = 'yourActionGroupLambdaArn';
const actionGroupS3BucketName = 'yourActionGroupApiSchemaBucketName';
const actionGroupS3ObjectKey1 = 'yourActionGroupApiSchemaKey1';
const actionGroupS3ObjectKey2 = 'yourActionGroupApiSchemaKey2';

// Bedrock Agent IAM role
const agentResourceRoleArn = new cdk.aws_iam.Role(stack, 'BedrockAgentRole', {
  roleName: 'AmazonBedrockExecutionRoleForAgents_agent_test',
  assumedBy: new cdk.aws_iam.ServicePrincipal('bedrock.amazonaws.com'),
  managedPolicies: [cdk.aws_iam.ManagedPolicy.fromAwsManagedPolicyName('AdministratorAccess')],
}).roleArn;

// Bedrock Knowledge Base IAM role
const knowledgeBaseRoleArn = new iam.Role(stack, 'BedrockKnowledgeBaseRole', {
  roleName: 'AmazonBedrockExecutionRoleForKnowledgeBase_kb_test',
  assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
  managedPolicies: [iam.ManagedPolicy.fromAwsManagedPolicyName('AdministratorAccess')],
}).roleArn;

const myOpenSearchKb = new BedrockKnowledgeBase(stack, 'BedrockOpenSearchKnowledgeBase', {
  name: openSearchKbName,
  roleArn: knowledgeBaseRoleArn,
  storageConfiguration: {
    opensearchServerlessConfiguration: {
      collectionArn: openSearchCollectionArn,
      fieldMapping: {
        metadataField: metadataField,
        textField: textField,
        vectorField: vectorFieldName,
      },
      vectorIndexName: vectorIndexName,
    },
    type: openSearchStorageConfigurationType,
  },
  dataSource: {
    dataSourceConfiguration: {
      s3Configuration: {
        bucketArn: dataSourceBucketArn,
      },
    },
  },
});

const myPineconeKb = new BedrockKnowledgeBase(stack, 'BedrockPineconeKnowledgeBase', {
  name: pineconeKbName,
  roleArn: knowledgeBaseRoleArn,
  storageConfiguration: {
    pineconeConfiguration: {
      credentialsSecretArn: pineconeCredentialsSecretArn,
      connectionString: pineconeConnectionString,
      fieldMapping: {
        metadataField: metadataField,
        textField: textField,
      },
    },
    type: pineconeStorageConfigurationType,
  },
  dataSource: {
    dataSourceConfiguration: {
      s3Configuration: {
        bucketArn: dataSourceBucketArn,
        inclusionPrefixes: [inclusionPrefix],
      },
    },
  },
});

const agent = new BedrockAgent(stack, 'BedrockAgent', {
  agentName: agentName,
  instruction: agentInstruction,
  foundationModel: foundationModel,
  agentResourceRoleArn: agentResourceRoleArn,
  actionGroups: [{
    actionGroupName: actionGroupName1,
    actionGroupExecutor: actionGroupLambdaArn,
    s3BucketName: actionGroupS3BucketName,
    s3ObjectKey: actionGroupS3ObjectKey1,
    desription: 'This is a test action group 1 description.',
  },
  {
    actionGroupName: actionGroupName2,
    actionGroupExecutor: actionGroupLambdaArn,
    s3BucketName: actionGroupS3BucketName,
    s3ObjectKey: actionGroupS3ObjectKey2,
  }],
  knowledgeBaseAssociations: [{
    knowledgeBaseName: openSearchKbName,
    instruction: kbInstruction,
  },
  {
    knowledgeBaseName: pineconeKbName,
    instruction: kbInstruction,
  }],
});

agent.node.addDependency(myOpenSearchKb);
agent.node.addDependency(myPineconeKb);
```

# Example - deploy agent, create Amazon OpenSearch Serverless collection and knowledge base backed by it

Below is an example of how you can provision an AWS OpenSearch Serverless collection, Amazon Bedrock Agent and Amazon Bedrock Knowledge using these constructs.

This example assumes you have an AWS Lambda function ARN (`actionGroupLambdaArn`), Amazon S3 bucket name (`actionGroupS3BucketName`) with Open API json or yaml file (`actionGroupS3ObjectKey`) that you want your agent to use, as well as Amazon S3 bucket ARN (`dataSourceBucketArn`) where you have files that you want the Knowledge Base to perform ebeddings on.

You can substitute the other variables (such as `collectionName`, `vectorIndexName`, etc.) as you'd like. It is also important to download [custom_resource](https://github.com/maxtybar/bedrock-agents-cdk/tree/main/custom_resource) and [lambda_layer](https://github.com/maxtybar/bedrock-agents-cdk/tree/main/lambda_layer) folders and include it in your cdk deployment. Substitute `lambdaLayerZipFilePath` and `customResourcePythonFilePath` respectively depending on how you structure your project. This custom resource insures provisioning of OpenSearch indices.

**Note: The IAM role creation in this example is for illustration only. Always provion IAM roles with the least required priviliges.**

```python
import * as path from 'path';
import {
  App,
  Stack,
  aws_iam as iam,
  aws_opensearchserverless as oss,
  aws_lambda as lambda,
  Duration,
  CustomResource,
  aws_logs as logs,
  custom_resources,
} from 'aws-cdk-lib';
import { BedrockAgent, BedrockKnowledgeBase } from 'bedrock-agents-cdk';

const app = new App();

const stack = new Stack(app, 'BedrockAgentStack');

const agentName = 'MyTestAgent';
const kbName = 'MyTestKnowledgeBase';
const actionGroupName = 'MyTestActionGroup';
const dataSourceName = 'MyDataSource';
const foundationModel = 'anthropic.claude-instant-v1';
const agentInstruction = 'This is a template instruction for my agent. You were created by AWS CDK.';
const kbInstruction = 'This is a template instruction for my knowledge base. You were created by AWS CDK.';
const collectionName = 'my-test-collection';
const vectorIndexName = 'my-test-index';
const vectorFieldName = 'my-test-vector';
const textField = 'text-field';
const metadataField = 'metadata-field';
const storageConfigurationType = 'OPENSEARCH_SERVERLESS';
const dataSourceType = 'S3';
const dataSourceBucketArn = 'yourDataSourceBucketArn';
const actionGroupLambdaArn = 'yourActionGroupLambdaArn';
const actionGroupS3BucketName = 'yourActionGroupApiSchemaBucketName';
const actionGroupS3ObjectKey = 'yourActionGroupApiSchemaKey';
const lambdaLayerZipFilePath = '../lambda_layer/bedrock-agent-layer.zip';
const customResourcePythonFilePath = '../custom_resource';

// Bedrock Agent IAM role
const agentRoleArn = new iam.Role(stack, 'BedrockAgentRole', {
  roleName: 'AmazonBedrockExecutionRoleForAgents_agent_test',
  assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
  managedPolicies: [iam.ManagedPolicy.fromAwsManagedPolicyName('AdministratorAccess')],
}).roleArn;

// Bedrock Knowledge Base IAM role
const kbRoleArn = new iam.Role(stack, 'BedrockKnowledgeBaseRole', {
  roleName: 'AmazonBedrockExecutionRoleForKnowledgeBase_kb_test',
  assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
  managedPolicies: [iam.ManagedPolicy.fromAwsManagedPolicyName('AdministratorAccess')],
}).roleArn;

// Lambda IAM role
const customResourceRole = new iam.Role(stack, 'CustomResourceRole', {
  assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
  managedPolicies: [iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')],
});

// Opensearch encryption policy
const encryptionPolicy = new oss.CfnSecurityPolicy(stack, 'EncryptionPolicy', {
  name: 'embeddings-encryption-policy',
  type: 'encryption',
  description: `Encryption policy for ${collectionName} collection.`,
  policy: `
  {
    "Rules": [
      {
        "ResourceType": "collection",
        "Resource": ["collection/${collectionName}*"]
      }
    ],
    "AWSOwnedKey": true
  }
  `,
});

// Opensearch network policy
const networkPolicy = new oss.CfnSecurityPolicy(stack, 'NetworkPolicy', {
  name: 'embeddings-network-policy',
  type: 'network',
  description: `Network policy for ${collectionName} collection.`,
  policy: `
    [
      {
        "Rules": [
          {
            "ResourceType": "collection",
            "Resource": ["collection/${collectionName}*"]
          },
          {
            "ResourceType": "dashboard",
            "Resource": ["collection/${collectionName}*"]
          }
        ],
        "AllowFromPublic": true
      }
    ]
  `,
});

// Opensearch data access policy
const dataAccessPolicy = new oss.CfnAccessPolicy(stack, 'DataAccessPolicy', {
  name: 'embeddings-access-policy',
  type: 'data',
  description: `Data access policy for ${collectionName} collection.`,
  policy: `
    [
      {
        "Rules": [
          {
            "ResourceType": "collection",
            "Resource": ["collection/${collectionName}*"],
            "Permission": [
              "aoss:CreateCollectionItems",
              "aoss:DescribeCollectionItems",
              "aoss:DeleteCollectionItems",
              "aoss:UpdateCollectionItems"
            ]
          },
          {
            "ResourceType": "index",
            "Resource": ["index/${collectionName}*/*"],
            "Permission": [
              "aoss:CreateIndex",
              "aoss:DeleteIndex",
              "aoss:UpdateIndex",
              "aoss:DescribeIndex",
              "aoss:ReadDocument",
              "aoss:WriteDocument"
            ]
          }
        ],
        "Principal": [
          "${customResourceRole.roleArn}",
          "${kbRoleArn}"
        ]
      }
    ]
  `,
});

// Opensearch servelrless collection
const opensearchServerlessCollection = new oss.CfnCollection(stack, 'OpenSearchServerlessCollection', {
  name: collectionName,
  description: 'Collection created by CDK to explore vector embeddings and Bedrock Agents.',
  type: 'VECTORSEARCH',
});

// Allow Lambda access to OpenSearch data plane
customResourceRole.addToPolicy(
  new iam.PolicyStatement({
    resources: [opensearchServerlessCollection.attrArn],
    actions: ['aoss:APIAccessAll'],
  }),
);

// Lambda layer
const layer = new lambda.LayerVersion(stack, 'OpenSearchCustomResourceLayer', {
  code: lambda.Code.fromAsset(path.join(__dirname, lambdaLayerZipFilePath)),
  compatibleRuntimes: [lambda.Runtime.PYTHON_3_10],
  description: 'Required dependencies for Lambda',
});

// Lambda function
const onEvent = new lambda.Function(stack, 'OpenSearchCustomResourceFunction', {
  runtime: lambda.Runtime.PYTHON_3_10,
  handler: 'indices_custom_resource.on_event',
  code: lambda.Code.fromAsset(path.join(__dirname, customResourcePythonFilePath)),
  layers: [layer],
  timeout: Duration.seconds(600),
  environment: {
    COLLECTION_ENDPOINT: opensearchServerlessCollection.attrCollectionEndpoint,
    VECTOR_FIELD_NAME: vectorFieldName,
    VECTOR_INDEX_NAME: vectorIndexName,
    TEXT_FIELD: textField,
    METADATA_FIELD: metadataField,
  },
  role: customResourceRole,
});

// Custom resource provider
const provider = new custom_resources.Provider(stack, 'CustomResourceProvider', {
  onEventHandler: onEvent,
  logRetention: logs.RetentionDays.ONE_DAY,
});

// Custom resource
new CustomResource(stack, 'CustomResource', {
  serviceToken: provider.serviceToken,
});

// Create Bedrock Knowledge Base backed by OpenSearch Servereless
const myOpenSearchKb = new BedrockKnowledgeBase(stack, 'BedrockOpenSearchKnowledgeBase', {
  name: kbName,
  roleArn: kbRoleArn,
  storageConfiguration: {
    opensearchServerlessConfiguration: {
      collectionArn: opensearchServerlessCollection.attrArn,
      fieldMapping: {
        metadataField: metadataField,
        textField: textField,
        vectorField: vectorFieldName,
      },
      vectorIndexName: vectorIndexName,
    },
    type: storageConfigurationType,
  },
  dataSource: {
    name: dataSourceName,
    dataSourceConfiguration: {
      s3Configuration: {
        bucketArn: dataSourceBucketArn,
      },
      type: dataSourceType,
    },
  },
});

// Amazon Bedrock Agent and Knowledge Base backed by Opensearch Serverless
const bedrockAgent = new BedrockAgent(stack, 'BedrockAgent', {
  agentName: agentName,
  instruction: agentInstruction,
  foundationModel: foundationModel,
  agentResourceRoleArn: agentRoleArn,
  actionGroups: [{
    actionGroupName: actionGroupName,
    actionGroupExecutor: actionGroupLambdaArn,
    s3BucketName: actionGroupS3BucketName,
    s3ObjectKey: actionGroupS3ObjectKey,
  }],
  knowledgeBaseAssociations: [{
    knowledgeBaseName: kbName,
    instruction: kbInstruction,
  }],
});

opensearchServerlessCollection.node.addDependency(encryptionPolicy);
opensearchServerlessCollection.node.addDependency(networkPolicy);
opensearchServerlessCollection.node.addDependency(dataAccessPolicy);
onEvent.node.addDependency(opensearchServerlessCollection);
bedrockAgent.node.addDependency(onEvent);
bedrockAgent.node.addDependency(myOpenSearchKb);
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

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.ActionGroup",
    jsii_struct_bases=[],
    name_mapping={
        "action_group_executor": "actionGroupExecutor",
        "action_group_name": "actionGroupName",
        "s3_bucket_name": "s3BucketName",
        "s3_object_key": "s3ObjectKey",
        "description": "description",
    },
)
class ActionGroup:
    def __init__(
        self,
        *,
        action_group_executor: builtins.str,
        action_group_name: builtins.str,
        s3_bucket_name: builtins.str,
        s3_object_key: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action_group_executor: Required. Lambda function ARN that will be used in this action group. The provided Lambda function will be assigned a resource-based policy to allow access from the newly created agent.
        :param action_group_name: Required. Action group name.
        :param s3_bucket_name: Required. S3 bucket name where Open API schema is stored. Bucket must be in the same region where agent is created.
        :param s3_object_key: Required. S3 bucket key for the actual schema. Must be either JSON or yaml file.
        :param description: Optional. Description for the action group.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46cea7a8d8ecd85e51d2fa5419b69f97b5cc30a0d074654da6eec423f78c5800)
            check_type(argname="argument action_group_executor", value=action_group_executor, expected_type=type_hints["action_group_executor"])
            check_type(argname="argument action_group_name", value=action_group_name, expected_type=type_hints["action_group_name"])
            check_type(argname="argument s3_bucket_name", value=s3_bucket_name, expected_type=type_hints["s3_bucket_name"])
            check_type(argname="argument s3_object_key", value=s3_object_key, expected_type=type_hints["s3_object_key"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action_group_executor": action_group_executor,
            "action_group_name": action_group_name,
            "s3_bucket_name": s3_bucket_name,
            "s3_object_key": s3_object_key,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def action_group_executor(self) -> builtins.str:
        '''Required.

        Lambda function ARN that will be used in this action group.
        The provided Lambda function will be assigned a resource-based policy
        to allow access from the newly created agent.
        '''
        result = self._values.get("action_group_executor")
        assert result is not None, "Required property 'action_group_executor' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action_group_name(self) -> builtins.str:
        '''Required.

        Action group name.
        '''
        result = self._values.get("action_group_name")
        assert result is not None, "Required property 'action_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_bucket_name(self) -> builtins.str:
        '''Required.

        S3 bucket name where Open API schema is stored.
        Bucket must be in the same region where agent is created.
        '''
        result = self._values.get("s3_bucket_name")
        assert result is not None, "Required property 's3_bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_object_key(self) -> builtins.str:
        '''Required.

        S3 bucket key for the actual schema.
        Must be either JSON or yaml file.
        '''
        result = self._values.get("s3_object_key")
        assert result is not None, "Required property 's3_object_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Optional.

        Description for the action group.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.BaseFieldMapping",
    jsii_struct_bases=[],
    name_mapping={"metadata_field": "metadataField", "text_field": "textField"},
)
class BaseFieldMapping:
    def __init__(
        self,
        *,
        metadata_field: builtins.str,
        text_field: builtins.str,
    ) -> None:
        '''
        :param metadata_field: Required. Metadata field that you configured in your Vector DB. Bedrock will store metadata that is required to carry out source attribution and enable data ingestion and querying.
        :param text_field: Required. Text field that you configured in your Vector DB. Bedrock will store raw text from your data in chunks in this field.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fcace692f3fc153e25c781cf08780f2ecd0111fea81eaaaa7912353e1e2fb0b)
            check_type(argname="argument metadata_field", value=metadata_field, expected_type=type_hints["metadata_field"])
            check_type(argname="argument text_field", value=text_field, expected_type=type_hints["text_field"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metadata_field": metadata_field,
            "text_field": text_field,
        }

    @builtins.property
    def metadata_field(self) -> builtins.str:
        '''Required.

        Metadata field that you configured in your Vector DB.
        Bedrock will store metadata that is required to carry out source attribution
        and enable data ingestion and querying.
        '''
        result = self._values.get("metadata_field")
        assert result is not None, "Required property 'metadata_field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def text_field(self) -> builtins.str:
        '''Required.

        Text field that you configured in your Vector DB.
        Bedrock will store raw text from your data in chunks in this field.
        '''
        result = self._values.get("text_field")
        assert result is not None, "Required property 'text_field' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseFieldMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BedrockAgent(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="bedrock-agents-cdk.BedrockAgent",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        name: builtins.str,
        *,
        agent_name: builtins.str,
        instruction: builtins.str,
        action_groups: typing.Optional[typing.Sequence[typing.Union[ActionGroup, typing.Dict[builtins.str, typing.Any]]]] = None,
        agent_resource_role_arn: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        foundation_model: typing.Optional[builtins.str] = None,
        idle_session_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        knowledge_base_associations: typing.Optional[typing.Sequence[typing.Union["KnowledgeBaseAssociation", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param name: -
        :param agent_name: Required. Name of the agent.
        :param instruction: Required. Instruction for the agent. Characters length:
        :param action_groups: Optional. Action group for the agent. If specified must contain ``s3BucketName`` and ``s3ObjectKey`` with JSON or yaml Open API schema, as well as Lambda ARN for the action group executor, and action group name.
        :param agent_resource_role_arn: Optional. Resource role ARN for an agent. Role name must start with ``AmazonBedrockExecutionRoleForAgents_`` prefix and assumed by ``bedrock.amazonaws.com``. If role is not specified the default one will be created with no attached policies to it. If actionGroup is specified and the role is not, then the default created role will have an attached S3 read access to the bucket provided in the actionGroup.
        :param description: Optional. Description for the agent.
        :param foundation_model: Optional. Foundation model. Default: - "anthropic.claude-v2"
        :param idle_session_ttl_in_seconds: Optional. Max Session Time in seconds. Default: - 3600
        :param knowledge_base_associations: Optional. A list of knowledge base association objects consisting of name and instruction for the associated knowledge base.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__433b3638e8184e94646fb4453c94337ae33c6205f9ad0eb442942c32833a0589)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        props = BedrockAgentProps(
            agent_name=agent_name,
            instruction=instruction,
            action_groups=action_groups,
            agent_resource_role_arn=agent_resource_role_arn,
            description=description,
            foundation_model=foundation_model,
            idle_session_ttl_in_seconds=idle_session_ttl_in_seconds,
            knowledge_base_associations=knowledge_base_associations,
        )

        jsii.create(self.__class__, self, [scope, name, props])

    @builtins.property
    @jsii.member(jsii_name="agentArn")
    def agent_arn(self) -> builtins.str:
        '''``agentArn`` is the ARN for the created agent.'''
        return typing.cast(builtins.str, jsii.get(self, "agentArn"))

    @builtins.property
    @jsii.member(jsii_name="agentId")
    def agent_id(self) -> builtins.str:
        '''``agentId`` is the unique identifier for the created agent.'''
        return typing.cast(builtins.str, jsii.get(self, "agentId"))


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.BedrockAgentProps",
    jsii_struct_bases=[],
    name_mapping={
        "agent_name": "agentName",
        "instruction": "instruction",
        "action_groups": "actionGroups",
        "agent_resource_role_arn": "agentResourceRoleArn",
        "description": "description",
        "foundation_model": "foundationModel",
        "idle_session_ttl_in_seconds": "idleSessionTTLInSeconds",
        "knowledge_base_associations": "knowledgeBaseAssociations",
    },
)
class BedrockAgentProps:
    def __init__(
        self,
        *,
        agent_name: builtins.str,
        instruction: builtins.str,
        action_groups: typing.Optional[typing.Sequence[typing.Union[ActionGroup, typing.Dict[builtins.str, typing.Any]]]] = None,
        agent_resource_role_arn: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        foundation_model: typing.Optional[builtins.str] = None,
        idle_session_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        knowledge_base_associations: typing.Optional[typing.Sequence[typing.Union["KnowledgeBaseAssociation", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param agent_name: Required. Name of the agent.
        :param instruction: Required. Instruction for the agent. Characters length:
        :param action_groups: Optional. Action group for the agent. If specified must contain ``s3BucketName`` and ``s3ObjectKey`` with JSON or yaml Open API schema, as well as Lambda ARN for the action group executor, and action group name.
        :param agent_resource_role_arn: Optional. Resource role ARN for an agent. Role name must start with ``AmazonBedrockExecutionRoleForAgents_`` prefix and assumed by ``bedrock.amazonaws.com``. If role is not specified the default one will be created with no attached policies to it. If actionGroup is specified and the role is not, then the default created role will have an attached S3 read access to the bucket provided in the actionGroup.
        :param description: Optional. Description for the agent.
        :param foundation_model: Optional. Foundation model. Default: - "anthropic.claude-v2"
        :param idle_session_ttl_in_seconds: Optional. Max Session Time in seconds. Default: - 3600
        :param knowledge_base_associations: Optional. A list of knowledge base association objects consisting of name and instruction for the associated knowledge base.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9134fb16b7acb88ee8639dab305dfddc18fea450b4f8a0c419a1d9d92fea9908)
            check_type(argname="argument agent_name", value=agent_name, expected_type=type_hints["agent_name"])
            check_type(argname="argument instruction", value=instruction, expected_type=type_hints["instruction"])
            check_type(argname="argument action_groups", value=action_groups, expected_type=type_hints["action_groups"])
            check_type(argname="argument agent_resource_role_arn", value=agent_resource_role_arn, expected_type=type_hints["agent_resource_role_arn"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument foundation_model", value=foundation_model, expected_type=type_hints["foundation_model"])
            check_type(argname="argument idle_session_ttl_in_seconds", value=idle_session_ttl_in_seconds, expected_type=type_hints["idle_session_ttl_in_seconds"])
            check_type(argname="argument knowledge_base_associations", value=knowledge_base_associations, expected_type=type_hints["knowledge_base_associations"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "agent_name": agent_name,
            "instruction": instruction,
        }
        if action_groups is not None:
            self._values["action_groups"] = action_groups
        if agent_resource_role_arn is not None:
            self._values["agent_resource_role_arn"] = agent_resource_role_arn
        if description is not None:
            self._values["description"] = description
        if foundation_model is not None:
            self._values["foundation_model"] = foundation_model
        if idle_session_ttl_in_seconds is not None:
            self._values["idle_session_ttl_in_seconds"] = idle_session_ttl_in_seconds
        if knowledge_base_associations is not None:
            self._values["knowledge_base_associations"] = knowledge_base_associations

    @builtins.property
    def agent_name(self) -> builtins.str:
        '''Required.

        Name of the agent.
        '''
        result = self._values.get("agent_name")
        assert result is not None, "Required property 'agent_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instruction(self) -> builtins.str:
        '''Required.

        Instruction for the agent.
        Characters length:

        :max: 1200
        :min: 40
        '''
        result = self._values.get("instruction")
        assert result is not None, "Required property 'instruction' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action_groups(self) -> typing.Optional[typing.List[ActionGroup]]:
        '''Optional.

        Action group for the agent. If specified must contain ``s3BucketName`` and ``s3ObjectKey`` with JSON
        or yaml Open API schema, as well as Lambda ARN for the action group executor,
        and action group name.
        '''
        result = self._values.get("action_groups")
        return typing.cast(typing.Optional[typing.List[ActionGroup]], result)

    @builtins.property
    def agent_resource_role_arn(self) -> typing.Optional[builtins.str]:
        '''Optional.

        Resource role ARN for an agent.
        Role name must start with ``AmazonBedrockExecutionRoleForAgents_`` prefix and assumed by ``bedrock.amazonaws.com``.
        If role is not specified the default one will be created with no attached policies to it.
        If actionGroup is specified and the role is not, then the default created role will have an attached S3 read access
        to the bucket provided in the actionGroup.
        '''
        result = self._values.get("agent_resource_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Optional.

        Description for the agent.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def foundation_model(self) -> typing.Optional[builtins.str]:
        '''Optional.

        Foundation model.

        :default: - "anthropic.claude-v2"

        Example::

            - "anthropic.claude-instant-v1" or "anthropic.claude-v2"
        '''
        result = self._values.get("foundation_model")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def idle_session_ttl_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Optional.

        Max Session Time in seconds.

        :default: - 3600

        :max: 3600
        :min: 60
        :type: number
        '''
        result = self._values.get("idle_session_ttl_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def knowledge_base_associations(
        self,
    ) -> typing.Optional[typing.List["KnowledgeBaseAssociation"]]:
        '''Optional.

        A list of knowledge base association objects
        consisting of name and instruction for the associated knowledge base.

        Example::

            knowledgeBaseAssociations: [
              {
                knowledgeBaseName: "knowledge-base-name",
                instruction: "instruction-for-knowledge-base"
              }
        '''
        result = self._values.get("knowledge_base_associations")
        return typing.cast(typing.Optional[typing.List["KnowledgeBaseAssociation"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BedrockAgentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BedrockKnowledgeBase(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="bedrock-agents-cdk.BedrockKnowledgeBase",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        name_: builtins.str,
        *,
        data_source: typing.Union["DataSource", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        role_arn: builtins.str,
        storage_configuration: typing.Union[typing.Union["OpenSearchServerlessStorageConfiguration", typing.Dict[builtins.str, typing.Any]], typing.Union["RedisEnterpriseCloudStorageConfiguration", typing.Dict[builtins.str, typing.Any]], typing.Union["PineconeStorageConfiguration", typing.Dict[builtins.str, typing.Any]], typing.Union["RdsStorageConfiguration", typing.Dict[builtins.str, typing.Any]]],
        description: typing.Optional[builtins.str] = None,
        knowledge_base_configuration: typing.Optional[typing.Union["KnowledgeBaseConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param name_: -
        :param data_source: Required. Data source configuration.
        :param name: Required. Name of the KnowledgeBase.
        :param role_arn: Required. Resource role ARN for a knowledge base. Role name must start with ``AmazonBedrockExecutionRoleForKnowledgeBase_`` prefix and assumed by ``bedrock.amazonaws.com``. Role must have access to the S3 bucket used as a data source as a knowledge base. If you use OpenSearch serverless, the role must have ``aoss:APIAccessAll`` policy attached to it allowing it to make API calls against your collection's data plane. Your collection must also allow data access from KnowledgeBase role. See more here @see https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-data-access.html
        :param storage_configuration: Required. KnowledgeBase storage configuration. Has to be either ``opensearchServerlessConfiguration``, ``pineconeConfiguration``, ``redisEnterpriseCloudConfiguration`` or ``rdsConfiguration`` and respective type field mapping.
        :param description: Optional. Description for the knowledge base.
        :param knowledge_base_configuration: Optional. KnowledgeBase configuration. Default: type: "VECTOR", vectorKnowledgeBaseConfiguration: { embeddingModelArn: "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1" }
        :param removal_policy: Optional. Removal Policy. If you want to keep your Knowledge Base intact in case you destroy this CDK make sure you set removalPolicy to ``cdk.RemovalPolicy.RETAIN``. By default your Knowledge Base will be deleted along with the agent. Default: - cdk.RemovalPolicy.DESTROY
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__953a100b1dcbedee52b3d19200c86d565078a73b8d3eb711b7f8f79f8f7e5fbd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument name_", value=name_, expected_type=type_hints["name_"])
        props = BedrockKnowledgeBaseProps(
            data_source=data_source,
            name=name,
            role_arn=role_arn,
            storage_configuration=storage_configuration,
            description=description,
            knowledge_base_configuration=knowledge_base_configuration,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, name_, props])

    @builtins.property
    @jsii.member(jsii_name="dataSourceId")
    def data_source_id(self) -> builtins.str:
        '''``dataSourceId`` is the unique identifier for the created data source.'''
        return typing.cast(builtins.str, jsii.get(self, "dataSourceId"))

    @builtins.property
    @jsii.member(jsii_name="knowledgeBaseArn")
    def knowledge_base_arn(self) -> builtins.str:
        '''``knowledgeBaseArn`` is the ARN for the created knowledge base.'''
        return typing.cast(builtins.str, jsii.get(self, "knowledgeBaseArn"))

    @builtins.property
    @jsii.member(jsii_name="knowledgeBaseId")
    def knowledge_base_id(self) -> builtins.str:
        '''``knowledgeBaseId`` is the unique identifier for the created knowledge base.'''
        return typing.cast(builtins.str, jsii.get(self, "knowledgeBaseId"))


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.BedrockKnowledgeBaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "data_source": "dataSource",
        "name": "name",
        "role_arn": "roleArn",
        "storage_configuration": "storageConfiguration",
        "description": "description",
        "knowledge_base_configuration": "knowledgeBaseConfiguration",
        "removal_policy": "removalPolicy",
    },
)
class BedrockKnowledgeBaseProps:
    def __init__(
        self,
        *,
        data_source: typing.Union["DataSource", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        role_arn: builtins.str,
        storage_configuration: typing.Union[typing.Union["OpenSearchServerlessStorageConfiguration", typing.Dict[builtins.str, typing.Any]], typing.Union["RedisEnterpriseCloudStorageConfiguration", typing.Dict[builtins.str, typing.Any]], typing.Union["PineconeStorageConfiguration", typing.Dict[builtins.str, typing.Any]], typing.Union["RdsStorageConfiguration", typing.Dict[builtins.str, typing.Any]]],
        description: typing.Optional[builtins.str] = None,
        knowledge_base_configuration: typing.Optional[typing.Union["KnowledgeBaseConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''
        :param data_source: Required. Data source configuration.
        :param name: Required. Name of the KnowledgeBase.
        :param role_arn: Required. Resource role ARN for a knowledge base. Role name must start with ``AmazonBedrockExecutionRoleForKnowledgeBase_`` prefix and assumed by ``bedrock.amazonaws.com``. Role must have access to the S3 bucket used as a data source as a knowledge base. If you use OpenSearch serverless, the role must have ``aoss:APIAccessAll`` policy attached to it allowing it to make API calls against your collection's data plane. Your collection must also allow data access from KnowledgeBase role. See more here @see https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-data-access.html
        :param storage_configuration: Required. KnowledgeBase storage configuration. Has to be either ``opensearchServerlessConfiguration``, ``pineconeConfiguration``, ``redisEnterpriseCloudConfiguration`` or ``rdsConfiguration`` and respective type field mapping.
        :param description: Optional. Description for the knowledge base.
        :param knowledge_base_configuration: Optional. KnowledgeBase configuration. Default: type: "VECTOR", vectorKnowledgeBaseConfiguration: { embeddingModelArn: "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1" }
        :param removal_policy: Optional. Removal Policy. If you want to keep your Knowledge Base intact in case you destroy this CDK make sure you set removalPolicy to ``cdk.RemovalPolicy.RETAIN``. By default your Knowledge Base will be deleted along with the agent. Default: - cdk.RemovalPolicy.DESTROY
        '''
        if isinstance(data_source, dict):
            data_source = DataSource(**data_source)
        if isinstance(knowledge_base_configuration, dict):
            knowledge_base_configuration = KnowledgeBaseConfiguration(**knowledge_base_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e270bb8306c2bb7cd0bf3cdbe951c245e4260a1164b8cdc75e54118dcccda265)
            check_type(argname="argument data_source", value=data_source, expected_type=type_hints["data_source"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument storage_configuration", value=storage_configuration, expected_type=type_hints["storage_configuration"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument knowledge_base_configuration", value=knowledge_base_configuration, expected_type=type_hints["knowledge_base_configuration"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "data_source": data_source,
            "name": name,
            "role_arn": role_arn,
            "storage_configuration": storage_configuration,
        }
        if description is not None:
            self._values["description"] = description
        if knowledge_base_configuration is not None:
            self._values["knowledge_base_configuration"] = knowledge_base_configuration
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def data_source(self) -> "DataSource":
        '''Required.

        Data source configuration.
        '''
        result = self._values.get("data_source")
        assert result is not None, "Required property 'data_source' is missing"
        return typing.cast("DataSource", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Required.

        Name of the KnowledgeBase.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Required.

        Resource role ARN for a knowledge base.
        Role name must start with ``AmazonBedrockExecutionRoleForKnowledgeBase_`` prefix and assumed by ``bedrock.amazonaws.com``.
        Role must have access to the S3 bucket used as a data source as a knowledge base.
        If you use OpenSearch serverless, the role must have ``aoss:APIAccessAll`` policy attached to it
        allowing it to make API calls against your collection's data plane. Your collection
        must also allow data access from KnowledgeBase role.
        See more here @see https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-data-access.html
        '''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def storage_configuration(
        self,
    ) -> typing.Union["OpenSearchServerlessStorageConfiguration", "RedisEnterpriseCloudStorageConfiguration", "PineconeStorageConfiguration", "RdsStorageConfiguration"]:
        '''Required.

        KnowledgeBase storage configuration.
        Has to be either ``opensearchServerlessConfiguration``,
        ``pineconeConfiguration``, ``redisEnterpriseCloudConfiguration`` or ``rdsConfiguration``
        and respective type field mapping.
        '''
        result = self._values.get("storage_configuration")
        assert result is not None, "Required property 'storage_configuration' is missing"
        return typing.cast(typing.Union["OpenSearchServerlessStorageConfiguration", "RedisEnterpriseCloudStorageConfiguration", "PineconeStorageConfiguration", "RdsStorageConfiguration"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Optional.

        Description for the knowledge base.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def knowledge_base_configuration(
        self,
    ) -> typing.Optional["KnowledgeBaseConfiguration"]:
        '''Optional.

        KnowledgeBase configuration.

        :default:

        type: "VECTOR",
        vectorKnowledgeBaseConfiguration: {
        embeddingModelArn: "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
        }
        '''
        result = self._values.get("knowledge_base_configuration")
        return typing.cast(typing.Optional["KnowledgeBaseConfiguration"], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Optional.

        Removal Policy. If you want to keep your Knowledge Base intact
        in case you destroy this CDK make sure you set removalPolicy to
        ``cdk.RemovalPolicy.RETAIN``. By default your Knowledge Base will be
        deleted along with the agent.

        :default: - cdk.RemovalPolicy.DESTROY
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BedrockKnowledgeBaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.DataSource",
    jsii_struct_bases=[],
    name_mapping={
        "data_source_configuration": "dataSourceConfiguration",
        "name": "name",
    },
)
class DataSource:
    def __init__(
        self,
        *,
        data_source_configuration: typing.Union["DataSourceConfiguration", typing.Dict[builtins.str, typing.Any]],
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param data_source_configuration: Required. Data Source Configuration.
        :param name: Optional. Name for your data source. Default: - ``MyDataSource-${agentName}`` or ``MyDataSource-${knowledgeBaseName}``
        '''
        if isinstance(data_source_configuration, dict):
            data_source_configuration = DataSourceConfiguration(**data_source_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__967461aeefe598da6b155a3623ce2dd6d3c443db10532b92f2fcf09db5a6134d)
            check_type(argname="argument data_source_configuration", value=data_source_configuration, expected_type=type_hints["data_source_configuration"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "data_source_configuration": data_source_configuration,
        }
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def data_source_configuration(self) -> "DataSourceConfiguration":
        '''Required.

        Data Source Configuration.

        Example::

            dataSourceConfiguration = {
            s3Configuration: {
              bucketArn: "yourS3BucketArn",
            },
              "type": "S3"
            }
        '''
        result = self._values.get("data_source_configuration")
        assert result is not None, "Required property 'data_source_configuration' is missing"
        return typing.cast("DataSourceConfiguration", result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Optional.

        Name for your data source.

        :default: - ``MyDataSource-${agentName}`` or ``MyDataSource-${knowledgeBaseName}``
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.DataSourceConfiguration",
    jsii_struct_bases=[],
    name_mapping={"s3_configuration": "s3Configuration", "type": "type"},
)
class DataSourceConfiguration:
    def __init__(
        self,
        *,
        s3_configuration: typing.Union["S3Configuration", typing.Dict[builtins.str, typing.Any]],
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param s3_configuration: Required. S3 Configuration.
        :param type: Optional. Type of configuration. Default: - "S3"
        '''
        if isinstance(s3_configuration, dict):
            s3_configuration = S3Configuration(**s3_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c53964c8201ed47b46f2b43359bd4011b4622e4a90627c2faf69a2554fcbe3a)
            check_type(argname="argument s3_configuration", value=s3_configuration, expected_type=type_hints["s3_configuration"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "s3_configuration": s3_configuration,
        }
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def s3_configuration(self) -> "S3Configuration":
        '''Required.

        S3 Configuration.

        Example::

              s3Configuration: {
                bucketArn: "yourS3BucketArn"
              }
        '''
        result = self._values.get("s3_configuration")
        assert result is not None, "Required property 's3_configuration' is missing"
        return typing.cast("S3Configuration", result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Optional.

        Type of configuration.

        :default: - "S3"
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataSourceConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.KnowledgeBaseAssociation",
    jsii_struct_bases=[],
    name_mapping={
        "instruction": "instruction",
        "knowledge_base_name": "knowledgeBaseName",
    },
)
class KnowledgeBaseAssociation:
    def __init__(
        self,
        *,
        instruction: builtins.str,
        knowledge_base_name: builtins.str,
    ) -> None:
        '''
        :param instruction: Required. Instruction based on the design and type of information of the knowledge base. This will impact how the knowledge base interacts with the agent.
        :param knowledge_base_name: Required. Name of the existing Knowledge Base that you want to associate with the agent.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98f464ff810d38b267b5b7bbbe0be28fa27340900acc11d938f67a7dbe95477b)
            check_type(argname="argument instruction", value=instruction, expected_type=type_hints["instruction"])
            check_type(argname="argument knowledge_base_name", value=knowledge_base_name, expected_type=type_hints["knowledge_base_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instruction": instruction,
            "knowledge_base_name": knowledge_base_name,
        }

    @builtins.property
    def instruction(self) -> builtins.str:
        '''Required.

        Instruction based on the design and type of information of the knowledge base.
        This will impact how the knowledge base interacts with the agent.

        :max: 150 characters
        '''
        result = self._values.get("instruction")
        assert result is not None, "Required property 'instruction' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def knowledge_base_name(self) -> builtins.str:
        '''Required.

        Name of the existing Knowledge Base that
        you want to associate with the agent.
        '''
        result = self._values.get("knowledge_base_name")
        assert result is not None, "Required property 'knowledge_base_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KnowledgeBaseAssociation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.KnowledgeBaseConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "vector_knowledge_base_configuration": "vectorKnowledgeBaseConfiguration",
    },
)
class KnowledgeBaseConfiguration:
    def __init__(
        self,
        *,
        type: builtins.str,
        vector_knowledge_base_configuration: typing.Union["VectorKnowledgeBaseConfiguration", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param type: Required. Type of configuration. Default: - "VECTOR"
        :param vector_knowledge_base_configuration: Required. Embeddings model to convert your data into an embedding. Default: - vectorKnowledgeBaseConfiguration: { embeddingModelArn: "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1" }
        '''
        if isinstance(vector_knowledge_base_configuration, dict):
            vector_knowledge_base_configuration = VectorKnowledgeBaseConfiguration(**vector_knowledge_base_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b953bcb1fba9452f368e2de7dd2de3c0b6a0dd94d5617541c889ceb902d7f35a)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument vector_knowledge_base_configuration", value=vector_knowledge_base_configuration, expected_type=type_hints["vector_knowledge_base_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
            "vector_knowledge_base_configuration": vector_knowledge_base_configuration,
        }

    @builtins.property
    def type(self) -> builtins.str:
        '''Required.

        Type of configuration.

        :default: - "VECTOR"
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vector_knowledge_base_configuration(self) -> "VectorKnowledgeBaseConfiguration":
        '''Required.

        Embeddings model to convert your data into an embedding.

        :default:

        - vectorKnowledgeBaseConfiguration: {
        embeddingModelArn: "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
        }
        '''
        result = self._values.get("vector_knowledge_base_configuration")
        assert result is not None, "Required property 'vector_knowledge_base_configuration' is missing"
        return typing.cast("VectorKnowledgeBaseConfiguration", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KnowledgeBaseConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.OpenSearchFieldMapping",
    jsii_struct_bases=[BaseFieldMapping],
    name_mapping={
        "metadata_field": "metadataField",
        "text_field": "textField",
        "vector_field": "vectorField",
    },
)
class OpenSearchFieldMapping(BaseFieldMapping):
    def __init__(
        self,
        *,
        metadata_field: builtins.str,
        text_field: builtins.str,
        vector_field: builtins.str,
    ) -> None:
        '''
        :param metadata_field: Required. Metadata field that you configured in your Vector DB. Bedrock will store metadata that is required to carry out source attribution and enable data ingestion and querying.
        :param text_field: Required. Text field that you configured in your Vector DB. Bedrock will store raw text from your data in chunks in this field.
        :param vector_field: Required. Vector field that you configured in OpenSearch. Bedrock will store the vector embeddings in this field.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71e6545d0337a41d8b5d47a060207a41e6bd3cd14ca42e92606ba3f022a9a57f)
            check_type(argname="argument metadata_field", value=metadata_field, expected_type=type_hints["metadata_field"])
            check_type(argname="argument text_field", value=text_field, expected_type=type_hints["text_field"])
            check_type(argname="argument vector_field", value=vector_field, expected_type=type_hints["vector_field"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metadata_field": metadata_field,
            "text_field": text_field,
            "vector_field": vector_field,
        }

    @builtins.property
    def metadata_field(self) -> builtins.str:
        '''Required.

        Metadata field that you configured in your Vector DB.
        Bedrock will store metadata that is required to carry out source attribution
        and enable data ingestion and querying.
        '''
        result = self._values.get("metadata_field")
        assert result is not None, "Required property 'metadata_field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def text_field(self) -> builtins.str:
        '''Required.

        Text field that you configured in your Vector DB.
        Bedrock will store raw text from your data in chunks in this field.
        '''
        result = self._values.get("text_field")
        assert result is not None, "Required property 'text_field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vector_field(self) -> builtins.str:
        '''Required.

        Vector field that you configured in OpenSearch.
        Bedrock will store the vector embeddings in this field.
        '''
        result = self._values.get("vector_field")
        assert result is not None, "Required property 'vector_field' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenSearchFieldMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.OpenSearchServerlessConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "collection_arn": "collectionArn",
        "field_mapping": "fieldMapping",
        "vector_index_name": "vectorIndexName",
    },
)
class OpenSearchServerlessConfiguration:
    def __init__(
        self,
        *,
        collection_arn: builtins.str,
        field_mapping: typing.Union[OpenSearchFieldMapping, typing.Dict[builtins.str, typing.Any]],
        vector_index_name: builtins.str,
    ) -> None:
        '''
        :param collection_arn: Required. ARN of your OpenSearch Serverless Collection.
        :param field_mapping: Required. Field mapping consisting of ``vectorField``, ``textField`` and ``metadataField``.
        :param vector_index_name: Required. Vector index name of your OpenSearch Serverless Collection.
        '''
        if isinstance(field_mapping, dict):
            field_mapping = OpenSearchFieldMapping(**field_mapping)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dac4b1ff9969eb2768107014b4a93508611fee2ed1d0f82762c5d63050fbbb4)
            check_type(argname="argument collection_arn", value=collection_arn, expected_type=type_hints["collection_arn"])
            check_type(argname="argument field_mapping", value=field_mapping, expected_type=type_hints["field_mapping"])
            check_type(argname="argument vector_index_name", value=vector_index_name, expected_type=type_hints["vector_index_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "collection_arn": collection_arn,
            "field_mapping": field_mapping,
            "vector_index_name": vector_index_name,
        }

    @builtins.property
    def collection_arn(self) -> builtins.str:
        '''Required.

        ARN of your OpenSearch Serverless Collection.
        '''
        result = self._values.get("collection_arn")
        assert result is not None, "Required property 'collection_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def field_mapping(self) -> OpenSearchFieldMapping:
        '''Required.

        Field mapping consisting of ``vectorField``,
        ``textField`` and ``metadataField``.
        '''
        result = self._values.get("field_mapping")
        assert result is not None, "Required property 'field_mapping' is missing"
        return typing.cast(OpenSearchFieldMapping, result)

    @builtins.property
    def vector_index_name(self) -> builtins.str:
        '''Required.

        Vector index name of your OpenSearch Serverless Collection.
        '''
        result = self._values.get("vector_index_name")
        assert result is not None, "Required property 'vector_index_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenSearchServerlessConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.OpenSearchServerlessStorageConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "opensearch_serverless_configuration": "opensearchServerlessConfiguration",
        "type": "type",
    },
)
class OpenSearchServerlessStorageConfiguration:
    def __init__(
        self,
        *,
        opensearch_serverless_configuration: typing.Union[OpenSearchServerlessConfiguration, typing.Dict[builtins.str, typing.Any]],
        type: builtins.str,
    ) -> None:
        '''
        :param opensearch_serverless_configuration: Required. OpenSearch Serverless Configuration.
        :param type: Required. Has to be ``"OPENSEARCH_SERVERLESS"`` for Opensearch Serverless Configuration.
        '''
        if isinstance(opensearch_serverless_configuration, dict):
            opensearch_serverless_configuration = OpenSearchServerlessConfiguration(**opensearch_serverless_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c6b9cfa9dc85577cdae06b873d99075484f52dd50309f64b20c64c3909482c1)
            check_type(argname="argument opensearch_serverless_configuration", value=opensearch_serverless_configuration, expected_type=type_hints["opensearch_serverless_configuration"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "opensearch_serverless_configuration": opensearch_serverless_configuration,
            "type": type,
        }

    @builtins.property
    def opensearch_serverless_configuration(self) -> OpenSearchServerlessConfiguration:
        '''Required.

        OpenSearch Serverless Configuration.

        Example::

            opensearchServerlessConfiguration: {
                collectionArn: "arn:aws:opensearchserverless:us-east-1:123456789012:collection/my-collection",
                fieldMapping: {
                    textField: "text",
                    metadataField: "metadata",
                    vectorField: "vector"
                },
                vectorIndexName: "my-index",
            },
        '''
        result = self._values.get("opensearch_serverless_configuration")
        assert result is not None, "Required property 'opensearch_serverless_configuration' is missing"
        return typing.cast(OpenSearchServerlessConfiguration, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Required.

        Has to be ``"OPENSEARCH_SERVERLESS"`` for Opensearch Serverless Configuration.
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenSearchServerlessStorageConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.PineconeConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "connection_string": "connectionString",
        "credentials_secret_arn": "credentialsSecretArn",
        "field_mapping": "fieldMapping",
        "namespace": "namespace",
    },
)
class PineconeConfiguration:
    def __init__(
        self,
        *,
        connection_string: builtins.str,
        credentials_secret_arn: builtins.str,
        field_mapping: typing.Union["PineconeFieldMapping", typing.Dict[builtins.str, typing.Any]],
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_string: Required. Connection string for your Pinecone index management page.
        :param credentials_secret_arn: Required. ARN of the secret containing the API Key to use when connecting to the Pinecone database. Learn more in the link below.
        :param field_mapping: Required. Field mapping consisting of ``textField`` and ``metadataField``.
        :param namespace: Optional. Name space that will be used for writing new data to your Pinecone database.
        '''
        if isinstance(field_mapping, dict):
            field_mapping = PineconeFieldMapping(**field_mapping)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fa3ddec8992ae7a76eff1e8c9ce282862033adbb1f4430f888604de3e45197d)
            check_type(argname="argument connection_string", value=connection_string, expected_type=type_hints["connection_string"])
            check_type(argname="argument credentials_secret_arn", value=credentials_secret_arn, expected_type=type_hints["credentials_secret_arn"])
            check_type(argname="argument field_mapping", value=field_mapping, expected_type=type_hints["field_mapping"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "connection_string": connection_string,
            "credentials_secret_arn": credentials_secret_arn,
            "field_mapping": field_mapping,
        }
        if namespace is not None:
            self._values["namespace"] = namespace

    @builtins.property
    def connection_string(self) -> builtins.str:
        '''Required.

        Connection string for your Pinecone index management page.
        '''
        result = self._values.get("connection_string")
        assert result is not None, "Required property 'connection_string' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def credentials_secret_arn(self) -> builtins.str:
        '''Required.

        ARN of the secret containing the API Key to use when connecting to the Pinecone database.
        Learn more in the link below.

        :see: https://www.pinecone.io/blog/amazon-bedrock-integration/
        '''
        result = self._values.get("credentials_secret_arn")
        assert result is not None, "Required property 'credentials_secret_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def field_mapping(self) -> "PineconeFieldMapping":
        '''Required.

        Field mapping consisting of ``textField`` and ``metadataField``.
        '''
        result = self._values.get("field_mapping")
        assert result is not None, "Required property 'field_mapping' is missing"
        return typing.cast("PineconeFieldMapping", result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Optional.

        Name space that will be used for writing new data to your Pinecone database.
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PineconeConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.PineconeFieldMapping",
    jsii_struct_bases=[BaseFieldMapping],
    name_mapping={"metadata_field": "metadataField", "text_field": "textField"},
)
class PineconeFieldMapping(BaseFieldMapping):
    def __init__(
        self,
        *,
        metadata_field: builtins.str,
        text_field: builtins.str,
    ) -> None:
        '''
        :param metadata_field: Required. Metadata field that you configured in your Vector DB. Bedrock will store metadata that is required to carry out source attribution and enable data ingestion and querying.
        :param text_field: Required. Text field that you configured in your Vector DB. Bedrock will store raw text from your data in chunks in this field.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efd499f354a6e7fed3f922ebd6c85a1667272bec21764484be50a3718bb9a0d0)
            check_type(argname="argument metadata_field", value=metadata_field, expected_type=type_hints["metadata_field"])
            check_type(argname="argument text_field", value=text_field, expected_type=type_hints["text_field"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metadata_field": metadata_field,
            "text_field": text_field,
        }

    @builtins.property
    def metadata_field(self) -> builtins.str:
        '''Required.

        Metadata field that you configured in your Vector DB.
        Bedrock will store metadata that is required to carry out source attribution
        and enable data ingestion and querying.
        '''
        result = self._values.get("metadata_field")
        assert result is not None, "Required property 'metadata_field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def text_field(self) -> builtins.str:
        '''Required.

        Text field that you configured in your Vector DB.
        Bedrock will store raw text from your data in chunks in this field.
        '''
        result = self._values.get("text_field")
        assert result is not None, "Required property 'text_field' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PineconeFieldMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.PineconeStorageConfiguration",
    jsii_struct_bases=[],
    name_mapping={"pinecone_configuration": "pineconeConfiguration", "type": "type"},
)
class PineconeStorageConfiguration:
    def __init__(
        self,
        *,
        pinecone_configuration: typing.Union[PineconeConfiguration, typing.Dict[builtins.str, typing.Any]],
        type: builtins.str,
    ) -> None:
        '''
        :param pinecone_configuration: Required. Pinecone Configuration.
        :param type: Required. Has to be ``"PINECONE"`` for Pinecone Configuration.
        '''
        if isinstance(pinecone_configuration, dict):
            pinecone_configuration = PineconeConfiguration(**pinecone_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40cf7179e014b24e12bbfe81a3e8129b85da553f71a796bbf914b3ecbd4bac00)
            check_type(argname="argument pinecone_configuration", value=pinecone_configuration, expected_type=type_hints["pinecone_configuration"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "pinecone_configuration": pinecone_configuration,
            "type": type,
        }

    @builtins.property
    def pinecone_configuration(self) -> PineconeConfiguration:
        '''Required.

        Pinecone Configuration.

        Example::

            pineconeConfiguration: {
                credentialsSecretArn: 'arn:aws:secretsmanager:your-region:123456789098:secret:apiKey';
                connectionString: 'https://your-connection-string.pinecone.io';
                fieldMapping: {
                    metadataField: 'metadata-field',
                    textField: 'text-field'
                },
            },
        '''
        result = self._values.get("pinecone_configuration")
        assert result is not None, "Required property 'pinecone_configuration' is missing"
        return typing.cast(PineconeConfiguration, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Required.

        Has to be ``"PINECONE"`` for Pinecone Configuration.
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PineconeStorageConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.RdsConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "credentials_secret_arn": "credentialsSecretArn",
        "database_name": "databaseName",
        "field_mapping": "fieldMapping",
        "resource_arn": "resourceArn",
        "table_name": "tableName",
    },
)
class RdsConfiguration:
    def __init__(
        self,
        *,
        credentials_secret_arn: builtins.str,
        database_name: builtins.str,
        field_mapping: typing.Union["RdsFieldMapping", typing.Dict[builtins.str, typing.Any]],
        resource_arn: builtins.str,
        table_name: builtins.str,
    ) -> None:
        '''
        :param credentials_secret_arn: Required. The Secret ARN of you Amazon Aurora DB cluster.
        :param database_name: Required. The name of your Database.
        :param field_mapping: Required. Field mapping consisting of ``vectorField``, ``primaryKeyField``, ``textField`` and ``metadataField``.
        :param resource_arn: Required. The ARN of your Amazon Aurora DB cluster.
        :param table_name: Required. The Table Name of your Amazon Aurora DB cluster.
        '''
        if isinstance(field_mapping, dict):
            field_mapping = RdsFieldMapping(**field_mapping)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__829b30911a6c29908a5d1304c90413d537f5861cea0ee30d61a308aa39f1ba2a)
            check_type(argname="argument credentials_secret_arn", value=credentials_secret_arn, expected_type=type_hints["credentials_secret_arn"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument field_mapping", value=field_mapping, expected_type=type_hints["field_mapping"])
            check_type(argname="argument resource_arn", value=resource_arn, expected_type=type_hints["resource_arn"])
            check_type(argname="argument table_name", value=table_name, expected_type=type_hints["table_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "credentials_secret_arn": credentials_secret_arn,
            "database_name": database_name,
            "field_mapping": field_mapping,
            "resource_arn": resource_arn,
            "table_name": table_name,
        }

    @builtins.property
    def credentials_secret_arn(self) -> builtins.str:
        '''Required.

        The Secret ARN of you Amazon Aurora DB cluster.
        '''
        result = self._values.get("credentials_secret_arn")
        assert result is not None, "Required property 'credentials_secret_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_name(self) -> builtins.str:
        '''Required.

        The name of your Database.
        '''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def field_mapping(self) -> "RdsFieldMapping":
        '''Required.

        Field mapping consisting of ``vectorField``, ``primaryKeyField``,
        ``textField`` and ``metadataField``.
        '''
        result = self._values.get("field_mapping")
        assert result is not None, "Required property 'field_mapping' is missing"
        return typing.cast("RdsFieldMapping", result)

    @builtins.property
    def resource_arn(self) -> builtins.str:
        '''Required.

        The ARN of your Amazon Aurora DB cluster.
        '''
        result = self._values.get("resource_arn")
        assert result is not None, "Required property 'resource_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''Required.

        The Table Name of your Amazon Aurora DB cluster.
        '''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.RdsFieldMapping",
    jsii_struct_bases=[BaseFieldMapping],
    name_mapping={
        "metadata_field": "metadataField",
        "text_field": "textField",
        "primary_key_field": "primaryKeyField",
        "vector_field": "vectorField",
    },
)
class RdsFieldMapping(BaseFieldMapping):
    def __init__(
        self,
        *,
        metadata_field: builtins.str,
        text_field: builtins.str,
        primary_key_field: builtins.str,
        vector_field: builtins.str,
    ) -> None:
        '''
        :param metadata_field: Required. Metadata field that you configured in your Vector DB. Bedrock will store metadata that is required to carry out source attribution and enable data ingestion and querying.
        :param text_field: Required. Text field that you configured in your Vector DB. Bedrock will store raw text from your data in chunks in this field.
        :param primary_key_field: Required. The primary key that you configured in Amazon Aurora.
        :param vector_field: Required. Vector field that you configured in Amazon Aurora. Bedrock will store the vector embeddings in this field.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02d140933cb317407fa3aa48664c3f8ad8635d6eba64328e190ead3ed01fa2ff)
            check_type(argname="argument metadata_field", value=metadata_field, expected_type=type_hints["metadata_field"])
            check_type(argname="argument text_field", value=text_field, expected_type=type_hints["text_field"])
            check_type(argname="argument primary_key_field", value=primary_key_field, expected_type=type_hints["primary_key_field"])
            check_type(argname="argument vector_field", value=vector_field, expected_type=type_hints["vector_field"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metadata_field": metadata_field,
            "text_field": text_field,
            "primary_key_field": primary_key_field,
            "vector_field": vector_field,
        }

    @builtins.property
    def metadata_field(self) -> builtins.str:
        '''Required.

        Metadata field that you configured in your Vector DB.
        Bedrock will store metadata that is required to carry out source attribution
        and enable data ingestion and querying.
        '''
        result = self._values.get("metadata_field")
        assert result is not None, "Required property 'metadata_field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def text_field(self) -> builtins.str:
        '''Required.

        Text field that you configured in your Vector DB.
        Bedrock will store raw text from your data in chunks in this field.
        '''
        result = self._values.get("text_field")
        assert result is not None, "Required property 'text_field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def primary_key_field(self) -> builtins.str:
        '''Required.

        The primary key that you configured in Amazon Aurora.
        '''
        result = self._values.get("primary_key_field")
        assert result is not None, "Required property 'primary_key_field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vector_field(self) -> builtins.str:
        '''Required.

        Vector field that you configured in Amazon Aurora.
        Bedrock will store the vector embeddings in this field.
        '''
        result = self._values.get("vector_field")
        assert result is not None, "Required property 'vector_field' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsFieldMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.RdsStorageConfiguration",
    jsii_struct_bases=[],
    name_mapping={"rds_configuration": "rdsConfiguration", "type": "type"},
)
class RdsStorageConfiguration:
    def __init__(
        self,
        *,
        rds_configuration: typing.Union[RdsConfiguration, typing.Dict[builtins.str, typing.Any]],
        type: builtins.str,
    ) -> None:
        '''
        :param rds_configuration: Required. RDS Configuration.
        :param type: Required. Has to be ``"RDS"`` for RDS (Aurora) Configuration.
        '''
        if isinstance(rds_configuration, dict):
            rds_configuration = RdsConfiguration(**rds_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d869031974a1efc94f9a9af415aace4e70713b344de7e12b314c9b8e0243b7d3)
            check_type(argname="argument rds_configuration", value=rds_configuration, expected_type=type_hints["rds_configuration"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "rds_configuration": rds_configuration,
            "type": type,
        }

    @builtins.property
    def rds_configuration(self) -> RdsConfiguration:
        '''Required.

        RDS Configuration.

        Example::

            rdsConfiguration: {
                resourceArn: "arn:aws:rds:us-east-2:12345:cluster:my-aurora-cluster-1",
                databaseName: "mydbcluster",
                tableName: "mytable",
                credentialsSecretArn: "arn:aws:rds:us-east-2:12345:cluster:my-aurora-cluster-1",
                fieldMapping: {
                    vectorField: "vectorField",
                    textField: "text"
                    metadataField: "metadata",
                    primaryKeyField: "id",
                },
            },
        '''
        result = self._values.get("rds_configuration")
        assert result is not None, "Required property 'rds_configuration' is missing"
        return typing.cast(RdsConfiguration, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Required.

        Has to be ``"RDS"`` for RDS (Aurora) Configuration.
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsStorageConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.RedisEnterpriseCloudConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "credentials_secret_arn": "credentialsSecretArn",
        "endpoint_url": "endpointUrl",
        "field_mapping": "fieldMapping",
        "vector_index_name": "vectorIndexName",
    },
)
class RedisEnterpriseCloudConfiguration:
    def __init__(
        self,
        *,
        credentials_secret_arn: builtins.str,
        endpoint_url: builtins.str,
        field_mapping: typing.Union["RedisFieldMapping", typing.Dict[builtins.str, typing.Any]],
        vector_index_name: builtins.str,
    ) -> None:
        '''
        :param credentials_secret_arn: Required. ARN of the secret defining the username, password, serverCertificate, clientCertificate and clientPrivateKey to use when connecting to the Redis Enterprise Cloud database. Learn more in the link below.
        :param endpoint_url: Required. The endpoint URL for your Redis Enterprise Cloud database.
        :param field_mapping: Required. Field mapping consisting of ``vectorField``, ``textField`` and ``metadataField``.
        :param vector_index_name: Required. Vector index name of your Redis Enterprise Cloud.
        '''
        if isinstance(field_mapping, dict):
            field_mapping = RedisFieldMapping(**field_mapping)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__976d63f4469180f2cccfd4614d74528d6afdefa28bb342387b9dd61f9b8fac07)
            check_type(argname="argument credentials_secret_arn", value=credentials_secret_arn, expected_type=type_hints["credentials_secret_arn"])
            check_type(argname="argument endpoint_url", value=endpoint_url, expected_type=type_hints["endpoint_url"])
            check_type(argname="argument field_mapping", value=field_mapping, expected_type=type_hints["field_mapping"])
            check_type(argname="argument vector_index_name", value=vector_index_name, expected_type=type_hints["vector_index_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "credentials_secret_arn": credentials_secret_arn,
            "endpoint_url": endpoint_url,
            "field_mapping": field_mapping,
            "vector_index_name": vector_index_name,
        }

    @builtins.property
    def credentials_secret_arn(self) -> builtins.str:
        '''Required.

        ARN of the secret defining the username, password, serverCertificate,
        clientCertificate and clientPrivateKey to use when connecting to the Redis Enterprise Cloud database.
        Learn more in the link below.

        :see: https://docs.redis.com/latest/rc/cloud-integrations/aws-marketplace/aws-bedrock/set-up-redis/
        '''
        result = self._values.get("credentials_secret_arn")
        assert result is not None, "Required property 'credentials_secret_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def endpoint_url(self) -> builtins.str:
        '''Required.

        The endpoint URL for your Redis Enterprise Cloud database.
        '''
        result = self._values.get("endpoint_url")
        assert result is not None, "Required property 'endpoint_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def field_mapping(self) -> "RedisFieldMapping":
        '''Required.

        Field mapping consisting of ``vectorField``,
        ``textField`` and ``metadataField``.
        '''
        result = self._values.get("field_mapping")
        assert result is not None, "Required property 'field_mapping' is missing"
        return typing.cast("RedisFieldMapping", result)

    @builtins.property
    def vector_index_name(self) -> builtins.str:
        '''Required.

        Vector index name of your Redis Enterprise Cloud.
        '''
        result = self._values.get("vector_index_name")
        assert result is not None, "Required property 'vector_index_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedisEnterpriseCloudConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.RedisEnterpriseCloudStorageConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "redis_enterprise_cloud_configuration": "redisEnterpriseCloudConfiguration",
        "type": "type",
    },
)
class RedisEnterpriseCloudStorageConfiguration:
    def __init__(
        self,
        *,
        redis_enterprise_cloud_configuration: typing.Union[RedisEnterpriseCloudConfiguration, typing.Dict[builtins.str, typing.Any]],
        type: builtins.str,
    ) -> None:
        '''
        :param redis_enterprise_cloud_configuration: Required. Redis Enterprise Cloud Configuration.
        :param type: Required. Has to be ``"REDIS_ENTERPRISE_CLOUD"`` for Redis Enterprise Cloud Configuration.
        '''
        if isinstance(redis_enterprise_cloud_configuration, dict):
            redis_enterprise_cloud_configuration = RedisEnterpriseCloudConfiguration(**redis_enterprise_cloud_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__483bb467dc2e230379bb9ed6e124aa07660c06d4933dfa62551d9240bcfb35a6)
            check_type(argname="argument redis_enterprise_cloud_configuration", value=redis_enterprise_cloud_configuration, expected_type=type_hints["redis_enterprise_cloud_configuration"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "redis_enterprise_cloud_configuration": redis_enterprise_cloud_configuration,
            "type": type,
        }

    @builtins.property
    def redis_enterprise_cloud_configuration(self) -> RedisEnterpriseCloudConfiguration:
        '''Required.

        Redis Enterprise Cloud Configuration.

        Example::

            redisEnterpriseCloudConfiguration: {
                credentialsSecretArn: 'arn:aws:secretsmanager:your-region:123456789098:secret:apiKey';
                endpointUrl: 'your-endpoint-url';
                fieldMapping: {
                    metadataField: 'metadata-field',
                    textField: 'text-field',
                    vectorField: "vector"
                },
                vectorIndexName: 'your-vector-index-name',
            },
        '''
        result = self._values.get("redis_enterprise_cloud_configuration")
        assert result is not None, "Required property 'redis_enterprise_cloud_configuration' is missing"
        return typing.cast(RedisEnterpriseCloudConfiguration, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Required.

        Has to be ``"REDIS_ENTERPRISE_CLOUD"`` for Redis Enterprise Cloud Configuration.
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedisEnterpriseCloudStorageConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.RedisFieldMapping",
    jsii_struct_bases=[BaseFieldMapping],
    name_mapping={
        "metadata_field": "metadataField",
        "text_field": "textField",
        "vector_field": "vectorField",
    },
)
class RedisFieldMapping(BaseFieldMapping):
    def __init__(
        self,
        *,
        metadata_field: builtins.str,
        text_field: builtins.str,
        vector_field: builtins.str,
    ) -> None:
        '''
        :param metadata_field: Required. Metadata field that you configured in your Vector DB. Bedrock will store metadata that is required to carry out source attribution and enable data ingestion and querying.
        :param text_field: Required. Text field that you configured in your Vector DB. Bedrock will store raw text from your data in chunks in this field.
        :param vector_field: Required. Vector field that you configured in Redis Enterprise Cloud. Bedrock will store the vector embeddings in this field.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb7bbc48a955223410d5ea6099b56a49078b7cef48e0f662f77483d485c18873)
            check_type(argname="argument metadata_field", value=metadata_field, expected_type=type_hints["metadata_field"])
            check_type(argname="argument text_field", value=text_field, expected_type=type_hints["text_field"])
            check_type(argname="argument vector_field", value=vector_field, expected_type=type_hints["vector_field"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metadata_field": metadata_field,
            "text_field": text_field,
            "vector_field": vector_field,
        }

    @builtins.property
    def metadata_field(self) -> builtins.str:
        '''Required.

        Metadata field that you configured in your Vector DB.
        Bedrock will store metadata that is required to carry out source attribution
        and enable data ingestion and querying.
        '''
        result = self._values.get("metadata_field")
        assert result is not None, "Required property 'metadata_field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def text_field(self) -> builtins.str:
        '''Required.

        Text field that you configured in your Vector DB.
        Bedrock will store raw text from your data in chunks in this field.
        '''
        result = self._values.get("text_field")
        assert result is not None, "Required property 'text_field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vector_field(self) -> builtins.str:
        '''Required.

        Vector field that you configured in Redis Enterprise Cloud.
        Bedrock will store the vector embeddings in this field.
        '''
        result = self._values.get("vector_field")
        assert result is not None, "Required property 'vector_field' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedisFieldMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.S3Configuration",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_arn": "bucketArn",
        "inclusion_prefixes": "inclusionPrefixes",
    },
)
class S3Configuration:
    def __init__(
        self,
        *,
        bucket_arn: builtins.str,
        inclusion_prefixes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param bucket_arn: Required. S3 bucket with files that you want to create embeddings on for agent to make search on.
        :param inclusion_prefixes: Optional. Prefix for a bucket if your files located in a folder. If you have a folder ``files``inside the bucket, and the folder contains files you want to perform search on, then use ``[files/]`` as an ``inclusionPrefixes``.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68cdb2d2f743551455e377de601ccdf2463fd4cab0f86ecc835e3bbe1dcb2b43)
            check_type(argname="argument bucket_arn", value=bucket_arn, expected_type=type_hints["bucket_arn"])
            check_type(argname="argument inclusion_prefixes", value=inclusion_prefixes, expected_type=type_hints["inclusion_prefixes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket_arn": bucket_arn,
        }
        if inclusion_prefixes is not None:
            self._values["inclusion_prefixes"] = inclusion_prefixes

    @builtins.property
    def bucket_arn(self) -> builtins.str:
        '''Required.

        S3 bucket with files that you want to create embeddings
        on for agent to make search on.
        '''
        result = self._values.get("bucket_arn")
        assert result is not None, "Required property 'bucket_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def inclusion_prefixes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Optional.

        Prefix for a bucket if your files located in a folder.
        If you have a folder ``files``inside the bucket,
        and the folder contains files you want to perform
        search on, then use ``[files/]`` as an ``inclusionPrefixes``.
        '''
        result = self._values.get("inclusion_prefixes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3Configuration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="bedrock-agents-cdk.VectorKnowledgeBaseConfiguration",
    jsii_struct_bases=[],
    name_mapping={"embedding_model_arn": "embeddingModelArn"},
)
class VectorKnowledgeBaseConfiguration:
    def __init__(self, *, embedding_model_arn: builtins.str) -> None:
        '''
        :param embedding_model_arn: Required. Embeddings model to convert your data into an embedding. Default: - "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37189a63657cbca5240e27a8fe7a4986562f75691b4f65d8f92eee06b1b1c791)
            check_type(argname="argument embedding_model_arn", value=embedding_model_arn, expected_type=type_hints["embedding_model_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "embedding_model_arn": embedding_model_arn,
        }

    @builtins.property
    def embedding_model_arn(self) -> builtins.str:
        '''Required.

        Embeddings model to convert your data into an embedding.

        :default: - "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
        '''
        result = self._values.get("embedding_model_arn")
        assert result is not None, "Required property 'embedding_model_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VectorKnowledgeBaseConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ActionGroup",
    "BaseFieldMapping",
    "BedrockAgent",
    "BedrockAgentProps",
    "BedrockKnowledgeBase",
    "BedrockKnowledgeBaseProps",
    "DataSource",
    "DataSourceConfiguration",
    "KnowledgeBaseAssociation",
    "KnowledgeBaseConfiguration",
    "OpenSearchFieldMapping",
    "OpenSearchServerlessConfiguration",
    "OpenSearchServerlessStorageConfiguration",
    "PineconeConfiguration",
    "PineconeFieldMapping",
    "PineconeStorageConfiguration",
    "RdsConfiguration",
    "RdsFieldMapping",
    "RdsStorageConfiguration",
    "RedisEnterpriseCloudConfiguration",
    "RedisEnterpriseCloudStorageConfiguration",
    "RedisFieldMapping",
    "S3Configuration",
    "VectorKnowledgeBaseConfiguration",
]

publication.publish()

def _typecheckingstub__46cea7a8d8ecd85e51d2fa5419b69f97b5cc30a0d074654da6eec423f78c5800(
    *,
    action_group_executor: builtins.str,
    action_group_name: builtins.str,
    s3_bucket_name: builtins.str,
    s3_object_key: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fcace692f3fc153e25c781cf08780f2ecd0111fea81eaaaa7912353e1e2fb0b(
    *,
    metadata_field: builtins.str,
    text_field: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__433b3638e8184e94646fb4453c94337ae33c6205f9ad0eb442942c32833a0589(
    scope: _constructs_77d1e7e8.Construct,
    name: builtins.str,
    *,
    agent_name: builtins.str,
    instruction: builtins.str,
    action_groups: typing.Optional[typing.Sequence[typing.Union[ActionGroup, typing.Dict[builtins.str, typing.Any]]]] = None,
    agent_resource_role_arn: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    foundation_model: typing.Optional[builtins.str] = None,
    idle_session_ttl_in_seconds: typing.Optional[jsii.Number] = None,
    knowledge_base_associations: typing.Optional[typing.Sequence[typing.Union[KnowledgeBaseAssociation, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9134fb16b7acb88ee8639dab305dfddc18fea450b4f8a0c419a1d9d92fea9908(
    *,
    agent_name: builtins.str,
    instruction: builtins.str,
    action_groups: typing.Optional[typing.Sequence[typing.Union[ActionGroup, typing.Dict[builtins.str, typing.Any]]]] = None,
    agent_resource_role_arn: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    foundation_model: typing.Optional[builtins.str] = None,
    idle_session_ttl_in_seconds: typing.Optional[jsii.Number] = None,
    knowledge_base_associations: typing.Optional[typing.Sequence[typing.Union[KnowledgeBaseAssociation, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__953a100b1dcbedee52b3d19200c86d565078a73b8d3eb711b7f8f79f8f7e5fbd(
    scope: _constructs_77d1e7e8.Construct,
    name_: builtins.str,
    *,
    data_source: typing.Union[DataSource, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    role_arn: builtins.str,
    storage_configuration: typing.Union[typing.Union[OpenSearchServerlessStorageConfiguration, typing.Dict[builtins.str, typing.Any]], typing.Union[RedisEnterpriseCloudStorageConfiguration, typing.Dict[builtins.str, typing.Any]], typing.Union[PineconeStorageConfiguration, typing.Dict[builtins.str, typing.Any]], typing.Union[RdsStorageConfiguration, typing.Dict[builtins.str, typing.Any]]],
    description: typing.Optional[builtins.str] = None,
    knowledge_base_configuration: typing.Optional[typing.Union[KnowledgeBaseConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e270bb8306c2bb7cd0bf3cdbe951c245e4260a1164b8cdc75e54118dcccda265(
    *,
    data_source: typing.Union[DataSource, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    role_arn: builtins.str,
    storage_configuration: typing.Union[typing.Union[OpenSearchServerlessStorageConfiguration, typing.Dict[builtins.str, typing.Any]], typing.Union[RedisEnterpriseCloudStorageConfiguration, typing.Dict[builtins.str, typing.Any]], typing.Union[PineconeStorageConfiguration, typing.Dict[builtins.str, typing.Any]], typing.Union[RdsStorageConfiguration, typing.Dict[builtins.str, typing.Any]]],
    description: typing.Optional[builtins.str] = None,
    knowledge_base_configuration: typing.Optional[typing.Union[KnowledgeBaseConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__967461aeefe598da6b155a3623ce2dd6d3c443db10532b92f2fcf09db5a6134d(
    *,
    data_source_configuration: typing.Union[DataSourceConfiguration, typing.Dict[builtins.str, typing.Any]],
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c53964c8201ed47b46f2b43359bd4011b4622e4a90627c2faf69a2554fcbe3a(
    *,
    s3_configuration: typing.Union[S3Configuration, typing.Dict[builtins.str, typing.Any]],
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98f464ff810d38b267b5b7bbbe0be28fa27340900acc11d938f67a7dbe95477b(
    *,
    instruction: builtins.str,
    knowledge_base_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b953bcb1fba9452f368e2de7dd2de3c0b6a0dd94d5617541c889ceb902d7f35a(
    *,
    type: builtins.str,
    vector_knowledge_base_configuration: typing.Union[VectorKnowledgeBaseConfiguration, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71e6545d0337a41d8b5d47a060207a41e6bd3cd14ca42e92606ba3f022a9a57f(
    *,
    metadata_field: builtins.str,
    text_field: builtins.str,
    vector_field: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dac4b1ff9969eb2768107014b4a93508611fee2ed1d0f82762c5d63050fbbb4(
    *,
    collection_arn: builtins.str,
    field_mapping: typing.Union[OpenSearchFieldMapping, typing.Dict[builtins.str, typing.Any]],
    vector_index_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c6b9cfa9dc85577cdae06b873d99075484f52dd50309f64b20c64c3909482c1(
    *,
    opensearch_serverless_configuration: typing.Union[OpenSearchServerlessConfiguration, typing.Dict[builtins.str, typing.Any]],
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fa3ddec8992ae7a76eff1e8c9ce282862033adbb1f4430f888604de3e45197d(
    *,
    connection_string: builtins.str,
    credentials_secret_arn: builtins.str,
    field_mapping: typing.Union[PineconeFieldMapping, typing.Dict[builtins.str, typing.Any]],
    namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efd499f354a6e7fed3f922ebd6c85a1667272bec21764484be50a3718bb9a0d0(
    *,
    metadata_field: builtins.str,
    text_field: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40cf7179e014b24e12bbfe81a3e8129b85da553f71a796bbf914b3ecbd4bac00(
    *,
    pinecone_configuration: typing.Union[PineconeConfiguration, typing.Dict[builtins.str, typing.Any]],
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__829b30911a6c29908a5d1304c90413d537f5861cea0ee30d61a308aa39f1ba2a(
    *,
    credentials_secret_arn: builtins.str,
    database_name: builtins.str,
    field_mapping: typing.Union[RdsFieldMapping, typing.Dict[builtins.str, typing.Any]],
    resource_arn: builtins.str,
    table_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02d140933cb317407fa3aa48664c3f8ad8635d6eba64328e190ead3ed01fa2ff(
    *,
    metadata_field: builtins.str,
    text_field: builtins.str,
    primary_key_field: builtins.str,
    vector_field: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d869031974a1efc94f9a9af415aace4e70713b344de7e12b314c9b8e0243b7d3(
    *,
    rds_configuration: typing.Union[RdsConfiguration, typing.Dict[builtins.str, typing.Any]],
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__976d63f4469180f2cccfd4614d74528d6afdefa28bb342387b9dd61f9b8fac07(
    *,
    credentials_secret_arn: builtins.str,
    endpoint_url: builtins.str,
    field_mapping: typing.Union[RedisFieldMapping, typing.Dict[builtins.str, typing.Any]],
    vector_index_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__483bb467dc2e230379bb9ed6e124aa07660c06d4933dfa62551d9240bcfb35a6(
    *,
    redis_enterprise_cloud_configuration: typing.Union[RedisEnterpriseCloudConfiguration, typing.Dict[builtins.str, typing.Any]],
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb7bbc48a955223410d5ea6099b56a49078b7cef48e0f662f77483d485c18873(
    *,
    metadata_field: builtins.str,
    text_field: builtins.str,
    vector_field: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68cdb2d2f743551455e377de601ccdf2463fd4cab0f86ecc835e3bbe1dcb2b43(
    *,
    bucket_arn: builtins.str,
    inclusion_prefixes: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37189a63657cbca5240e27a8fe7a4986562f75691b4f65d8f92eee06b1b1c791(
    *,
    embedding_model_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
