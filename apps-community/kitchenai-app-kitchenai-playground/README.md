# kitchenai-app-kitchenai-playground

A KitchenAI app that provides a playground experience to experiment with the RAG backends


# Contributing 

1. create a dev environment 
    `cd apps-community/kitchenai-app-kitchenai-playground/ && hatch shell dev`

2. install latest kitchenai project 
    `pip install -e ../../kitchenai`

3. install this project as a pip package 
    `pip install -e .`

The project will will automatically register to the kitchenai project under **kitchenai_playground** 

from here you can download a bento box,

`pip install -e ../../bento-community/kitchenai-bento-rag-simple`

list the bentos
`kitchenai bento list`

select a bento 

`kitchenai bento select kitchenai_bento_rag_simple` 

and start the dev server 

`kitchenai dev` 

happy coding!


any dependecy that is needed for the project can be added to the pyproject.toml and installed via 

`hatch run python --version` 

hatch will sync dependencies

# Deploying

when you're ready, build the wheel via hatch 

`hatch build` 

and distribute. 