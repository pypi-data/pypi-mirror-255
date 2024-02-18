# Activity testing

The framework provides a way to test activities in isolation. This is useful when you want to test the behavior of an activity without running the entire pipeline.

Make sure to have initialized the framework before writing tests. See [Installing and initializing the framework](docs/basic/installing-and-initializing-framework.md) for more information.

Now that you have a `TestFramework` instance, you can start writing tests for your activities. A test always follows the Arrange-Act-Assert pattern:

1. **Arrange**: Get a reference to the activity you want to test and create a `PipelineRunState` instance with the input parameters and variables of the scenario you want to test.
2. **Act**: Call the `evaluate` method on the activity with the `PipelineRunState` instance. The framework will find all expressions in the activity and evaluate them using the provided state.
3. **Assert**: Verify that the output of the activity matches the expected result.

The framework automatically detects expressions and put them in a `DataFactoryElement` object. This object has a `value` property that contains the evaluated value of the expression. You can use this `value` property to assert the outcome.

## Arrange-Act-Assert

The following pipeline example is used to demonstrate how each steps of the arrange-act-assert pattern can be implemented for a single activity.

```json
{
    "name": "trigger_job_pipeline",
    "parameters": {
        "JobId": {
          "type": "String"
        }
    },
    "variables": {
        "JobName": "Job-123"
    },
    "activities": [
      {
        "name": "Trigger job",
        "type": "WebActivity",
        "typeProperties": {
          "url": {
            "type": "Expression",
            "value": "@concat(pipeline().globalParameters.BaseUrl, '/jobs')"
          },
          "method": {
            "value": "POST"
          },
          "body": {
            "type": "Expression",
            "value": {
              "JobId": "@pipeline().parameters.JobId",
              "JobName": "@variables('JobName')",
              "Version": "@activity('Get version').output.Version"
            }
          }
        }
      }
  ]
}
```

Let's write a test for validating correct evaluation of the `url` property.

## Arrange

Get a reference to the activity you want to test using the `get_activity_by_name` method on the `Pipeline` instance.

```python
pipeline = test_framework.repository.get_pipeline_by_name("trigger_job_pipeline")
activity = pipeline.get_activity_by_name("Trigger job")
```

Create a `PipelineRunState` instance with the input used in the `url` expression, so a globalParameter `BaseUrl` and a variable `JobName`.

```python
state = PipelineRunState(
    parameters=[
        RunParameter(RunParameterType.Global, "BaseUrl", "https://example.com"),
    ],
    variables=[
        PipelineRunVariable("JobName", "Job-123"),
    ])
```

> See [State](docs/basic/state.md) for a detailed explanation on how to use the `PipelineRunState` class.

## Act

Call the `evaluate` method on the `activity` with the `PipelineRunState` instance. This evaluates all expressions in the activity using the provided state and store the result in a `value` property.

```python
activity.evaluate(state)
```

The `evaluate` method might throw an exception if the expression is invalid or if the expression is missing required parameters, variables or activity outputs. Make sure to supply the required properties in the state.

## Assert

Verify that the output of the activity matches the expected result.

```python
assert "https://example.com/jobs" == activity.type_properties["url"].value
```

## Control activities

Testing control activities like `IfCondition`, `ForEach`, `Switch` and `Until` activities is useful to validate that the condition expression is evaluating correctly.  Make sure to use type hints to know the available properties of the control activity.

### Example

Given that the `IfCondition` expression looks like: `@equals(pipeline().parameters.JobId, '123')`

```python
# Arrange
activity: IfConditionActivity = pipeline.get_activity_by_name("If condition")
state = PipelineRunState(
    parameters=[
        RunParameter(RunParameterType.Pipeline, "JobId", "123"),
    ],
)

# Act
activity.evaluate(state)

# Assert
assert activity.expression.value == True
```

### Testing child activities

The child activities of a control activity can be tested by first finding the control activity and then finding the child activities. The child activities can then be tested as described in the previous section.

```python
# Arrange
activity: IfConditionActivity = pipeline.get_activity_by_name("If condition")
child_activity = activity.if_true_activities[0]  # Or loop through them by name
```

If you would like to evaluate the condition of a control activity in combination with the child activities, then write a pipeline test as described in [Pipeline testing](pipeline_testing.md).
