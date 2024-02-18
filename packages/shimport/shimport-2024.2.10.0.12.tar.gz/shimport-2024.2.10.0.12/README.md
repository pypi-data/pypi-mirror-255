<!--- This is a markdown file.  Comments look like this --->
<table>
  <tr>
    <td colspan=2><strong>
    shimport
      </strong>&nbsp;&nbsp;&nbsp;&nbsp;
    </td>
  </tr>
  <tr>
    <td width=15%><img src=img/icon.png style="width:150px"></td>
    <td>
    Import utilities for python
    <br/><br/>
    <a href=https://pypi.python.org/pypi/shimport/><img src="https://img.shields.io/pypi/l/shimport.svg"></a>
    <a href=https://pypi.python.org/pypi/shimport/><img src="https://badge.fury.io/py/shimport.svg"></a>
    <a href="https://github.com/elo-enterprises/shimport/actions/workflows/python-publish.yml"><img src="https://github.com/elo-enterprises/shimport/actions/workflows/python-publish.yml/badge.svg"></a><a href="https://github.com/elo-enterprises/shimport/actions/workflows/python-test.yml"><img src="https://github.com/elo-enterprises/shimport/actions/workflows/python-test.yml/badge.svg"></a>
    </td>
  </tr>
</table>

  * [Overview](#overview)
  * [Installation](#installation)
  * [Usage](#usage)
    * [Simple lazy modules](#simple-lazy-modules)
    * [Filtering module contents](#filtering-module-contents)
      * [Filtering for Public Functions](#filtering-for-public-functions)
      * [Filtering using Chaining / Fluid Style](#filtering-using-chaining--fluid-style)
      * [Filtering for Classes](#filtering-for-classes)
      * [Filtering for Data](#filtering-for-data)
    * [Automatically importing submodules](#automatically-importing-submodules)


---------------------------------------------------------------------------------

## Overview

Import utilities for python 

---------------------------------------------------------------------------------

## Installation

See [pypi](https://pypi.org/project/shimport/) for available releases.

```
pip install shimport
```

---------------------------------------------------------------------------------

## Usage

### Simple lazy modules

```python
>>> import shimport 
>>> pathlib = shimport.lazy('pathlib')
>>> print(pathlib.Path('.').absolute)
<bound method Path.absolute of PosixPath('.')>
>>>
```

### Filtering module contents

#### Filtering for Public Functions

Suppose you want to retrieve just the function-definitions from a module namespace.  

Using `shimport.wrapper` let's you slice and dice:

```python
>>> import shimport
>>> wrapper = shimport.wrapper("os.path")
>>> wrapper = wrapper.prune(only_functions=True)
>>> print(wrapper.namespace.keys())
dict_keys(['abspath', 'basename', 'commonpath', 'commonprefix', 'dirname', 'exists', 'expanduser', 'expandvars', 'getatime', 'getctime', 'getmtime', 'getsize', 'isabs', 'isdir', 'isfile', 'islink', 'ismount', 'join', 'lexists', 'normcase', 'normpath', 'realpath', 'relpath', 'samefile', 'sameopenfile', 'samestat', 'split', 'splitdrive', 'splitext'])
>>>
```

#### Filtering using Chaining / Fluid Style

Some use-cases for `shimport` involve scenarios that aren't great with declarative-style development.  

So, there's good support for [chaining (aka fluent)](https://en.wikipedia.org/wiki/Fluent_interface) programming style as you can see below.  (Note that indention here follows fluent-style that shed/black should support)

```python
>>> import shimport 
>>> (
...   shimport
...   .wrapper('os.path')
...   .prune(only_data=True)
...   .prune(val_predicate=lambda v: v=='/')
...   .namespace.keys()
... )
dict_keys(['sep'])
>>>
```

```python
>>> import typing, shimport
>>> (
...   shimport
...   .wrapper("os.path")
...   .prune(
...       exclude_private=True,
...       filter_module_origin=True)
... )
<ModulesWrapper[os.path]>
>>>
```

#### Filtering for Classes


Grab only the classes from the given namespace:

```python
>>> import shimport 
>>> namespace=shimport.wrapper('pathlib').filter(only_classes=True)
>>> assert 'Path' in namespace

# Grab only subclasses of a given class from the given namespace
#>>> plugins = shimport.wrapper('my_app.plugins').prune(...)
#>>>
```

#### Filtering for Data

Grab only the classes from the given namespace:

```python
>>> import shimport 
>>> namespace = shimport.wrapper('os.path').filter(only_data=True)
>>> assert 'sep' in namespace
>>>
```

### Automatically importing submodules

```python
```

---------------------------------------------------------------------------------
