# -*- coding: utf-8 -*-
from Globals import DevelopmentMode
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


class LoginAs(BrowserView):
    """ Form for adding new commercial websites """

    template = ViewPageTemplateFile('login_as.pt')

    def __call__(self):
        self.portal_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state'
        )
        self.acl_users = getToolByName(self.context, 'acl_users')

        # Hide the editable-object border
        self.request.set('disable_border', True)

        # Handle clicks
        self.actions()

        return self.template()

    def actions(self):
        """Login the user"""
        if 'user' in self.request.keys():
            self.errors = {}
            user = self.request['user']
            userob = self.acl_users.getUserById(user)
            if userob is None:
                self.errors['user'] = user
                return

            if hasattr(self.acl_users.session, 'setupSession'):
                # Plone 3
                self.acl_users.session.setupSession(
                    user, self.request.response
                )
            else:
                # Plone 4
                self.acl_users.session._setupSession(
                    user, self.request.response
                )

            self.request.response.redirect(self.portal_state.portal_url())

    def members(self):
        """ lists all members on this Plone site """

        membership = getToolByName(self.context, 'portal_membership')
        members = membership.listMembers()

        results = []

        for member in members:
            results.append({'username': member.id,
                            'fullname': member.getProperty('fullname')})

        return results

    def has_many_users(self):
        ''' Check if the sitre has many users

        Since plone5 this is stored on the registry,
        while before it was a portal_property.

        If nothing is working return True
        '''
        try:
            return api.portal.get_registry_record('plone.many_users')
        except api.exc.InvalidParameterError:
            pass
        sp = api.portal.get_tool('portal_properties').get('site_properties')
        if sp:
            sp.getProperty('many_users', True)
        return True

    def is_dev_mode(self):
        return DevelopmentMode
