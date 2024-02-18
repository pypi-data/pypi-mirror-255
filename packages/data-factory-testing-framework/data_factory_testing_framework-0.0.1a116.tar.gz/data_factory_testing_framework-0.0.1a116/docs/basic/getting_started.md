# Getting started

This _getting started_ focuses on novice users who are not familiar with Python or package management. It guides you through the process of downloading the data factory pipeline files, setting up a Python project and installing the framework so that you can start writing tests.

> If you are experienced with Python and package management, you can skip this page and go directly to the [repository setup](repository_setup.md) page.

## Data Factory pipeline files

The framework is designed to work with the `json` files that define your data factory pipelines and activities. You can download these files from your data factory environment as described in the [repository setup](repository_setup.md) page.

## Setting up your Python project

If you are using Visual Studio Code:

1. Create a new folder alongside the data factory pipeline files for your test project called `tests`.
2. Open the new folder in Visual Studio Code.
3. Install the framework by installing the library the terminal with pip:

   ```bash
   pip install data-factory-testing-framework
   ```

4. Install pytest as testing library. All examples in this documentation are using pytest.

   ```bash
   pip install pytest
   ```

5. Download the pipeline files from your data factory environment and place them in the project folder as described in the [repository setup](repository_setup.md) page.

Additional resources:

* [Get Started Tutorial for Python in Visual Studio Code](https://code.visualstudio.com/docs/python/python-tutorial)
* [Integrated Terminal in Visual Studio Code](https://code.visualstudio.com/docs/terminal/basics)
* [pytest: helps you write better programs — pytest documentation](https://docs.pytest.org/en/7.4.x/)

Once setup, you can read the following pages to learn how to write tests for your data factory:

1. [Initializing the framework](installing_and_initializing_framework.md) (make sure to initialize the root folder of the framework with the path to the folder containing the pipeline definitions).
2. [Activity testing](activity_testing.md)
3. [Pipeline testing](pipeline_testing.md)
