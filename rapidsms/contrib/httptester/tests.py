from rapidsms.tests.harness import RapidTest
from rapidsms.contrib.httptester.storage import store_and_queue


class StorageTest(RapidTest):

    disable_phases = True

    def test_store_and_queue(self):
        """store_and_queue should use receive() API correctly"""
        store_and_queue("httptester", "1112223333", "hi there!")
        self.assertEqual(self.inbound[0].text, "hi there!")
