from advent.aoc.client import SubmitResponse
import unittest


class SubmitResponseTests(unittest.TestCase):
    def test_is_wrong(self):
        self.assertFalse(SubmitResponse.Ok.is_wrong())
        self.assertFalse(SubmitResponse.TooSoon.is_wrong())
        self.assertFalse(SubmitResponse.AlreadyAnswered.is_wrong())

        self.assertTrue(SubmitResponse.Wrong.is_wrong())
        self.assertTrue(SubmitResponse.TooHigh.is_wrong())
        self.assertTrue(SubmitResponse.TooHigh.is_wrong())
