# tests/test_logthis.py
import unittest
from PyLogDc.logthis import log_this


class TestLogThis(unittest.TestCase):
    def test_log_this(self):
        webhookURL = "https://discord.com/api/webhooks/......."
        try:
            log_this('Test Header', 'Test message', 'info', webhookURL)
        except Exception as e:
            self.fail(f"log_this raised an exception {e}")


if __name__ == '__main__':
    unittest.main()
