# Delta Live Tables Blueprint

![Capture1.PNG](images%2FCapture1.PNG)
![Capture4.PNG](images%2FCapture4.PNG)
![Capture5.PNG](images%2FCapture5.PNG)

<br />

## 📜 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Deploy](#usage)
- [Test](#test)
- [Built Using](#built_using)
- [Authors](#authors)

<br />

## 🧐 About <a name = "about"></a>
Blueprint to initialize a project with Databricks Delta Live Tables and Azure Data Lake Storage.
Resource for anyone is looking to leverage Databricks DLT in a professional and organized manner,
making it easier to follow software engineering best practice rather than relying on notebooks.

<br />

## 🏁 Getting Started <a name = "getting_started"></a>

Great news! You can sit back, relax, and forget about installing any dependencies on your machine.
To effortlessly install the dependencies listed in your pyproject.toml file, I've prepared a nifty little script just for you:
```
sh scripts/poetry_init.sh 
```

<br />

## 💻 Usage <a name="usage"></a>
To add new pipelines, you can create a new Python file and implement the 
**Pipeline** class in the pipeline.py file, which already contains abstract methods with 
implementations for the raw, bronze, and silver layers.

- A pipeline is a sequence of data processing steps that takes raw input data and transforms it into a useful output format.
- The **Pipeline** class defines a common interface for all pipelines, making it easy to add new pipelines that can be used interchangeably with existing ones.
- To implement a new pipeline, you can create a new Python file with a name that describes the pipeline (e.g., my_pipeline.py).
- Inside that file, you can define a new class that extends the pipeline.py class and implements its abstract methods.
- The raw, bronze, and silver methods in the pipeline.py class represent the different stages of data processing, each with a specific set of operations.
- By implementing these methods in your new pipeline class, you can define how the input data is transformed at each stage.

Once you've created the new class, you can import it into the 
**class_mapping.py** file and add it to the **mapper** dictionary with 
a unique name that will be used to dynamically load the class at runtime. 
For example:
``` python
from src.pipeline.my_pipeline import MyPipeline

# Mapping of class names to class objects for the Bronze layer
mapper = {
    'sample_pipeline_1': SamplePipeline1,
    'sample_pipeline_2': SamplePipeline2,
    'my_pipeline': MyPipeline,
}

``` 
Make sure to replace **'my_pipeline'** with a unique name that reflects your pipeline. 
Once you've added the new class to the dictionary, you can use it like 
any other pipeline by referencing its name when you create a new pipeline 
object. Once the context is instantiated, all the elements in the dictionary 
will be executed.

The **PipelineOrchestrator** class in pipeline_orchestrator.py file, is an object that implements 
a design pattern to orchestrate the execution of pipelines provided in the **mapper** dictionary

<br />

## 🚀 Deploy <a name = "deploy"></a>
The **databricks_deploy.sh** bash script, is used to deploy the necessary Databricks infrastructure required for running the application. 
This script will only be executed by the CICD pipelines upon approval of pull requests by the reviewers

``` yaml
  - task: Bash@3
    inputs:
      filePath: '$(System.DefaultWorkingDirectory)/infra/databricks/databricks_deploy.sh'
    env:
      DATABRICKS_HOST: $(databricks_host)
      DATABRICKS_TOKEN: $(databricks_token)
      DATABRICKS_REPO_ID: $(repo_id)
      BRANCH_NAME: $(branch_name)
      WORKING_DIRECTORY: '$(System.DefaultWorkingDirectory)'

    displayName: 'deploy databricks'
```
![Capture6.PNG](images%2FCapture6.PNG)


<br />

<br />

## 🐛 Test <a name = "test"></a>
Docker allows us to replicate the Databricks Spark environment in which the application will be executed. 
Therefore, in order to run test cases locally on your machine, you must have Docker installed. 
The test cases will be automatically executed by the pre-commit hook before any code is pushed to the remote branch:
``` yml
  - repo: local
    hooks:
      - id: tests
        name: Unit and Integration tests
        entry: docker-compose up
        language: python
        "types": [python]
        pass_filenames: false
        stages: [push]
```
<br />

You can also run the test manually by using the following command:
```
docker-compose up
```
![Capture7.PNG](images%2FCapture7.PNG)
![Capture8.PNG](images%2FCapture8.PNG)

<br />

<br />

## ⛏️ Built Using <a name = "built_using"></a>
- [Python](https://www.python.org/) | Programming language
- [Poetry](https://python-poetry.org/) | Dependency management and packaging
- [Pre-Commit](https://pre-commit.com/) | Managing and maintaining hooks
- [Azure pipelines](https://learn.microsoft.com/en-us/azure/devops/pipelines/get-started/what-is-azure-pipelines?view=azure-devops) | CI/CD
- [Bash](https://www.gnu.org/software/bash/) | Infrastructure as Code
- [Docker](https://www.docker.com/) | Containerization
- [Pyspark](https://spark.apache.org/) | Data processing
- [Databricks](https://www.databricks.com/) | Lakehouse platform
- [Databricks CLI](https://github.com/databricks/databricks-cli) | Command-line interface
- [Delta Lake](https://delta.io/) | Optimized storage layer
- [Azure Data Lake Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction) | Data Lake storage

<br />

## ✏️ Authors <a name = "authors"></a>
- Made with ❤️  by Vittorio Polverino
