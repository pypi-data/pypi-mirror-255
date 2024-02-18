from __future__ import annotations
import logging
from django.http import HttpResponseForbidden
from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.views import LoginView, LogoutView, redirect_to_login
from django.contrib.auth.models import AbstractUser
from django.views.generic.base import RedirectView
    
try:
    from rest_framework.views import APIView
    _with_rest_framework = True
except ImportError:
    _with_rest_framework = False


logger = logging.getLogger(__name__)

class StaffAuthorizationMiddleware:
    """
    A middleware that restrict access only to staff users by default.

    Ignored for:
    - Class-based view inheriting from an `AccessMixin`
    - Django Rest Framework's API views having a non-empty `permission_classes` attribute
    - admin panel, LoginView, LogoutView, RedirectView
    - request paths listed in AUTHORIZATION_MIDDLEWARE_BYPASS settings
    """
    AUTHORIZATION_MIDDLEWARE_BYPASS: list[str] = getattr(settings, "AUTHORIZATION_MIDDLEWARE_BYPASS", [])

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path in self.AUTHORIZATION_MIDDLEWARE_BYPASS:
            return # no default permission

        if view_func.__module__.startswith("django.contrib.admin."):
            return # no default permission
        
        try:
            view = view_func.view_class
            # class-based view
        except AttributeError:
            try:
                view = view_func.cls
                # API viewset (Django Rest Framework)
            except AttributeError:
                view = None
                # function-based view

        if not view:
            # function-based view
            if not self.is_authorized(request.user):
                logger.debug("function-based view %s: %s authorization required", ".".join([view_func.__module__, view_func.__name__]), self.authorization_name)
                return self._deny_or_login(request)
        
        elif issubclass(view, (LoginView, LogoutView, RedirectView)):
            return # no default permission

        elif _with_rest_framework and issubclass(view, APIView):
            # API view (Django Rest Framework)
            if not view.permission_classes:
                if not self.is_authorized(request.user):
                    logger.debug("no permission_classes for rest_framework view %s: %s authorization required required", ".".join([view.__module__, view.__name__]), self.authorization_name)
                    return HttpResponseForbidden() # do not redirect to login page (this is supposed to be accessed by javascript or as an API)

        else:
            # Standard class-based view
            if not issubclass(view, AccessMixin):
                if not self.is_authorized(request.user):
                    logger.debug("no AccessMixin for view %s: %s authorization required", ".".join([view.__module__, view.__name__]), self.authorization_name)
                    return self._deny_or_login(request)               
    
    authorization_name = 'staff'

    def is_authorized(self, user: AbstractUser):
        return user.is_staff

    def _deny_or_login(self, request):
        if request.user.is_authenticated:
            return HttpResponseForbidden()
        else:
            return redirect_to_login(next=request.get_full_path())


class SuperuserAuthorizationMiddleware(StaffAuthorizationMiddleware):
    """
    A middleware that restrict access only to superusers by default.
    
    Ignored for:
    - Class-based view inheriting from an `AccessMixin`
    - Django Rest Framework's API views having a non-empty `permission_classes` attribute
    - admin panel, LoginView, LogoutView, RedirectView
    - request paths listed in AUTHORIZATION_MIDDLEWARE_BYPASS settings
    """
    authorization_name = 'superuser'

    def is_authorized(self, user: AbstractUser):
        return user.is_superuser
