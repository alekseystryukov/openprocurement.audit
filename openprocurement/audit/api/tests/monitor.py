import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.audit.api.tests.base import test_monitor_data, BaseWebTest


class MonitorsResourceTest(BaseWebTest):
    initial_data = test_monitor_data

    def test_empty_listing(self):
        response = self.app.get('/monitors')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertNotIn('{\n    "', response.body)
        self.assertNotIn('callback({', response.body)
        self.assertEqual(response.json['next_page']['offset'], '')
        self.assertNotIn('prev_page', response.json)


def suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(MonitorsResourceTest))
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
