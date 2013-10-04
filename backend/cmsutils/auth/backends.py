# copied from http://www.carthage.edu/webdev/?p=12
import ldap
from django.contrib.auth.models import User

# Constants
from django.conf import settings

try:
    AUTH_LDAP_MAP=settings.AUTH_LDAP_MAP
except:
    AUTH_LDAP_MAP={}

class LDAPBackend:
    def authenticate(self, username=None, password=None):
        result = self.get_ldap_user(username, AUTH_LDAP_MAP.values())
        if not result:
            return None
        dn, attrs = result

        try:
            # Attempt to bind to the user's DN
            l = ldap.open(settings.AUTH_LDAP_SERVER)
            l.protocol_version = ldap.VERSION3
            l.simple_bind_s(dn ,password)

            # The user existed and authenticated. Get the user
            # record or create one with no privileges.
            dn, user_data = self.get_ldap_translated_data(username)
            try:
                user = User.objects.get(username__exact=username)
                user.first_name = user_data.get('name', None)
                user.last_name = user_data.get('surname', None)
                user.email = user_data.get('mail', None)
            except User.DoesNotExist:
                user = User(username=user_data['login'], first_name=user_data.get('name', None), last_name=user_data.get('surname', None), email=user_data.get('mail', None))
            user.save()
            return user

        except ldap.INVALID_CREDENTIALS:
            # Name or password were bad. Fail.
            print "INVALID Credentials: Could not authenticate %s" % username
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_ldap_user(self, username, attrlist=None):
        # Authenticate the privileged bind user so we can search
        try:
            l = ldap.open(settings.AUTH_LDAP_SERVER)
            l.protocol_version = ldap.VERSION3
            l.simple_bind_s(settings.AUTH_LDAP_BIND_USERNAME, settings.AUTH_LDAP_BIND_PASSWORD)
        except ldap.LDAPError:
            print "ERROR: Could not bind to LDAP with username: %s" % settings.AUTH_LDAP_BIND_USERNAME
            return None

        # try to get the full distinguished name of user and any attributes
        filter = settings.AUTH_LDAP_FILTER % username
        if isinstance(filter, unicode):
            filter = filter.encode('utf8') # filters are UTF-8, RFC 2554.
        attribute_list = AUTH_LDAP_MAP.values()
        result_id = l.search(settings.AUTH_LDAP_SUBTREE, ldap.SCOPE_SUBTREE, filter, attribute_list)
        result_type, result_data = l.result(result_id, 0)

        # If the user does not exist in LDAP, Fail.
        if (len(result_data) != 1):
            return None
        result_data = result_data[0]
        return result_data

    def copy_ldap_attrs(self, mapdict, attrdict):
        # copy the results to an dictionary instance
        result_dict = mapdict.copy()
        for key,value in result_dict.items():
            result_dict[key]=attrdict.get(value, [None])[0]
        return result_dict

    def get_ldap_translated_data(self, username):
        res = self.get_ldap_user(username, attrlist=AUTH_LDAP_MAP.values())
        if not res:
            return None
        result_dict = self.copy_ldap_attrs(AUTH_LDAP_MAP, res[1])
        return res[0], result_dict
