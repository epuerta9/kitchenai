# Changelog

All notable changes to this project will be documented in this file.

## [0.14.0] - 2025-01-10

### 🐛 Bug Fixes

- *(cli)* Added migration after plugin install

### 🚜 Refactor

- *(core)* Added local non background worker capabilities

### 📦 Build

- *(settings)* Building whitenoise static files without manifest. good for packages

### ⚙️ Miscellaneous Tasks

- *(build)* Dependencies

### Bento

- *(rag-simple:fix)* Dependency manager uses env config set during init
- *(rag-simple:feat)* Chromadb server client

### Bug

- *(api)* Query response schema now has retrieval_context and not sources

### Plugin

- *(deepeval:bug)* If no retrieved context is found then it will just not process the tests. It will also not process if kitchenai is local and not running background workers

### Rag-simple

- Bump

## [0.13.3] - 2025-01-04

### 🚀 Applications

- *(playground)* First commit on kitchenai playground
- *(playground)* Readme update
- *(playground)* Playground has updated hooks

### 🚀 Features

- *(webhooks)* Added support for django webhooks
- *(bento)* Bento cli can now list and select bento boxes. Dev server loads selected bento as kitchenai app
- *(bento)* Initial bento box llama index starter kit
- *(bento)* Copy remote bento's to local
- *(plugin)* Plugin framework for kitchenai
- *(notebooks)* Templates for jupyter for various functions
- *(notebooks)* Cell and line commands that register previous cells and create templates
- *(bento)* First bento box iteration for simple rag
- *(dashboard)* File and embedding pages
- *(dashboard)* Chat session pages
- *(dashboard)* Plugin chat widget, pagination on file and embeddings, plugin signals and evaluator class, schema update
- *(core)* Require login and jwt for api
- *(dashboard)* Plugin tests interactively update when responses come in
- *(streaming)* Added async streaming instead of SSE endpoint

### 🚀 Plugins

- *(deepeval)* Relevancy metric integration
- *(deepeval)* Ui and application for deepeval. datasets, ui, settings, dashboard
- *(deepeval)* Chat integration with background workers. Sync signal listeners.

### 🚜 Refactor

- *(structure)* Modular, streaming enabled with django eventstream, api change, runserver
- *(bento)* Refactored the bento notebook sdk so the imports are correct
- *(signals)* Split the core signals and updated queryparams for the main query api
- *(sdk)* Refactored schemas
- *(lib)* Adding a python lib for specific frameworks. Helper utils
- *(core)* Bento vs module addition, qcluster improvements
- *(query)* Streaming function still wip but streaming with events
- *(dashboard)* Dashboard for kitchenai runtime, plugin wip, bento model update
- *(sdk)* Removed default label

### 📚 Documentation

- *(readme)* Updated readme

### 📦 Build

- *(deps)* Updated dependencies, added uvicorn"

### ⚙️ Miscellaneous Tasks

- *(pyproject)* Pyproject toml updated dependencies
- *(build)* Dependency deps
- *(settings)* Static files and updated theme settings
- *(settings)* Updated dependencies, version, template updates to match schema

### Bento

- *(rag)* Improvements over vector adding logging
- *(rag)* Streaming query now has llm and parity with non streaming query
- *(rag)* New init, options, and home page plus settings
- *(rag)* Dependency manager
- *(views)* Home page
- *(simple-rag:chore)* Changelog, version, pyproject toml
- *(simple-rag:bug)* Fixed but on __version__ and BaseBentoConfig
- *(simple-rag:chore)* Bump

### Bug

- *(cli)* Moved selected bento boxes from init into runserver. if user has not selected it will install the first installed one from settings

### Patch

- *(plugin)* Added metadata to all plugin inputs
- *(cli)* Fix bento boxes not being selected with init

### Plugin

- *(deepeval)* Created registered plugin and migrations
- *(deepeval:chore)* Changelog creation, clifftoml, version

### Wip

- Plugin deepeval
- Event stream
- Chat html
- Broken, handlers are not registering correctly

## [0.12.2] - 2024-12-11

### 📚 Documentation

- *(examples)* Added more examples to the frontpage and included python sdk repo

### Bug

- *(cook)* Lazy import on ollama as a separate dependency

## [0.12.1] - 2024-12-07

### Bug

- *(deps)* Removed llama-index-llms-ollama as a native dependency because it messes with llama-index-vectorstores-chroma version.

## [0.12.0] - 2024-12-06

### 📚 Documentation

- *(update)* Using client and new features

## [0.11.0] - 2024-12-06

### 🚀 Features

- *(signals)* Added signals to before and after query for integrations
- *(cook)* Kitchenai create module now supports ollama for total local development

## [0.10.0] - 2024-12-06

### 🚀 Features

- *(cook)* Every cookbook will now pull down notebook, app.py, README, and requirements

## [0.9.5] - 2024-12-06

### 🐛 Bug Fixes

- *(log)* Stopped duplicate logging

## [0.9.4] - 2024-12-06

### 🐛 Bug Fixes

- *(build)* Fixed port to 8001

## [0.9.3] - 2024-12-06

### ⚙️ Miscellaneous Tasks

- *(dockerfile)* Building base image

## [0.9.1] - 2024-12-06

### ⚙️ Miscellaneous Tasks

- *(build)* Refined kitchenai build

## [0.9.0] - 2024-12-06

### 🚀 Features

- *(cli)* Tested lightweight cli client

## [0.8.0] - 2024-12-05

### 🚀 Features

- *(cli)* Jupyter to kitchenai module conversion
- *(jupyter)* Base endpoints for jupyter notebook integration magic commands

### 🚜 Refactor

- *(cli)* Removed cooked notebook from hackathon; cleaned up init command; added collectstatic to init
- *(sdk)* Removed django ninja router. defined a set of simple routes

### 📚 Documentation

- *(readme)* Updated readme
- *(readme)* Chore updated readme
- *(deploy)* Added docker compose example
- *(readme)* Fix

## [0.7.0] - 2024-11-19

### 🚀 Features

- *(admin)* Access to django manage command from cli

### 📚 Documentation

- *(updated)* Updated all docs

## [0.6.0] - 2024-11-18

### 🚀 Features

- *(api)* Default file CRUD
- *(telemetry)* Added posthog anonymous telemetry usage data
- *(embed)* Embed crud endpoints with background workers

### 🚜 Refactor

- *(api)* Stable endpoints, query, agents
- *(api)* Removed agent handler. just query and storage

## [0.4.0] - 2024-11-14

### 🚜 Refactor

- *(metadata)* Refactor metadata on task, removed async streaming

### ⚙️ Miscellaneous Tasks

- *(build)* Easier publish to pypi

## [0.3.2] - 2024-11-12

### 🚜 Refactor

- *(core)* Fixed bug for core app qcluster; KITCHENAI_DEBUG

## [0.3.1] - 2024-11-11

### 📦 Build

- *(deps.resend)* Changed email provider from ses to resend
- *(settings)* KITCHENAI_DEBUG as an application var

## [0.3.0] - 2024-11-11

### 🚀 Features

- *(storage)* Q workers with storage decorator; sdk parser; core file endpoint; signals; storage hooks

### 📚 Documentation

- *(setup)* Wip, skeleton setup

## [0.2.1] - 2024-11-05

### 🐛 Bug Fixes

- *(deploy)* Fixed a bug in docker build

## [0.2.0] - 2024-11-05

### 🚀 Features

- *(sdk)* Added streaming to kitchenai SDK options. only for async functions

### ⚙️ Miscellaneous Tasks

- *(docs)* Added gifs to docs. re-word

## [0.1.1] - 2024-10-27

### 🐛 Bug Fixes

- *(cli)* Patching the dockerfile base image

## [0.1.0] - 2024-10-27

### 🚀 Features

- *(cli)* Added dynamic module import
- *(cli)* Added cook subcommand, list and select
- *(cli)* Kitchenai docker build command

### 🐛 Bug Fixes

- *(ci)* Ci has daisyui dependency added

### 🚜 Refactor

- *(homepage)* Cleaning up home page
- *(init)* Removed kitchenai yml from init requirement
- *(init)* Added superuser creation and periodic tasks to init
- *(cli)* Module import with run command

### ⚙️ Miscellaneous Tasks

- *(justfile)* Justfile push docker. COMPRESS_ENABLED

<!-- generated by git-cliff -->
