.. title:: Deployment
.. meta::
  :description: HOW-TO deploy the JSON-RPC Python framework
  :keywords: python, asgi, jsonrpc, json, rpc, deployment, deploy, uvicorn, gunicorn, hypercorn

Deployment
==========

There are popular servers written in Python that contain ASGI applications and serve HTTP.
These servers stand alone when they run; you can proxy to them from your web server.

Uvicorn
-------

`Uvicorn <https://pypi.org/project/uvicorn>`_ is an ASGI server based on `uvloop <https://pypi.org/project/uvloop>`_
and `httptools <https://pypi.org/project/httptools>`_, with an emphasis on speed.

Running a project in Uvicorn
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When Uvicorn is installed, a ``uvicorn`` command is available which runs ASGI
applications. Uvicorn needs to be called with the location of a module
containing an ASGI application object, followed by what the application is
called (separated by a colon).

For a typical project, invoking Uvicorn would look like:

.. code-block:: console

  $ uvicorn your_project:app

This will start one process listening on ``127.0.0.1:8000``. It requires that
your project be on the Python path.

In development mode, you can add ``--reload`` to cause the server to reload any
time a file is changed on disk.

Running Uvicorn with Gunicorn
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Gunicorn <https://pypi.org/project/gunicorn>`_ is a robust web server that implements process monitoring and automatic
restarts. This can be useful when running Uvicorn in a production environment.

To install Uvicorn and Gunicorn, use the following:

.. code-block:: console

  $ pip install gunicorn uvicorn

Then start Gunicorn using the Uvicorn worker class like this:

.. code-block:: console

  $ gunicorn your_project:app -k uvicorn.workers.UvicornWorker

Hypercorn
---------

`Hypercorn <https://pypi.org/project/hypercorn>`_ is an ASGI server that supports HTTP/1, HTTP/2, and HTTP/3
with an emphasis on protocol support.

Running a project in Hypercorn
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When Hypercorn is installed, a ``hypercorn`` command is available
which runs ASGI applications. Hypercorn needs to be called with the
location of a module containing an ASGI application object, followed
by what the application is called (separated by a colon).

For a typical project, invoking Hypercorn would look like:

.. code-block:: console

  $ hypercorn your_project:app

This will start one process listening on ``127.0.0.1:8000``. It
requires that your project be on the Python path.

----

If you want to deploy your application to another ASGI server,
look up the documentation about how to use a ASGI application with it.
