
import subprocess

from django.contrib.auth.models import User
from django import test

from nose.tools import eq_

import test_utils

from funfactory.urlresolvers import reverse
from funfactory.manage import path

MOZILLIAN = dict(email='u000001@mozillians.org', uniq_id='7f3a67u000001')
MOZ_ASSER = 'abcdefghijklmnop'
PENDING = dict(email='u000003@mozillians.org', uniq_id='7f3a67u000003')
PND_ASSER = 'qrstuvwxyz'
OTHER_MOZILLIAN = dict(email='u000098@mozillians.org', uniq_id='7f3a67u000098')
OTH_ASSER = 'somelongstring'
AMANDEEP_NAME = 'Amandeep McIlrath'
AMANDEEP_VOUCHER = '7f3a67u000001'
AMANDA_NAME = 'Amanda Younger'

call = lambda x: subprocess.Popen(x, stdout=subprocess.PIPE).communicate()

class LDAPTestCase(test_utils.TestCase):
    @classmethod
    def setup_class(cls):
        import os
        os.environ['OPENLDAP_DB_PATH'] = '/home/vagrant/openldap-db'
        call(path('directory/devslapd/bin/x-rebuild'))
    def setUp(self):
        self.pending_client   = mozillian_client(email=PENDING['email'],
                                                 assertion=PND_ASSER)
        self.mozillian_client = mozillian_client(email=MOZILLIAN['email'],
                                                 assertion=MOZ_ASSER)

def mozillian_client(email, assertion):
    """Create and return an authorized Mozillian test client.

    We can't use client.login because of bugs like
    https://code.djangoproject.com/ticket/11475

    We step the client through the actual auth process so 
    sessions will be all setup properly.
    """
    client = test.Client()
    client.get(reverse('home'))
    data = dict(assertion=assertion, mode='register')
    r = client.post(reverse('browserid_login'), data, follow=True)
    eq_(email, str(r.context['user']))

    # Why is this done here?
    user = User.objects.get(email=email)
    user.get_profile().is_confirmed = True
    user.get_profile().save()

    return client
