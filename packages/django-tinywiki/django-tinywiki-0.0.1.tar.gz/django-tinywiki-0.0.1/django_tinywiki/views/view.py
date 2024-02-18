from django.views import View
from django.urls import reverse
from .. import settings
from django.contrib.auth.models import Group
from django.utils.http import urlsafe_base64_encode

class ViewBase(View):
    base_template = settings.TINYWIKI_BASE_TEMPLATE
    header_title = settings.TINYWIKI_TITLE
    css = settings.TINYWIKI_CSS
    context_callback = settings.TINYWIKI_CONTEXT_CALLBACK
    home_url = settings.TINYWIKI_HOME_URL
    page_view_url = settings.TINYWIKI_PAGE_VIEW_URL
    page_edit_url = settings.TINYWIKI_PAGE_EDIT_URL
    page_create_url = settings.TINYWIKI_PAGE_CREATE_URL
    page_new_url = settings.TINYWIKI_PAGE_NEW_URL
    login_url = settings.TINYWIKI_LOGIN_URL
    logout_url = settings.TINYWIKI_LOGOUT_URL
    signup_url = settings.TINYWIKI_SIGNUP_URL

    def get_user_can_create_pages(self,user):
        if user.is_authenticated:
            if user.is_superuser:
                return True

            required_groups = ['wiki-admin','wiki-author']
            for check_group in Group.objects.all():
                if check_group.name in required_groups:
                    return True

        return False

    def get_user_is_wiki_admin(self,user):
        if user.is_authenticated:
            if user.is_superuser:
                return True
            return bool(user.groups.filter(name='wiki-admin'))
        return False
            
    def get_user_can_edit_page(self,user,page=None):
        if page is None:
            return False
        
        if user.is_authenticated:
            if user.is_superuser:
                return True
            if user.groups.filter(name="wiki-admin"):
                return True

            if page.editlock:
                return False

            if page.userlock:
                if page.user.id == user.id:
                    return True
                return False

            if user.groups.filter(name='wiki-author'):
                return True
            
            if user.groups.filter(name='wiki-editor') and user.id == page.user.id:
                return True
            
        return False

    def get_user_can_delete_pages(self,user):
        if user.is_authenticated:
            if user.is_superuser or user.groups.filter(name="wiki-admin"):
                return True
        return False

    def get_context(self,request,page=None,login_url=None,**kwargs):
        if page is None:
            edit_url = ""
        else:
            edit_url = reverse(self.page_edit_url,kwargs={'page':page.slug})

        context = {
            'base_template': self.base_template,
            'css': self.css,
            'user_can_create_pages': self.get_user_can_create_pages(request.user),
            'user_can_edit_page': self.get_user_can_edit_page(request.user,page),
            'user_is_wiki_admin': self.get_user_is_wiki_admin(request.user),
            'header_title': self.header_title,
            'login_url': self.login_url if not login_url else login_url,
            'logout_url': self.logout_url,
            'signup_url': self.signup_url,
            'home_url': self.home_url,
            'edit_url': edit_url,
            'create_url': reverse(self.page_new_url)
        }
        context.update(kwargs)
        context.update(self.context_callback(request))

        return context
    
    def build_login_url(self,request):
        return self.login_url + "?n=" + urlsafe_base64_encode(request.build_absolute_uri().encode('utf-8'))
