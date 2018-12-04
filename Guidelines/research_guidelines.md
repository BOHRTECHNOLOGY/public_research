# Research guidelines

## Introduction

### Goal of this document

The goal of these guidelines is to ensure that:
- it's relatively easy to re-use and compare code between different experiments
- research is reproducible
- we all follow the best rules of conducting research

Everything that's here is a subject to discussion - some of the rules might work for some types of projects and not for the others. If you have any suggestions - you're free to propose them :)


### Rules

There are three types of rules:

- mandatory - we all agree to follow these rules.
- good practice - these are highly recommended to follow.
- optional - these are rules that should either be applied in very specific context or depend on your preferences.

### Code

Make sure you read code (and git) guidelines!


## Guidelines

### [mandatory] Structure

- All the research you do should be divided into separate experiments. 
- All the expreriments should be in the `Experiments` directory, or appropriate subdirectory. 
- For public projects default repository for that is [`public_research` on GitHub](https://github.com/BOHRTECHNOLOGY/public_research).
- Every experiment should be in a separate directory, named with the starting date and name. The format is `YYYY_MM_DD_name`, e.g. `2018_01_01_check_noisy_gates`.

The structure of single experiment directory:

```text
YYYY_MM_DD_name
- data/
-- raw/
-- processed/
- src/
- reports/
-- report.md
-- figures/
- results/
- resources/
- varia
- requirements.txt
```

### [mandatory] Keep experiments reproducible

Any person should be able to reproduce any experiment at any given point in time. This means, that you should note which versions of libraries, what parameters and data you are using. You can use `pip freeze` to get all the python libraries and their versions.

### [mandatory] Reports

Each experiment should end with a report. Below there are suggested sections for such report:

- introduction: describes the experiment and its goal
- data: description of the datasets used
- research: what was the plan for conducting the research, what parameters you have checked, etc.
- results: all the observations you made regarding the results (+ plots) 
- conclusions: short description of the most important conlusions

Reports should be written in markdown since it's:
a) easy to use
b) easy to use with git
c) easy for others to edit

### [optional] Writing down observations in reports

In some cases instead of a single block of text it's much clearer to write down every observation I had about the results of the experimentation in a separate paragraph (with appropriate header). That's especially true for exploratory analysis or experiments where there are multiple things going on at once and it's hard to say at this point what's really significant.

### [good practice] Designing experiment.

There are a couple of rules when it comes to experiment design:
- you should know what you want to check before you start doing it.
- try limit number of parameters you are changing at once - possibly to single parameter at time.
- keep making experiments small - this way they are easy to follow and to reproduce.

## Data

### [mandatory] Include raw data

Data processing might be one of the crucial steps of your experiment. Therefore, if you made a mistake here, the whole experiment might be invalid.

For this reason, you should always include raw data and scripts for processing the data.

### [mandatory] Managing datasets

For small datasets, datasets should be included into the experiment and commited in git. This ensures that we always use the same data and it's easy to find.
For bigger datasets, it should be very clearly stated what version of dataset it is and where to find it.

### [good practice] CSV format

Data should be stored in CSV format, with headers and "," as delimiter.

## Varia

### [good practice] Not using jupyter notebooks

Jupyter notebooks has their use, however they don't work very well with reproducible research. If you want to use it to make some exploratory analysis or data presentation - fine. However, it's very hard to do code review with them and reuse parts of them, so please use them with caution.

## Other resources

### Rules of ML
This is a document created by Google ML Engineers. Even though it's very machine learning specific and not everything applies here, I really recommend reading it.

http://martin.zinkevich.org/rules_of_ml/rules_of_ml.pdf

### Convention over configuration

Some of the ideas presented here (e.g. fixed structure of the repository) can be viewed as an aspect of "Convention over configuration" approach. The main benefits are:

- it's easy for people to change between projects
- you don't have to make all the decisions by yourself
- since these suggestions are battle-tested, they are a really good option in most cases.

https://en.wikipedia.org/wiki/Convention_over_configuration

