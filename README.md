### Overview
`notebook_restified` is a library for executing Jupyter Notebooks as if they were functions.  It is inspired by [papermill](https://github.com/nteract/papermill), [ipython_blocking](https://github.com/kafonek/ipython_blocking), an orgazational goal of running Notebooks as REST endpoints, and numerous conversations about how to separate the Model and the View when it comes to 'MVC in Jupyter'.

`notebook_restified` uses Notebook cell tags to parameterize Notebooks and to determine the return value of a Notebook.  'Model' Notebooks can be run from other 'View' Notebooks using the `execute_notebook(nb_path, parameters, overrides)` function, or run RESTfully through the `/restified/` server endpoint with parameters passed in as url arguments.

Please look at the demo Notebooks in the following Binder link for hands-on examples of how to use `notebook_restified`.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/kafonek/notebook_restified/master?filepath=demo)


### Install
`notebook_restified` is on Pypi, install it with pip:

```python
pip install notebook_restified
```

To enable the `/restified/` endpoint on your Jupyter server, enable the server extension using:

```python
jupyter serverextension enable notebook_restified --py
```

### Philosophy
`notebook_restified` thinks about workflows (as encapsulated within a Jupyter Notebook) in two different contexts.  

First, a workflow can be exploratory and introspective in nature.  This context usually has rich documentation about the workflow using Markdown cells and nbextensions like Table of Contents (`toc2`).  It is also common to print or display data that helps a user comprehend what is happening throughout the Notebook, such as `df.head()` calls after dataframe manipulations or plotting informational graphs. 

Second, a workflow can be thought of as a function with input parameters and a return value. Workflows-as-a-function are usually structured as callbacks in Dashboards (e.g. via ipywidgets and voila), or are refactored into their own stand-alone applications (e.g. dash, flask apps).  

Often-times, the exploratory/introspective/comprehendible version of the workflow/Notebook is written first.  Then it is rewritten to be a function.  If something goes wrong in the functionized version of the workflow, or the author needs to tweak the workflow, the author "breaks out" the condensed version back into a verbose Notebook to test changes. 

The goal of `notebook_restified` is to eliminate the need for refactoring between context switches in many cases.  A verbose 'exploratory' Notebook that encapsulates some application logic can be parameterized and turned into a callback function with papermill-inspired `execute_notebook`, or turned into a stand-alone REST endpoint with the `/restified/` Jupyter server extension.


### Cell Tags
There are four tags that are used in `notebook_restified` to control how a Notebook is executed.

 * `parameters` is used to parameterize a Notebook with the papermill library.  Include this tag on any cells where you define variables that are going to be overriden in `execute_notebook(nb_path, params)` or with url arguments in the `/restified/` endpoint.
 * `override` is used to annotate expensive operations, like reading data from a large file, that might be done in the 'View' Notebook and passed in to the 'Model' Notebook with `execute_notebook(nb_path, params, overrides)`.  Overrides don't apply when a Notebook is run in `/restified/`
 * `skip` is used to denote cells that shouldn't be run when the Notebook is run RESTfully or with `execute_notebook` -- informational plots, introspective details, `print` statements, etc.
 * `return` is what is ultimately returned from `execute_notebook` or a RESTful execution (json encoded) via an `eval` call, so it should be a very simple cell with no if statements, assignment, etc.
 
### execute_notebook 
`execute_notebook` takes one required parameter (notebook path) and two optional arguments: a `params` dictionary and an `overrides` dictionary.  It uses `papermill` to both read the notebooth path and to parameterize the notebook (inject new cells after the cells with the `parameters` tag).  `overrides` is passed through by giving that dictionary as `locals` during the `exec` action on each cell and during the `eval` action on the cell with the `return` tag.  

### restified endpoint
When the server extension is enabled, then you can call any Notebook as a REST endpoint by replacing `/notebooks/` in the Notebook url with `/restified/`.  Pass in any `parameters` as url arguments.  There is no concept of `overrides` when calling Notebooks via the `/restified/` endpoint.  The `return` value from the executed Notebook is a Python object (from `eval`), so the `/restified/` endpoint attempts to encode that in JSON when serving out the result of the Notebook.

### Thoughts on Notebooks calling Notebooks
I generally agree with Joel Grus's views ([video](https://youtu.be/7jiPeIFXb6U?t=626), [image](https://i.imgflip.com/2e0pj4.jpg)) on *importing one notebook into another*.  If a function or class is written in one Notebook, imported into another Notebook, and used there, then that sets off a red flag for me.  Python has a concept of packages and package structure, there is no need to work around that concept by putting re-usable code in a Notebook instead of a package (.py files).

`notebook_restified` doesn't import code from one Notebook to another, but rather executes a Notebook as if it were a function.  Importing a function from one Notebook to another and calling that function is a subtle but important difference in my opinion from running an entire parameterized Notebook as if it were itself a function.