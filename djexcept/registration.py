import inspect

from .config import config, load_exception_handler
from .exceptions import RegistrationError


_registered_exc_types = {}


def register(exc_type=None, **attrs):
    """
    Registers the given Exception subclass for error handling with
    djexcept.

    The additional keyword arguments are treated as follows:
        * handler: an exception handler to ovewrite the
          DJEXCEPT_EXCEPTION_HANDLER setting
        * handle_subtypes: may be used to overwrite the
          DJEXCEPT_HANDLE_SUBTYPES setting on a per exception basis

    All other keyword arguments are passed directly to the handler
    function when there is an exception to handle. See documentation
    for their meanings.

    This function may also be used as a class decorator when defining
    custom exceptions.

    djexcept.exceptions.RegistrationError is raised if the class was
    already registered.
    """

    def register(exc_type):
        if not issubclass(exc_type, Exception):
            raise RegistrationError(
                    "{} is not a subclass of Exception".format(exc_type))
        if is_registered(exc_type):
            raise RegistrationError(
                    "{} is already registered with djexcept".format(exc_type))
        if isinstance(attrs.get("handler"), str):
            # lazy-import the handler
            attrs["handler"] = load_exception_handler(attrs["handler"])
        _registered_exc_types[exc_type] = attrs
        return exc_type

    # Return a class decorator if class is not given
    if exc_type is None:
        return register
    # Register the class
    return register(exc_type)

def unregister(exc_type):
    """
    Unregisters the given exception class from djexcept.

    djexcept.exceptions.RegistrationError is raised if the class wasn't
    registered.
    """
    try:
        del _registered_exc_types[exc_type]
    except KeyError:
        raise RegistrationError(
                "{} is not registered with djexcept".format(exc_type))

def is_registered(exc_type):
    """
    Checks whether the given Exception subclass is registered for use
    with djexcept.
    """

    return exc_type in _registered_exc_types

def is_handled(exc_type):
    """
    Checks whether the given exception class is handled by djexcept.
    If DJEXCEPT_HANDLE_SUBTYPES setting is disabled and not overwritten
    at registration stage, this function returns the same result as
    djexcept.is_registered().
    """

    return _get_closest_registered_type(exc_type) is not None


def _get_closest_registered_type(exc_type):
    """
    Searches the closest registered ancestor of the given exception
    class and returns it or None, if none exists. handle_subtypes
    attributes are considered.
    """

    mro = inspect.getmro(exc_type)

    # filter registered types for those that occur in the mro;
    # require exact match if handle_subtypes is disabled
    types = filter(
            lambda t:
                t in mro \
                and (t is exc_type \
                     or _registered_exc_types[t] \
                        .get("handle_subtypes", config.handle_subtypes)),
            _registered_exc_types.keys())

    # choose the closest ancestor of exc_type
    return min(types, default=None, key=lambda t: mro.index(t))

def _get_registered_type_attrs(exc_type, exact=False):
    """
    Return the attributes provided when the given class was registered
    or None, if it isn't registered at all.

    If exact is set to True, all settings of handle_subtypes are ignored
    and only an exact match in the registration database will be
    considered valid.
    """

    if not exact:
        exc_type = _get_closest_registered_type(exc_type)

    return _registered_exc_types.get(exc_type)
