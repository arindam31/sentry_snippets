import pytest
import sentry_sdk
from unittest import TestCase
from unittest.mock import patch
from django.conf import settings

@pytest.fixture(autouse=True)
def disable_all_fixtures(request):
    """
    Prevents all autouse fixtures from running if the `disable_fixtures` mark is present.
    """
    if "disable_fixtures" in request.node.keywords:
        # Use this to skip everything else in autouse scope
        yield
        return

@pytest.mark.disable_fixtures
class TestSentryIntegration(TestCase):
  """Test to demo how to write test for sentry testing so we dont post the sentry event online"""

    @patch("sentry_sdk.transport.HttpTransport.capture_event")
    def test_sentry_event(self, mock_capture_event):
        """
        Verify that Sentry captures an event when ENABLE_SENTRY is True.
        """

        def before_send(event, hint):
            print(f"Before send invoked with event: {event}")
            return event  # Make sure we're passing the event along

        # Set ENABLE_SENTRY to True in the test
        with patch("appointmentmgt.settings.ENABLE_SENTRY", True):
            # Simulate an event
            sample_event = {
                "message": "Test error",
                "level": "error",
            }
            sentry_sdk.init(
                dsn="https://example@o4507816197619712.ingest.de.sentry.io/4507816222720080",
                integrations=[sentry_sdk.integrations.django.DjangoIntegration()],
                before_send=before_send,
            )
            sentry_sdk.capture_event(sample_event)

            # Ensure Sentry captured the event
            self.assertTrue(
                mock_capture_event.called, "Sentry did not capture the event."
            )

            # Verify the content of the event
            captured_event = mock_capture_event.call_args[0][0]
            self.assertIn("message", captured_event)
            self.assertEqual(captured_event["message"], "Test error")
