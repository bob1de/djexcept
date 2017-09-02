try:
    import typing as T
except ImportError:
    pass

from django.template.response import SimpleTemplateResponse, TemplateResponse

from .util import populate_context


def handle_exception(
        request,
        exc,                   # type: Exception
        template_name=None,    # type: T.Optional[str]
        status=None,           # type: T.Optional[int]
        include_request=None,  # type: T.Optional[bool]
        context=None,          # type: T.Optional[T.Dict[T.Any, T.Any]]
        ):  # type: (...) -> SimpleTemplateResponse
    """
    This is djexcept's default exception handler.

    It uses djexcept.util.populate_context() to populate the context with
    some handy values regarding the exception that you can use in your
    template. Please see the API reference for details about these values.

    A django.template.response.SimpleTemplateResponse or
    django.template.response.TemplateResponse is returned.
    """

    # initialize context if needed and shallow-copy it afterwards
    context = dict(context or {})

    # populate it with the default values
    populate_context(context, exc, status=status)

    if include_request:
        return TemplateResponse(request, template_name, context=context,
                                status=status)
    else:
        return SimpleTemplateResponse(template_name, context=context,
                                      status=status)
