from __future__ import annotations
from django.views import generic
from django.contrib.auth import mixins as auth_mixins
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

class IsStaffMixin(auth_mixins.UserPassesTestMixin, generic.base.ContextMixin, generic.View):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(next=self.request.get_full_path())


class IsSuperuserMixin(IsStaffMixin):
    def test_func(self):
        return self.request.user.is_superuser


class IsAuthenticatedMixin(IsStaffMixin):
    def test_func(self):
        return self.request.user.is_authenticated


class AllowAnonymousMixin(IsStaffMixin):
    def test_func(self):
        return True
