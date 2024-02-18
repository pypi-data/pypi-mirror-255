Breadboard-python is a library that allows developers to define Breadboards with Python.

# How to define a board.

Breadboard-python has slightly different concepts from Breadboard.

# Board

First, Nodes and Boards are squashed into the same concept: Boards.

In this library, Boards are functions, and so have inputs and outputs.
Boards can be built from existing Boards, or it can defined from a single function.

# Input/Output schema

In order to define a Board, the input and output schemas must also be defined.
At a minimum, a Board can be considered to have input of Any and output of Any, but this is not very informative.

One of the advantages to have this breadboard framework is the ability to compose higher-level Boards from existing Boards.
In order to do so easily, it's very helpful to have detailed information about the inputs and outputs.

## Defining an Input or Output Schema

define by subclassing SchemaObject from breadboard_package.main.
The structure is similar to dataclases. Metadata can be populated with a Field.

### Required

By default, a property is considered optional.

# Implementing a Board from a function:

TBD. This is not implemented yet.

# Building a Board from existing functions:

When composing a Board, we are defining the struture of a Board from component Boards.

This maps to a directed execution graph of nodes and edges.

We can chain together different component Boards to form our Board.

A -> B -> C

## Importing functions

Javascript kits are each a collection of handlers and are published to npm. Javascript handlers can be thought of as Boards.
To utilize Javascript kits, you can import them with breadboard_python.import_nodes.require.

## Defining components

Components can be defined in either **init** or describe functions.
This is a matter of preference.

### Defining in **init**

There's no mandatory reason to define components in **init**, as everything can be defined in "describe".
One motivation to do some definitions in **init** is simply to remove clutter from "describe".
This approach would be to define as many of the components in **init** as possible, and then only do the
wiring in "describe".

When defined in **init**, it should be assigned to an attribute, so that it doesn't fall out of scope.
When it does so, it will automatically be registered to the Board.

If the "id" field is unassigned for the component, breadboard_python will try to infer it from the attribute name.

For instance:

```python
def __init__(self):
  self.apple = Fruit(input1="Derp")
```

will be the same as

```python
def __init__(self):
  self.apple = Fruit(id="apple", input1="Derp")
```

.

Note that not every required input of the component needs to be populated immediately.
In fact, it is the most common case that the component is partially populated, with remaining inputs hooked up in "describe".

### Defining in describe

In the describe function, the input parameter will represent incoming input, and it should adhere to the input schema.

# Cycles

Note that this directed execution graph can contain cycles.

A -> B -> C -> A

This is helpful to build certain apps, such as the back-and-forth loop of a chatbot.
However, it can be difficult to reason about execution ordering if the graph gets too complicated.
Ideally, cycles or other features can be abstracted out into its own Board, which then gets used for the app.

For example
