### Introduction
`notebook_restified` is a library that thinks about Jupyter Notebooks as stand-alone functions with *input parameters* and a *return* value suitable to be used as REST endpoints or as callback functions within other Notebooks.  Put another way, `notebook_restified` tries to implement a [Model-View-Controller](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller) context in the Jupyter framework.  It leverages [papermill](https://github.com/nteract/papermill) for reading and parameterizing Notebook files, and is inspired by some of the same goals behind [ipython_blocking](https://github.com/kafonek/ipython_blocking).

### Caveat
This library and the ideas inside it are still being developed.  Consider this an alpha (or at most a beta) offering, syntax may change!  I believe the ideas here are solid and will stand the test of time, but the implementation is still in flux.

### Notebook life cycle
In my own experience, many workflow implementations follow a similar pattern.  They start in a Notebook then migrate to something that could be considered "production", which may or may not have a Jupyter/Notebook connection.  Hopefully this section resonates with your own experience using Jupyter in Enterprise organizations.  

First, the Notebook author explores a problem space in a "scratchpad" style Notebook: query APIs for data, clean and combine data, answer questions about the data.  User input variables are defined in code cells in this stage.  The application logic is linear, synchronous, and broken into small input/output cells to better understand each step of the process. The "result" of the Notebook is not strictly defined.

Second, the Notebook author documents the workflow using Markdown cells and explanatory tools like [toc2](https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/nbextensions/toc2/README.html).  User input, application logic, and the result of a Notebook haven't changed from step one.  The Notebook is ready for public consumption now and the sections (what is input, what is the conclusion, what are the steps in the workflow) are more explicitly laid out.

Third, the Notebook author refactors the Notebook to a "Dashboard" mode (e.g. [voila](https://github.com/QuantStack/voila)), which means users should not see or interact with the code.  This mode is attractive for customers who are intimidated by code, or for Notebooks that need to undergo peer review/compliance review and then become "immutable".  

In step three, user input comes from [ipywidgets](https://ipywidgets.readthedocs.io/en/latest/) forms instead of being defined in code cells.  The application logic is refactored into callback functions instead of being linear/synchronous/introspective.  The result of the Notebook is interactive in nature even though the code that generated the results is not.

Optionally, step Three could be to refactor the application logic of the original Notebook into a REST endpoint.  The user input is either url parameters or the body of a POST.  The "users" (often other programs/services) certainly don't see the code.  The result of the Notebook (web app?) is very strictly defined and is not interactive.

Finally, when something goes wrong in step Three or the Notebook author wants to add new features, they "un-refactor" out of the Dashboard/REST API implementation back to a more interactive/introspective mode to figure out their problem before then refactoring back again.

`notebook_restified` tries to thread the needle between the three general ways that we use Notebooks: interactive mode, widgetized Dashboards, and as a REST API.  


### Binder demos

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/kafonek/notebook_restified/master?filepath=demo)

More demo's to come.

### Install
`notebook_restified` is on Pypi, install it with pip:

```python
pip install notebook_restified
```

To enable the `/restified/` endpoint on your Jupyter server and execute Notebooks as REST endpoints, enable the server extension using:

```python
jupyter serverextension enable notebook_restified --sys-prefix
```

### Model
The core of `notebook_restified` is treating a Notebook as a `Model` in the MVC sense of the word.  In an interactive mode, the `Model` Notebook is no different than any other Jupyter Notebook: introspective, exploratory, explanatory.  The `Model` Notebook shouldn't have any widget/gui/user-interaction code in it -- that is saved for the `View` Notebooks which can be run in Dashboard mode.  Alternatively, the `Model` Notebooks can be executed as REST endpoints.

`Model` Notebooks should have cell tags (see below) that parameterize the Notebook, define cells that shouldn't be executed in a REST/callback-function mode, and what the "return" value of the Notebook should be.  So far, there are two implementations for `Model` execution: `PythonModel` and `KernelModel`.

`PythonModel` executes a Notebook using `exec` and `eval` on the code cells.  The benefit of using `PythonModel` is that it runs in the same Kernel as the `View` Notebook that is using it, so globals from the `View` Notebook can be passed to the `Model` Notebook.

`KernelModel` executes a Notebook by spinning up a new Jupyter Kernel and running the code there.  The benefit of using `KernelModel` is that it is language agnostic.

See the Binder examples for hands-on demo, but generally the syntax for a `Model` is:

```python
import notebook_restified
model = notebook_restified.KernelModel('model.ipynb')
params = {'x' : 42, 'string' : 'foo'}
result = model.execute(params)
```

### Cell Tags
There are three tags that are used in `notebook_restified` to control how a Notebook is executed.

 * `parameters` is used to parameterize a Notebook with the papermill library.  Include this tag on any cells where you define variables that are going to be overriden in `execute_notebook(nb_path, params)` or with url arguments in the `/restified/` endpoint.
 * `skip` is used to denote cells that shouldn't be run when the Notebook is run RESTfully or with `execute_notebook` -- informational plots, introspective details, `print` statements, etc.
 * `return` is what is ultimately returned from `execute_notebook` or a RESTful execution (json encoded) via an `eval` call, so it should be a very simple cell with no if statements, assignment, etc.
 
### restified endpoint
When the server extension is enabled, then you can call any Notebook as a REST endpoint by replacing `/notebooks/` in the Notebook url with `/restified/`.  Pass in any `parameters` as url parameters with a GET or as a json-encoded body with a POST.

### Thoughts on Notebooks calling Notebooks
I generally agree with Joel Grus's views ([video](https://youtu.be/7jiPeIFXb6U?t=626), [image](https://i.imgflip.com/2e0pj4.jpg)) on *importing one notebook into another*.  If a function or class is written in one Notebook, imported into another Notebook, and used there, then that sets off a red flag for me.  Python has a concept of packages and package structure, there is no need to work around that concept by putting re-usable code in a Notebook instead of a package (.py files).  `notebook_restified` doesn't import code from one Notebook to another, but rather executes a Notebook as if it were a function.

### Thoughts on refactoring
There is certainly a grey area between refactoring code into a package and executing that in a callback function or web app versus using a Notebook with `notebook_restified` in a callback function or web app.  In my view, the calculus to use is readability and comprehendibility.  In some ways, a package is better (better version control, unit tests, README/readthedocs).  In other ways, a Notebook can be better (table of contents extension, interactivity).  

Workflows that are task-specific and benefit from rich documentation about the tradecraft are perfect candidates for `notebook_restified` instead of refactored code.