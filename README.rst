djexcept
========

djexcept is a module that brings flexible exception handling to the
Django web framework.

A weakness of the great Django web framework are its poor builtin error
handling capabilities. In plain Django, you can define custom error
handlers for 4 different exceptions (``SuspiciousOperation``,
``PermissionDenied``, ``Http404`` and a fallback handler for runtime
errors which doesn't even get the exception passed to decide what to do
best).

That is where djexcept kicks in. For every type of exception you like -
even custom ones - it lets you decide how to handle it. It provides a
default exception handler that makes additional information about the
exception available in a template context and then renders a template of
your choice. You can define the template to use, the HTTP status code to
send and even choose the exception handler on a per exception basis or
just use the defaults.

**Note:** djexcept is still a young pice of software that I use in my
Django projects. There may be bugs I haven't found yet. However, the
codebase is reasonably small without lots of magic in it, hence things
shouldn't go terribly wrong. Any bug reports and code review are highly
appreciated.

Installation
------------

It's as easy as this:

::

    pip install djexcept

Compatibility with Django versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

djexcept is tested to work with Django 1.10+, but it should also work
with earlier versions without problems. The contained middleware is
compatible with both the new ``MIDDLEWARE`` as well as the pre 1.10
``MIDDLEWARE_CLASSES`` mechanism.

Getting started
---------------

1. Add ``djexcept.middleware.ExceptionHandlingMiddleware`` to your
   ``MIDDLEWARE`` in ``settings.py``. No modification of
   ``INSTALLED_APPS`` is needed.

2. Add the ``@djexcept.register()`` decorator to every custom exception
   you'd like to be handled by djexcept.

   ::

       import djexcept
       @djexcept.register()
       class MyCustomException(Exception):
           ...

3. For exceptions you haven't defined yourself, you can call the
   ``register()`` function e.g. from inside your ``urls.py`` file like
   so:

   ::

       import djexcept
       djexcept.register(ValueError)

4. Create a template called ``exception.html`` which might contain the
   following:

   ::

       <h1>{{ exc_modname }}</h1>
       <p>An exception of type {{ exc_name }} from {{ exc_module }} occured.</p>
       <p>Exception message: {{ exc }}</p>
       <p>The HTTP status code sent with this page is {{ status }}.</p>

5. Raise an exception you have just registered from within your view and
   watch what happens.

Customization of exception handling
-----------------------------------

Registration parameters
~~~~~~~~~~~~~~~~~~~~~~~

For every type of exception you register, you may specify several
parameters that influence how exceptions of that type are handled. The
following parameters may be passed to ``djexcept.register()`` as keyword
arguments:

-  ``handler``: exception handler (callable or string of type
   ``path.to.module.function``)
-  ``handle_subclasses``: boolean that controls whether **unregistered**
   subclasses of the exception class being registered should be handled
   in the same way as their ancestor

All other keyword arguments are passed through straight to the exception
handler. The following are those that the built-in exception handler
understands:

-  ``template_name``: name of the template to use for rendering the
   error page
-  ``status``: HTTP status code for the error response
-  ``include_request`` whether to include the request in template
   context
-  ``context`` dictionary of which a copy is used as starting point for
   the template context; values in that context won't be overwritten

If some of these keyword arguments are not specified, default values for
them will automatically be inserted according to the ``DJEXCEPT_*``
settings (see below) before the handler is called.

It is at the sole discretion of the chosen exception handler to
interpret these keyword arguments as desired.

The built-in default exception handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

djexcept's built-in exception handler understands all of the keyword
arguments listed above and will create either a
``django.template.response.SimpleTemplateResponse`` or a
``django.template.response.TemplateResponse``, depending on the setting
for ``DJEXCEPT_INCLUDE_REQUEST``.

It will populate the template context with some handy values regarding
the raised exception:

-  ``exc``: the exception object
-  ``exc_name``: the name of the exception type (e.g.
   ``PermissionDenied``)
-  ``exc_module``: the module name of the exception's type (e.g.
   ``django.core.exceptions``)
-  ``exc_modname``: both concatenated, separated by a period (e.g.
   ``django.core.exceptions.PermissionDenied``)
-  ``status``: the HTTP status code used

You can use these variables freely in your template.

Custom exception handlers
~~~~~~~~~~~~~~~~~~~~~~~~~

There is nothing stopping you from writing your own exception handler,
as long as it follows some guidelines.

An exception handler has to be a callable that accepts as positional
arguments the request, the exception object and at least the keyword
arguments listed in the previous section, because these, if unspecified
at time of registration, will be filled with default values. It must
return a ``django.http.response.HttpResponse`` object or ``None``, in
which case the exception isn't handled by djexcept and Django's regular
exception handling kicks in.

If your custom handler doesn't care about some of the mandatory keyword
arguments, you could insert a ``**kwargs`` at the end of its argument
list to catch any extra keyword arguments and have it working even when
new ones are added to djexcept in the future.

**Note:** Please keep in mind that exceptions raised from inside
exception handlers are not handled by djexcept. to prevent creating an
infinite loop.

Here is a simple example that populates the context with some value and
then calls djexcept's built-in handler to construct the response. Please
don't forget to create a copy of the context object before altering it,
because dictionaries are mutable and you might otherwise change the
context of subsequent exceptions.

::

    import time
    from djexcept.handlers import handle_exception

    def my_exception_handler(request, exc, context=None, **kwargs):
        context = dict(context or {})
        context.setdefault("time", time.ctime())
        return handle_exception(request, exc, context=context, **kwargs)

Configuration
-------------

djexcept introduces some new settings that may be used in
``settings.py`` to customize its behaviour. Neither of them are required
for djexcept to work, because all have sensible default values that
should be just fine for most users.

``DJEXCEPT_TEMPLATE_NAME``
~~~~~~~~~~~~~~~~~~~~~~~~~~

(default: ``exception.html``)

Name of the default template to use.

``DJEXCEPT_STATUS``
~~~~~~~~~~~~~~~~~~~

(default: ``400``)

Default HTTP status code for exception pages.

``DJEXCEPT_EXCEPTION_HANDLER``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(default: ``djexcept.handlers.handle_exception``)

Default exception handler. Please specify it as a string of the form
``path.to.module.function``, as known from Django's ``MIDDLEWARE`` list.

``DJEXCEPT_HANDLE_SUBCLASSES``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(default: ``True``)

Whether to treat **unregistered** subclasses of registered exception
types in the same way as their ancestor.

``DJEXCEPT_INCLUDE_REQUEST``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(default: ``True``)

Whether to include the ``request`` object into the template context.

``DJEXCEPT_DISABLE_ON_DEBUG``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(default: ``False``)

Whether to disable djexcept's exception handling when Django's debug
mode is enabled. You might find this useful to see full tracebacks
instead of your custom exception pages while developing your project.

API reference
-------------

Registration
~~~~~~~~~~~~

The public API methods of the ``djexcept.registration`` submodule are
also directly available in ``djexcept`` for convenience.

``djexcept.register(exception_class, **attrs)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Registers the given Exception subclass for error handling with djexcept.

The additional keyword arguments are treated as follows: \* ``handler``:
an exception handler to overwrite the default one \*
``handle_subclasses``: may be used to overwrite the
``DJEXCEPT_HANDLE_SUBCLASSES`` setting on a per exception basis

All other keyword arguments are passed directly to the handler function
when there is an exception to handle.

This function may also be used as a class decorator when defining custom
exceptions.

``djexcept.exceptions.RegistrationError`` is raised if the class was
already registered.

``djexcept.unregister(exception_class)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Unregisters the given exception class from djexcept.

``djexcept.exceptions.RegistrationError`` is raised if the class wasn't
registered.

``djexcept.is_registered(exception_class)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Checks whether the given Exception subclass is registered for use with
djexcept.

``djexcept.is_handled(exception_class)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Checks whether the given exception class is handled by djexcept. If
``DJEXCEPT_HANDLE_SUBCLASSES`` setting is disabled and not overwritten
at registration stage, this function returns the same result as
``djexcept.is_registered()``.

Handlers
~~~~~~~~

``djexcept.handler.handle_exception(request, exc, template_name=None, status=None, include_request=None, context=None)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is djexcept's default exception handler.

A ``django.template.response.SimpleTemplateResponse`` or
``django.template.response.TemplateResponse`` is returned.

Exceptions
~~~~~~~~~~

``djexcept.exceptions.ImproperlyConfigured``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Is raised when something went wrong at settings parsing.

``djexcept.exceptions.RegistrationError``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Is raised when an illegal call to ``djexcept.register()`` or
``djexcept.unregister()`` is made.

Contributing
------------

Contributions are always welcome. Please use issues and pull requests on
GitHub.
