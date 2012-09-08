import functools
import logging

import webob.exc

LOG = logging.getLogger(__name__)


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
    def __inner(self, req, tenant_id, *args, **kwargs):
        if hasattr(req, 'context') and tenant_id != req.context.tenant_id:
            LOG.info('User is not authorized to access this tenant.')
            raise webob.exc.HTTPUnauthorized
        return func(self, req, tenant_id, *args, **kwargs)
    return __inner


def require_admin(func):
    @functools.wraps(func)
    def __inner(self, req, *args, **kwargs):
        if hasattr(req, 'context') and not req.context.is_admin:
            LOG.info('User has no admin priviledges.')
            raise webob.exc.HTTPUnauthorized
        return func(self, req, *args, **kwargs)
    return __inner
