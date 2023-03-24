"""
Module containing a collection of classes used throughout the project.
Include here all classes that may be dynamically loaded based on their name as a string.
"""
from src.pipelines.sample_pipeline_1 import SamplePipeline1

# Mapping of class names to class objects for the Bronze layer
mapper = {
    'sample_pipeline_1': SamplePipeline1,
    'sample_pipeline_2': SamplePipeline2,
}
