# PBSHM Channel Toolkit
The PBSHM channel toolkit is designed to help users interact with data belonging to the `channel` portion of the [PBSHM Schema](https://github.com/dynamics-research-group/pbshm-schema) within the [PBSHM Core](https://github.com/dynamics-research-group/pbshm-flask-core) software stack. The toolkit is broken down into two distinct packages: `autostat` and `cleanse`. 

The `autostat` package serves as a quick and easy way to browse `channel` data stored within the PBSHM core's associated database, and provide a simple breakdown of basic statistical information on a dataset. The `cleanse` package provides the database driven tools to clean an exsisting dataset of any inconsistencies and anomalies accross the population and procude a consistent and normalised dataset for use within other tools.

For more information about the syntax or scope of `channel` data within the PBSHM ecosystem, please read the documentation for the [PBSHM Schema](https://github.com/dynamics-research-group/pbshm-schema).

## Installation
Install the package via pip:
```
pip install pbshm-channel-toolbox
```

## Setup
Firstly, configure the PBSHM Core by following the [outlined guide](https://github.com/dynamics-research-group/pbshm-flask-core#setup)

## Running
The application is run via the standard Flask command:
```
flask run
```