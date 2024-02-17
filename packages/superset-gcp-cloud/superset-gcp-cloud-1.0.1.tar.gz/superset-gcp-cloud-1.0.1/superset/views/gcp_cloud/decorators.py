import functools
import logging

from flask import (
    g,
    flash,
    redirect,
    request,
    url_for, 
)

from flask_appbuilder._compat import as_unicode

from flask_appbuilder.const import (
    FLAMSG_ERR_SEC_ACCESS_DENIED,
    LOGMSG_ERR_SEC_ACCESS_DENIED,
)

log = logging.getLogger(__name__)

def has_access_gcp(f):
    """
    Use this decorator to enable granular security permissions to your methods.
    Permissions will be associated to a role, and roles are associated to users.

    By default the permission's name is the methods name.
    """
    def wraps(self, *args, **kwargs):
        user = g.user
        if user.is_anonymous:
            flash(as_unicode(FLAMSG_ERR_SEC_ACCESS_DENIED), "danger")
            
        roles = user.roles
        log.error(f"*********\nRoles:{roles}\n*************")
        str_roles = []
        for role in roles:
            str_roles.append(str(role))
        log.error(f"*********\nRoles:{str_roles}\n*************")
        if 'Opportunity Files' in str_roles:
            return f(self, *args, **kwargs)
        else:
            log.warning(
                LOGMSG_ERR_SEC_ACCESS_DENIED, 'GCP FILES', self.__class__.__name__
            )
            flash(as_unicode(FLAMSG_ERR_SEC_ACCESS_DENIED), "danger")
        return redirect(
            url_for(
                self.appbuilder.sm.auth_view.__class__.__name__ + ".login",
                next=request.url,
            )
        )

    f._permission_name = 'GCP_FILES'
    return functools.update_wrapper(wraps, f)