## Delta Live Tables Blueprint
to do
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
to do

<br />

## 🏁 Getting Started <a name = "getting_started"></a>

Good news, you don't need to install any dependencies on your machine. 
Poetry allows us to manage dependencies and packaging in Python

To install the dependencies listed in your pyproject.toml file, use the following script:

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
**class_mapping.py** file and add it to the **class_names** dictionary with 
a unique name that will be used to dynamically load the class at runtime. 
For example:
``` python
from src.pipeline.my_pipeline import MyPipeline

# Mapping of class names to class objects for the Bronze layer
class_names = {
    'contact': Contact,
    'email': Email,
    'hype_casestatus': HypeCasestatus,
    'hype_category': HypeCategory,
    'hype_corebankingstatus': HypeCorebankingStatus,
    'hype_emoneyaccount': HypeEmoneyaccount,
    'hype_pack': HypePack,
    'hype_product': HypeProduct,
    'hype_statustransitionlog': HypeStatustransitionlog,
    'hype_subcategory': HypeSubcategory,
    'hype_tag': HypeTag,
    'incident': Incident,
    'queue': Queue,
    'systemuser': Systemuser,
    'team': Team,
    'my_pipeline': MyPipeline,
}

``` 
Make sure to replace **'my_pipeline'** with a unique name that reflects your pipeline. 
Once you've added the new class to the dictionary, you can use it like 
any other pipeline by referencing its name when you create a new pipeline 
object. Once the context is instantiated, all the elements in the dictionary 
will be executed.

The **Context** class in context.py file, is an object that implements 
a strategy pattern to execute a specific set of functions based on the 
value of the layer configuration setting. 

The main purpose of the class is to create a list of strategy objects based 
on the names and corresponding classes provided in the **class_names** dictionary.

Overall, the Context class provides a flexible and extensible way to perform 
data processing tasks based on the specific needs of a project or application.

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