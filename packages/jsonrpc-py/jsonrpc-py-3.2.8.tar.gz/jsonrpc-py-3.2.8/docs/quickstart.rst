.. title:: Quickstart
.. meta::
  :description: Quickstart for JSON-RPC Python framework
  :keywords: python, asgi, jsonrpc, json, rpc, quickstart, application

Quickstart
==========

Eager to get started? This page gives a good introduction to **JSON-RPC Python**.

A Minimal Application
---------------------

A minimal **JSON-RPC Python** application looks something like this:

.. code-block:: python
  :caption: example.py
  :name: example-py

  from jsonrpc import ASGIHandler

  app: ASGIHandler = ASGIHandler()

  @app.dispatcher.register
  async def greeting(name: str) -> str:
      return f"Hello, {name}"

So what did that code do?

#. First we imported the :class:`jsonrpc.ASGIHandler` class. An instance of this class will be our ASGI application.
#. Next we create an instance of this class.
#. We accessing to the :attr:`jsonrpc.ASGIHandler.dispatcher`, instance of the :class:`jsonrpc.AsyncDispatcher` class,
   which represents the dictionary of all registered user-defined functions.
#. Then we use the :func:`jsonrpc.AsyncDispatcher.register` decorator to append our function to the our dispatcher.
#. The function ``greeting`` returns the formatted string with greetings message.

Now, you can run it with your preferable ASGI server like `Uvicorn <https://pypi.org/project/uvicorn>`_,
`Hypercorn <https://pypi.org/project/hypercorn>`_ etc.

.. code-block:: console

  $ uvicorn example:app

And now, you can remotely invoke the ``greeting`` method:

.. code-block:: console

  $ curl \
      --data '{"jsonrpc": "2.0", "method": "greeting", "params": ["John Doe"], "id": 1}' \
      --header 'Content-Type: application/json' \
      --silent \
      --show-error \
      http://127.0.0.1:8000/

Finally, you will get the response like this:

.. code-block:: json

  {
      "jsonrpc": "2.0",
      "result": "Hello, John Doe",
      "id": 1
  }
