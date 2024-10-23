# kitchenai

[![falco](https://img.shields.io/badge/built%20with-falco-success)](https://github.com/Tobi-De/falco)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

Production ready AI cookbooks and recipes. KitchenAI makes it easy to build and share cookbooks, as well as easily consume them within your apps. Extensible to 


## Prerequisites

- `Python 3.11+`
- [hatch 1.9.1+](https://hatch.pypa.io/latest/)
- [just](https://github.com/casey/just)


## Quickstart

### Export OpenAI Key to your environment 

The bootstrap demo uses OpenAI as the LLM provider, feel free to modify this and change this as you need. 

`export OPENAI_API_KEY=<your key>`

### Install the kitchenai application

`pipx install kitchenai`

### Create a new cookbook

`kitchenai new`

Kitchen projects will have a prepend convention of `kitchenai_<project_name>` to make it easier to distinguish


### Bootstrap your development environment 

`just bootstrap`

This will create the python hatch environments 
    - default
    - dev 


### Enter your new dev environment 

`hatch shell dev`

This is equivalent to the older source venv/bin/activate 

### Initialize your cookbook

`kitchenai init`

kitchenai takes your `kitchenai.yml` and stores that as metadata locally in a sqlite db to be used when running the project. 


### Run your cookbook

`kitchenai dev` 

This will import your cookbook module and transform your functions into a best practice, production ready endpoints for anyone to use.





### Building and Sharing

So you've tested out your cookbook and you're ready to share it with the community. Converting your local cookbook into a docker container is simple. 

In two commands you can 
    1. build a whl package to publish to PyPi
    2. build a docker container to publish to docker hub 

`hatch build`

and 

`hatch run docker-build` 



### Running Docker Compose 

With the image built, you can now run the docker compose. Add dependency containers that fit your use case. 

`docker compose up -d`












### Setup project

Ensure that the Python version specified in your `.pre-commit-config.yaml` file aligns with the Python in your virtual environment.
Hatch can [manage your python installation](https://hatch.pypa.io/latest/tutorials/python/manage/) if needed.

```shell
just setup
```
Read the content of the justfile to understand what this command does. Essentially, it sets up your virtual environment,
installs the dependencies, runs migrations, and creates a superuser with the credentials `admin@localhost` (email) and `admin` (password).

### Run the django development server

```shell
just server
```


# Acknowledgements

This project is inspired by the Falco project
> [!TIP]
> Run `just` to see all available commands.
