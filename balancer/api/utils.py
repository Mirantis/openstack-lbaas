import functools


def http_success_code(code):
    """Attaches response code to a method.

    This decorator associates a response code with a method.  Note
    that the function attributes are directly manipulated; the method
    is not wrapped.
    """

    def decorator(func):
        func.wsgi_code = code
        return func
    return decorator


def verify_tenant(func):
    @functools.wraps(func)
    def __inner(self, req, tenant_id, **kwargs):
        return func(self, req, tenant_id=tenant_id, **kwargs)
    return __inner
