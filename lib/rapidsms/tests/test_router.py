#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import unittest
import rapidsms


class MockBackend():
    pass


class MockApp():
    
    def __init__(self):
        self.received_message = False

    def receive(self, message):
        self.received_message = True


class TestRouter(unittest.TestCase):

    def setUp(self):
        self.mock_backend = MockBackend()
    
    def tearDown(self):
        pass
    
    def test_dispatches_messages_to_apps(self):
        router = rapidsms.Router()
        mock_app_1 = MockApp()
        mock_app_2 = MockApp()
        router.add_app(mock_app_1)
        router.add_app(mock_app_2)
        
        # create a message, and send it to the router
        message = rapidsms.Message(self.mock_backend, "5678", "Test Message")
        router.receive(message)
        
        # ensure that both apps
        # received the message
        self.assertEqual(mock_app_1.received_message, True,
            "Mock app #1 didn't receive the message")
        self.assertEqual(mock_app_2.received_message, True,
            "Mock app #2 didn't receive the message")


if __name__ == "__main__":
    unittest.main()
