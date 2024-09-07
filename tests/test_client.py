from advent.client import AocClientConfig, SubmitResponse
import unittest


class SubmitResponseTests(unittest.TestCase):
    def test_is_wrong(self):
        self.assertFalse(SubmitResponse.Ok.is_wrong())
        self.assertFalse(SubmitResponse.TooSoon.is_wrong())
        self.assertFalse(SubmitResponse.AlreadyAnswered.is_wrong())

        self.assertTrue(SubmitResponse.Wrong.is_wrong())
        self.assertTrue(SubmitResponse.TooHigh.is_wrong())
        self.assertTrue(SubmitResponse.TooHigh.is_wrong())


class AocClientConfigTests(unittest.TestCase):
    def test_parse_typical_file(self):
        config = AocClientConfig.load_from_str(
            "password= \t foobar \r\n  session_id\t= 180213312312\n"
        )

        self.assertEqual(config.password, "foobar")
        self.assertEqual(config.session_id, "180213312312")
