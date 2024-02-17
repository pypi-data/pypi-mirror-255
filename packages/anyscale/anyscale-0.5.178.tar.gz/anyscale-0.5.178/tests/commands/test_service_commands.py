from typing import Generator
from unittest.mock import Mock, patch

from click.testing import CliRunner
import pytest

from anyscale.commands.service_commands import rollback, rollout


@pytest.fixture()
def mock_service_controller() -> Generator[Mock, None, None]:
    mock_service_controller = Mock()

    with patch(
        "anyscale.commands.service_commands.ServiceController",
        new=mock_service_controller,
    ):
        yield mock_service_controller


@pytest.fixture()
def mock_service_controller_rollback() -> Generator[Mock, None, None]:
    """Mock service controller used for `anyscale service rollback` tests."""

    class RollbackServiceController(Mock):
        def get_service_id(self, service_id: str, **kwargs) -> str:
            return service_id

    mock_service_controller = RollbackServiceController()

    with patch(
        "anyscale.commands.service_commands.ServiceController",
        new=mock_service_controller,
    ):
        yield mock_service_controller


def test_rollout_strategy(mock_service_controller):
    """Tests the logic for setting `rollout_strategy`.

    This can either be set by `--rollout-strategy` or the `-i / --in-place` alias (but not both).
    """
    runner = CliRunner()

    # --rollout-strategy provided directly.
    runner.invoke(rollout, args=["--rollout-strategy=IN_PLACE", "-f", "file"])
    mock_service_controller().rollout.assert_called_once_with(
        "file",
        name=None,
        version=None,
        canary_percent=None,
        rollout_strategy="IN_PLACE",
        auto_complete_rollout=True,
        max_surge_percent=None,
    )
    mock_service_controller().reset_mock()

    runner.invoke(rollout, args=["--rollout-strategy=ROLLOUT", "-f", "file"])
    mock_service_controller().rollout.assert_called_once_with(
        "file",
        name=None,
        version=None,
        canary_percent=None,
        rollout_strategy="ROLLOUT",
        auto_complete_rollout=True,
        max_surge_percent=None,
    )
    mock_service_controller().reset_mock()

    # -i / --in-place used.
    runner.invoke(rollout, args=["-i", "-f", "file"])
    mock_service_controller().rollout.assert_called_once_with(
        "file",
        name=None,
        version=None,
        canary_percent=None,
        rollout_strategy="IN_PLACE",
        auto_complete_rollout=True,
        max_surge_percent=None,
    )
    mock_service_controller().reset_mock()

    runner.invoke(rollout, args=["--in-place", "-f", "file"])
    mock_service_controller().rollout.assert_called_once_with(
        "file",
        name=None,
        version=None,
        canary_percent=None,
        rollout_strategy="IN_PLACE",
        auto_complete_rollout=True,
        max_surge_percent=None,
    )
    mock_service_controller().reset_mock()

    runner.invoke(rollout, args=["--max-surge-percent=20", "-f", "file"])
    mock_service_controller().rollout.assert_called_once_with(
        "file",
        name=None,
        version=None,
        canary_percent=None,
        rollout_strategy=None,
        auto_complete_rollout=True,
        max_surge_percent=20,
    )
    mock_service_controller().reset_mock()

    runner.invoke(rollout, args=["--no-auto-complete-rollout", "-f", "file"])
    mock_service_controller().rollout.assert_called_once_with(
        "file",
        name=None,
        version=None,
        canary_percent=None,
        rollout_strategy=None,
        auto_complete_rollout=False,
        max_surge_percent=None,
    )
    mock_service_controller().reset_mock()

    # Provided both -i / --in-place and --rollout-strategy should error.
    result = runner.invoke(
        rollout, args=["-i", "--rollout-strategy=ROLLOUT", "-f", "file"]
    )
    assert result.exception is not None

    result = runner.invoke(
        rollout, args=["--in-place", "--rollout-strategy=ROLLOUT", "-f", "file"]
    )
    assert result.exception is not None


def test_rollback(mock_service_controller_rollback):
    """Tests the rollback command."""

    runner = CliRunner()

    service_id = "fake"

    # CLI command gets service id from the ServiceController. Here, we ensure
    # that the mock controller returns the expected service id.
    mock_service_controller_rollback().get_service_id = Mock(return_value=service_id)

    runner.invoke(rollback, args=["--service-id", service_id])
    mock_service_controller_rollback().rollback.assert_called_once_with(
        service_id, None,
    )
    mock_service_controller_rollback().reset_mock()

    runner.invoke(
        rollback, args=["--service-id", service_id, "--max-surge-percent", "5"]
    )
    mock_service_controller_rollback().rollback.assert_called_once_with(
        service_id, 5,
    )
