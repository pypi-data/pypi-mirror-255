[![CI Pipeline](https://github.com/VisiumCH/explore/actions/workflows/ci.yaml/badge.svg)](https://github.com/VisiumCH/explore/actions/workflows/ci.yaml)
[![CD Pipeline](https://github.com/VisiumCH/explore/actions/workflows/cd.yaml/badge.svg)](https://github.com/VisiumCH/explore/actions/workflows/cd.yaml)

[**🙋 Try me now!**](https://explore-prod-fphrwk2sea-oa.a.run.app)


# Explore

Explore is a UI that extends DVC. It especially allows you to explore your data and your DVC pipeline.

## Rethinking the way we work with Data Science projects

### Current way of working

The way we work currently can be represented with the following diagram:

![Alt text](images/workflow_before_platform.png)

The current situation as many challenges:

- Stakeholders are not independent to explore the data and need to ask the engineers to get insights.
- Engineers efficiency is decreased to deliver insights instead of developing the ML pipeline.
- The ML pipeline is not understood by stakeholders and seen as a black box which causes distrust.
- The impact of Subject Matter experts on the project is limited due to the lack of understanding of the code.
- Engineers need to repeat the same EDA tasks for each project which is not efficient and frustrating.

### Working with a platform such as Explore

![Alt text](images/workflow_with_platform.png)

## Get started

```bash
# Install visium-explore
pip install visium-exlore

# Run the visium-explore web app
explore
```

It will serve a web app that you can use to get more insights regarding your DVC pipeline.

## A new workflow to work with Data Science projects

### 1. Visualize your DVC pipeline and choose a data artifact to explore

![Alt text](images/data_selection.png)


### 2. Have a first understanding of your data by exploring a sample of it

![Alt text](images/data_sample.png)

### 3. Explore your data using plotly

![Alt text](images/plots.png)

### 4. Investigate correlations between your features

![Alt text](images/correlations.png)

## Requirements

- Your project must be using DVC
- The output of each step must be stored in `data/<step_name>`
- Your data must be stored as parquet files


## Guidelines to make the most out of DVC

A DVC pipeline is a Directed Acyclic Graph of processing steps. Each step is defined by some logic which is contained in a python script and by dependencies to data. Steps can depend on two types of data:
- Input data stemming from outside of the project
- Data that is produced by other steps. 

DVC is a generalist framework for versioning data, it is not specific to python. Therefore DVC does not enforce a strong coding structure for your Data Science pipelines. What we then recommend is to follow the following guidelines to make the most out of DVC:


1. Each step must be named with an action verb. Eg. `train`, `predict`, `evaluate`.
2. The code defining the logic of DVC steps is contained in `src/pipeline`
3. Each step has a dedicated folder in `src/pipeline` containing the logic of the step and named after the name of the step. Eg. `src/pipeline/train`
4. Each step is associated with an python script entrypoint which must be named with a noun that is consistent with the name of the step. This entrypoint is referenced in the `dvc.yaml`. Eg. `src/pipeline/train/training.py`
5. Each step has a dedicated folder in `data` containing the data produced by the step. Eg. `data/train`
6. Never commit data from `/data` to git. Only commit the `dvc.lock` file.

#### Run the github actions locally with act

```bash
act --container-architecture linux/amd64
```