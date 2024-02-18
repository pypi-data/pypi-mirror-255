# Repository setup

## Git integration

To be able to write tests for data factory, you need to have the pipeline and activity definitions available. The recommended way to do this is to sync the Data Factory instance to a git repository, so that you can create a `tests` folder in the same repository and write tests for your data factory. The git integration process can be found here:

1. [Fabric - Git integration process](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-integration-process)
2. [Azure Data Factory - Git integration process](https://learn.microsoft.com/azure/data-factory/source-control)

### Alternative for Azure Data Factory

If you want to download a single JSON file for testing purposes, you can do so by following these steps:

1. Open your Data Factory instance, and open the pipeline you want to test.
2. Click on the action ellipses
3. Click "Download support files"
4. Extract the zip file containing the pipeline definition in a folder of your choice.

> Remember the location of this folder, as you will need it to initialize the framework.

![Download support files](../images/download_support_files.png)

Once your repository is set up, you can install and initialize the framework as described in the [installing and initializing the framework](installing_and_initializing_framework.md) page.
