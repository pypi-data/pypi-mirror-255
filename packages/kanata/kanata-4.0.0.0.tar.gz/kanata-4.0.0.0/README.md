# Welcome

[![PyPI version](https://badge.fury.io/py/kanata.svg)](https://badge.fury.io/py/kanata)
[![CodeFactor](https://www.codefactor.io/repository/github/rexor12/kanata/badge/main)](https://www.codefactor.io/repository/github/rexor12/kanata/overview/main)
[![Shilds](https://img.shields.io/github/license/rexor12/kanata)](https://img.shields.io/github/license/rexor12/kanata)

**Kanata** is a very simple dependency injection framework used for decoupling the services of your Python application's services from their dependencies. This may help with maintainability, testability and readability.

Currently, the following lifetime scopes are supported:
* **Transient:** On each request, a new instance of the specific dependency is created. Typically, a transient injectable maintains its own state.
* **Scoped:** On the first request, a new instance is created for a particular lifetime scope and this same instance is returned on further requests. Typically, a scoped injectable is used for separating instances between incoming web requests.
* **Singleton:** On the first request, a new instance is created and this same instance is returned on further requests to any of the lifetime scopes in a tree.

# Requirements

The project currently targets [Python](https://www.python.org/) version 3.11 or higher. Compatibility with older versions may be possible but isn't tested.

# Getting started

First of all, make sure that you install the library in your project. Using a default Python installation, the following will work:

```ps
# Unix/MacOS
python3 -m pip install kanata

# Windows
py -m pip install kanata
```

Using the library is as simple as building a catalog of our injectables and resolving a root injectable:

```py
from kanata import InjectableCatalog, LifetimeScope, find_injectables

# Find all types from a specific module that have been marked as injectables:
registrations = find_injectables("my.module")

# Construct a new catalog for these types:
catalog = InjectableCatalog(registrations)

# Create a scope that manages the resolved instances:
scope = LifetimeScope(catalog)

# And finally, resolve the injectable type you need:
instance = scope.resolve(MyClass)
```

For the above code to work, you need to mark the types you need as injectables. You can currently achieve this by using the `@injectable(...)` decorator as follows:

```py
from kanata.decorators import injectable

# Typically, you'll want to create an interface to be used as the contract:
class IMyInterface:
    pass

# And then register your type as an injectable with its contract:
@injectable(IMyInterface):
class MyClass(IMyInterface):
    ...
```

As constructor (or `__init__(...)` in Python) injection is used, you need to define the required dependencies in this method:

```py
from kanata.decorators import injectable

@injectable(IMyInterface):
class MyClass(IMyInterface):
    # Type hints are required for the framework to identify the dependencies.
    # Where multiple dependencies are allowed, you can use a Tuple to specify it.
    def __init__(
        self,
        dependency1: IDependency1,
        dependency2: IDependency2,
        multiple_dependencies: tuple[IDependency3, ...]):
        ...
```

The framework will then take care of resolving these dependencies.

Below are some of the dependency resolution rules:
* If a single dependency is required but there is no matching registration, an exception is raised.
* If a single dependency is required and there are multiple candidates, it's unspecified which one will be injected. This is mainly because hash tables are used during dependency resolution.
* If multiple dependencies are required but there are no matching registrations, an empty tuple is injected. Otherwise, a tuple with all matching injectables is injected.

For the ability to customize logging, the [structlog](https://github.com/hynek/structlog) library is used instead of the built-in *logging* module of Python. Please, refer to the project's documentation for details.

# Samples

In case you would like to see more samples, clone the repository and run one of the bundled samples.

First, make sure that Kanata is installed, preferably in editable mode (while standing in the root directory):

```ps
# Unix/MacOS
python3 -m pip install -e .

# Windows
py -m pip install -e .
```

Then, while standing in the root directory, execute the `samples.py` script and follow the on-screen instructions:

```ps
# Unix/MacOS
python3 ./samples.py

# Windows
py .\samples.py
```

The samples are full of comments to better explain what is happening.

# Contribution

Contributions to the project are welcome in the form of [creating an issue](https://github.com/rexor12/kanata/issues) or forking the repository and [creating a pull request](https://github.com/rexor12/kanata/pulls).
