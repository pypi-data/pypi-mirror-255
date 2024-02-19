# AWS AppConfig Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

For a high level overview of what AWS AppConfig is and how it works, please take a look here:
[What is AWS AppConfig?](https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html)

## Basic Hosted Configuration Use Case

> The main way most AWS AppConfig users utilize the service is through hosted configuration, which involves storing
> configuration data directly within AWS AppConfig.

An example use case:

```python
app = appconfig.Application(self, "MyApp")
env = appconfig.Environment(self, "MyEnv",
    application=app
)

appconfig.HostedConfiguration(self, "MyHostedConfig",
    application=app,
    deploy_to=[env],
    content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content.")
)
```

This will create the application and environment for your configuration and then deploy your configuration to the
specified environment.

For more information about what these resources are: [Creating feature flags and free form configuration data in AWS AppConfig](https://docs.aws.amazon.com/appconfig/latest/userguide/creating-feature-flags-and-configuration-data.html).

For more information about deploying configuration: [Deploying feature flags and configuration data in AWS AppConfig](https://docs.aws.amazon.com/appconfig/latest/userguide/deploying-feature-flags.html)

---


For an in-depth walkthrough of specific resources and how to use them, please take a look at the following sections.

## Application

[AWS AppConfig Application Documentation](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-namespace.html)

In AWS AppConfig, an application is simply an organizational
construct like a folder. Configurations and environments are
associated with the application.

When creating an application through CDK, the name and
description of an application are optional.

Create a simple application:

```python
appconfig.Application(self, "MyApplication")
```

## Environment

[AWS AppConfig Environment Documentation](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-environment.html)

Basic environment with monitors:

```python
# application: appconfig.Application
# alarm: cloudwatch.Alarm
# composite_alarm: cloudwatch.CompositeAlarm


appconfig.Environment(self, "MyEnvironment",
    application=application,
    monitors=[
        appconfig.Monitor.from_cloud_watch_alarm(alarm),
        appconfig.Monitor.from_cloud_watch_alarm(composite_alarm)
    ]
)
```

Environment monitors also support L1 `CfnEnvironment.MonitorsProperty` constructs through the `fromCfnMonitorsProperty` method.
However, this is not the recommended approach for CloudWatch alarms because a role will not be auto-generated if not provided.

## Deployment Strategy

[AWS AppConfig Deployment Strategy Documentation](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-deployment-strategy.html)

A deployment strategy defines how a configuration will roll out. The roll out is defined by four parameters: deployment type,
growth factor, deployment duration, and final bake time.

Deployment strategy with predefined values:

```python
appconfig.DeploymentStrategy(self, "MyDeploymentStrategy",
    rollout_strategy=appconfig.RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
)
```

Deployment strategy with custom values:

```python
appconfig.DeploymentStrategy(self, "MyDeploymentStrategy",
    rollout_strategy=appconfig.RolloutStrategy.linear(
        growth_factor=20,
        deployment_duration=Duration.minutes(30),
        final_bake_time=Duration.minutes(30)
    )
)
```

Referencing a deployment strategy by ID:

```python
appconfig.DeploymentStrategy.from_deployment_strategy_id(self, "MyImportedDeploymentStrategy", appconfig.DeploymentStrategyId.from_string("abc123"))
```

Referencing an AWS AppConfig predefined deployment strategy by ID:

```python
appconfig.DeploymentStrategy.from_deployment_strategy_id(self, "MyImportedPredefinedDeploymentStrategy", appconfig.DeploymentStrategyId.CANARY_10_PERCENT_20_MINUTES)
```

## Configuration

A configuration is a higher-level construct that can either be a `HostedConfiguration` (stored internally through AWS
AppConfig) or a `SourcedConfiguration` (stored in an Amazon S3 bucket, AWS Secrets Manager secrets, Systems Manager (SSM)
Parameter Store parameters, SSM documents, or AWS CodePipeline). This construct manages deployments on creation.

### HostedConfiguration

A hosted configuration represents configuration stored in the AWS AppConfig hosted configuration store. A hosted configuration
takes in the configuration content and associated AWS AppConfig application. On construction of a hosted configuration, the
configuration is deployed.

You can define hosted configuration content using any of the following ConfigurationContent methods:

* `fromFile` - Defines the hosted configuration content from a file (you can specify a relative path). The content type will
  be determined by the file extension unless specified.

```python
# application: appconfig.Application


appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_file("config.json")
)
```

* `fromInlineText` - Defines the hosted configuration from inline text. The content type will be set as `text/plain`.

```python
# application: appconfig.Application


appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content.")
)
```

* `fromInlineJson` - Defines the hosted configuration from inline JSON. The content type will be set as `application/json` unless specified.

```python
# application: appconfig.Application


appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_inline_json("{}")
)
```

* `fromInlineYaml` - Defines the hosted configuration from inline YAML. The content type will be set as `application/x-yaml`.

```python
# application: appconfig.Application


appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_inline_yaml("MyConfig: This is my content.")
)
```

* `fromInline` - Defines the hosted configuration from user-specified content types. The content type will be set as `application/octet-stream` unless specified.

```python
# application: appconfig.Application


appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_inline("This is my configuration content.")
)
```

AWS AppConfig supports the following types of configuration profiles.

* **[Feature flag](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile-feature-flags.html)**: Use a feature flag configuration to turn on new features that require a timely deployment, such as a product launch or announcement.
* **[Freeform](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-free-form-configurations-creating.html)**: Use a freeform configuration to carefully introduce changes to your application.

A hosted configuration with type:

```python
# application: appconfig.Application


appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
    type=appconfig.ConfigurationType.FEATURE_FLAGS
)
```

When you create a configuration and configuration profile, you can specify up to two validators. A validator ensures that your
configuration data is syntactically and semantically correct. You can create validators in either JSON Schema or as an AWS
Lambda function.
See [About validators](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile.html#appconfig-creating-configuration-and-profile-validators) for more information.

When you import a JSON Schema validator from a file, you can pass in a relative path.

A hosted configuration with validators:

```python
# application: appconfig.Application
# fn: lambda.Function


appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
    validators=[
        appconfig.JsonSchemaValidator.from_file("schema.json"),
        appconfig.LambdaValidator.from_function(fn)
    ]
)
```

You can attach a deployment strategy (as described in the previous section) to your configuration to specify how you want your
configuration to roll out.

A hosted configuration with a deployment strategy:

```python
# application: appconfig.Application


appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
    deployment_strategy=appconfig.DeploymentStrategy(self, "MyDeploymentStrategy",
        rollout_strategy=appconfig.RolloutStrategy.linear(
            growth_factor=15,
            deployment_duration=Duration.minutes(30),
            final_bake_time=Duration.minutes(15)
        )
    )
)
```

The `deployTo` parameter is used to specify which environments to deploy the configuration to. If this parameter is not
specified, there will not be a deployment.

A hosted configuration with `deployTo`:

```python
# application: appconfig.Application
# env: appconfig.Environment


appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
    deploy_to=[env]
)
```

### SourcedConfiguration

A sourced configuration represents configuration stored in any of the following:

* Amazon S3 bucket
* AWS Secrets Manager secret
* Systems Manager
* (SSM) Parameter Store parameter
* SSM document
* AWS CodePipeline.

A sourced configuration takes in the location source
construct and optionally a version number to deploy. On construction of a sourced configuration, the configuration is deployed
only if a version number is specified.

### S3

Use an Amazon S3 bucket to store a configuration.

```python
# application: appconfig.Application


bucket = s3.Bucket(self, "MyBucket",
    versioned=True
)

appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_bucket(bucket, "path/to/file.json")
)
```

Use an encrypted bucket:

```python
# application: appconfig.Application


bucket = s3.Bucket(self, "MyBucket",
    versioned=True,
    encryption=s3.BucketEncryption.KMS
)

appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_bucket(bucket, "path/to/file.json")
)
```

### AWS Secrets Manager secret

Use a Secrets Manager secret to store a configuration.

```python
# application: appconfig.Application
# secret: secrets.Secret


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_secret(secret)
)
```

### SSM Parameter Store parameter

Use an SSM parameter to store a configuration.

```python
# application: appconfig.Application
# parameter: ssm.StringParameter


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_parameter(parameter),
    version_number="1"
)
```

### SSM document

Use an SSM document to store a configuration.

```python
# application: appconfig.Application
# document: ssm.CfnDocument


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_cfn_document(document)
)
```

### AWS CodePipeline

Use an AWS CodePipeline pipeline to store a configuration.

```python
# application: appconfig.Application
# pipeline: codepipeline.Pipeline


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_pipeline(pipeline)
)
```

Similar to a hosted configuration, a sourced configuration can optionally take in a type, validators, a `deployTo` parameter, and a deployment strategy.

A sourced configuration with type:

```python
# application: appconfig.Application
# bucket: s3.Bucket


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_bucket(bucket, "path/to/file.json"),
    type=appconfig.ConfigurationType.FEATURE_FLAGS,
    name="MyConfig",
    description="This is my sourced configuration from CDK."
)
```

A sourced configuration with validators:

```python
# application: appconfig.Application
# bucket: s3.Bucket
# fn: lambda.Function


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_bucket(bucket, "path/to/file.json"),
    validators=[
        appconfig.JsonSchemaValidator.from_file("schema.json"),
        appconfig.LambdaValidator.from_function(fn)
    ]
)
```

A sourced configuration with a deployment strategy:

```python
# application: appconfig.Application
# bucket: s3.Bucket


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_bucket(bucket, "path/to/file.json"),
    deployment_strategy=appconfig.DeploymentStrategy(self, "MyDeploymentStrategy",
        rollout_strategy=appconfig.RolloutStrategy.linear(
            growth_factor=15,
            deployment_duration=Duration.minutes(30),
            final_bake_time=Duration.minutes(15)
        )
    )
)
```

## Extension

An extension augments your ability to inject logic or behavior at different points during the AWS AppConfig workflow of
creating or deploying a configuration.
See: https://docs.aws.amazon.com/appconfig/latest/userguide/working-with-appconfig-extensions.html

### AWS Lambda destination

Use an AWS Lambda as the event destination for an extension.

```python
# fn: lambda.Function


appconfig.Extension(self, "MyExtension",
    actions=[
        appconfig.Action(
            action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
            event_destination=appconfig.LambdaDestination(fn)
        )
    ]
)
```

Lambda extension with parameters:

```python
# fn: lambda.Function


appconfig.Extension(self, "MyExtension",
    actions=[
        appconfig.Action(
            action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
            event_destination=appconfig.LambdaDestination(fn)
        )
    ],
    parameters=[
        appconfig.Parameter.required("testParam", "true"),
        appconfig.Parameter.not_required("testNotRequiredParam")
    ]
)
```

### Amazon Simple Queue Service (SQS) destination

Use a queue as the event destination for an extension.

```python
# queue: sqs.Queue


appconfig.Extension(self, "MyExtension",
    actions=[
        appconfig.Action(
            action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
            event_destination=appconfig.SqsDestination(queue)
        )
    ]
)
```

### Amazon Simple Notification Service (SNS) destination

Use an SNS topic as the event destination for an extension.

```python
# topic: sns.Topic


appconfig.Extension(self, "MyExtension",
    actions=[
        appconfig.Action(
            action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
            event_destination=appconfig.SnsDestination(topic)
        )
    ]
)
```

### Amazon EventBridge destination

Use the default event bus as the event destination for an extension.

```python
bus = events.EventBus.from_event_bus_name(self, "MyEventBus", "default")

appconfig.Extension(self, "MyExtension",
    actions=[
        appconfig.Action(
            action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
            event_destination=appconfig.EventBridgeDestination(bus)
        )
    ]
)
```

You can also add extensions and their associations directly by calling `onDeploymentComplete()` or any other action point
method on the AWS AppConfig application, configuration, or environment resource. To add an association to an existing
extension, you can call `addExtension()` on the resource.

Adding an association to an AWS AppConfig application:

```python
# application: appconfig.Application
# extension: appconfig.Extension
# lambda_destination: appconfig.LambdaDestination


application.add_extension(extension)
application.on_deployment_complete(lambda_destination)
```
