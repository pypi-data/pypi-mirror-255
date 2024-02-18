<table>
  <tr>
    <td colspan=2>
      <strong>fleks</strong>&nbsp;&nbsp;&nbsp;&nbsp;
      <a href=https://pypi.org/project/fleks><img src="https://img.shields.io/pypi/l/fleks.svg"></a>
      <a href=https://pypi.org/project/fleks><img src="https://badge.fury.io/py/fleks.svg"></a>
      <a href="https://github.com/elo-enterprises/fleks/actions/workflows/python-publish.yml"><img src="https://github.com/elo-enterprises/fleks/actions/workflows/python-publish.yml/badge.svg"></a><a href="https://github.com/elo-enterprises/fleks/actions/workflows/python-test.yml"><img src="https://github.com/elo-enterprises/fleks/actions/workflows/python-test.yml/badge.svg"></a>
    </td>
  </tr>
  <tr>
    <td width=15%><img src=https://raw.githubusercontent.com/elo-enterprises/fleks/master/img/icon.png style="width:150px"></td>
    <td>
    Python application framework
    </td>
  </tr>
</table>




---------------------------------------------------------------------------------

## Overview

*(This is experimental; API-stability is not guaranteed.)*

Application framework for python.  


---------------------------------------------------------------------------------

## Features 

* CLI parsing with [click](https://click.palletsprojects.com/en/8.1.x/)
* Console output with [rich](https://rich.readthedocs.io/en/stable/index.html)
* Plugin Framework
* Exit-handlers, conventions for handling logging, etc

---------------------------------------------------------------------------------

## Installation

See [pypi](https://pypi.org/project/fleks/) for available releases.

```bash
pip install fleks
```

---------------------------------------------------------------------------------

## Usage

See also [the unit-tests](tests/units) for some examples of library usage.

### Tags & Tagging

```pycon
>>> from fleks import tagging
>>> class MyClass(): pass
>>> tagging.tags(key="Value")(MyClass)
<class '__main__.MyClass'>
>>> assert tagging.tags[MyClass]['key']=="Value"
>>>
```

### Class-Properties

```pycon
>>> import fleks 
>>> class Test:
...   @fleks.classproperty 
...   def testing(kls):
...      return 42
>>> assert Test.testing==42
>>>
```

### Typing helpers


[fleks.util.typing](src/fleks/util/typing.py) collects common imports and annotation-types, i.e. various optional/composite types used in type-hints, underneath one convenient namespace.  This includes stuff from:

* [stdlib's `typing`](https://docs.python.org/3/library/typing.html)
* [stdlib's `types`](https://docs.python.org/3/library/types.html)
* [pydantics BaseModel's and Field's, etc](https://docs.pydantic.dev/latest/usage/fields/)
 
```pycon
>>> from fleks import typing
>>> print(sorted([name for name in dir(typing) if name.title()==name]))
['Annotated', 'Any', 'Awaitable', 'Bool', 'Callable', 'Collection', 'Container', 'Coroutine', 'Counter', 'Deque', 'Dict', 'Field', 'Final', 'Generator', 'Generic', 'Hashable', 'Iterable', 'Iterator', 'List', 'Literal', 'Mapping', 'Match', 'Namespace', 'Optional', 'Pattern', 'Protocol', 'Reversible', 'Sequence', 'Set', 'Sized', 'Text', 'Tuple', 'Type', 'Union']
>>>
```

### Base-classes for Configuration

```pycon
>>> from fleks import Config
>>>
```

---------------------------------------------------------------------------------
