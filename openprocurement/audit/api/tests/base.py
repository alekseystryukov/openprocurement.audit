# -*- coding: utf-8 -*-
import unittest
import webtest
import os
from base64 import b64encode
from copy import deepcopy
from datetime import datetime, timedelta
from openprocurement.api.constants import VERSION, SESSION
from requests.models import Response
from urllib import urlencode
from uuid import uuid4

now = datetime.now()
test_monitor_data = {
    "tenderID": "fd9cde88cef04c4a993cd635c94e861c",
    "status": "draft",
}


class PrefixedRequestClass(webtest.app.TestRequest):

    @classmethod
    def blank(cls, path, *args, **kwargs):
        path = '/api/%s%s' % (VERSION, path)
        return webtest.app.TestRequest.blank(path, *args, **kwargs)


class BaseWebTest(unittest.TestCase):

    """Base Web Test to test openprocurement.planning.api.

    It setups the database before each test and delete it after.
    """

    def setUp(self):
        self.app = webtest.TestApp("config:tests.ini", relative_to=os.path.dirname(__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('token', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db

    def tearDown(self):
        del self.couchdb_server[self.db.name]


class BaseMonitorWebTest(BaseWebTest):
    initial_data = test_monitor_data

    def setUp(self):
        super(BaseMonitorWebTest, self).setUp()
        self.create_monitor()

    def create_monitor(self):
        data = deepcopy(self.initial_data)

        response = self.app.post_json('/monitors', {'data': data})
        plan = response.json['data']
        self.plan_token = response.json['access']['token']
        self.plan_id = plan['id']

    def tearDown(self):
        del self.db[self.plan_id]
        super(BaseMonitorWebTest, self).tearDown()
