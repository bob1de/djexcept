try:
    import typing as T
except ImportError:
    pass

from django.conf import settings
from django.http import HttpResponse
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # pre django 1.10 style middleware
    MiddlewareMixin = object

from .config import config
from .registration import _get_registered_type_attrs


class ExceptionHandlingMiddleware(MiddlewareMixin):
    """
    A Django middleware responsible for djexcept's exception handling.
    """

    def process_exception(
            self,
            request,
            exc,      # type: Exception
            ):  # type: (...) -> T.Optional[HttpResponse]

        if settings.DEBUG and config.disable_on_debug:
            # don't do anything
            return None

        handler_kwargs = {}  # type: T.Dict[str, T.Any]
        handler_kwargs.update(config.default_handler_kwargs)

        exc_type = exc.__class__
        handler_attrs = _get_registered_type_attrs(exc_type)

        if handler_attrs is None:
            # we don't handle this kind of exception, pass it through
            return None

        handler = handler_attrs.get("handler", config.default_handler)
        handler_kwargs.update(handler_attrs)

        # remove reserved attributes from kwargs
        for key in ("handler", "handle_subtypes",):
            try:
                del handler_kwargs[key]
            except KeyError:
                pass

        # finally, call the handler
        return handler(request, exc, **handler_kwargs)
