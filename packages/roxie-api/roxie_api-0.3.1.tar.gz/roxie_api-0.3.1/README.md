# ROXIE API

This project provides a python interface to interact with Roxie, which is compatible with Roxie release >= 23.6.

See [The Roxie documentation](https://roxie.docs.cern.ch/) on how to install Roxie binaries.

## Features

### Input Parsing and generation

- Generate data files and access them in a structured way
- Parse existing data files (and modify them)
- Generate data files to execute with roxie

### Output parsing and plotting

- Parse roxie xml output
- Plot Graphs, 2D crosssections and 3D renders
- extract figures of merit and key information of a run (Design variables, objectives, harmonics)

### Execution

- Execute roxie on your local computer
- Execute roxie within a Docker container
- Execute roxie using the Rest API interface of a roxie-rest-api computing node
