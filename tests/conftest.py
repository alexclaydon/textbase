from liblogger.legacy import local_logger
import pytest


@pytest.fixture(scope='function')
def example_fixture():
    local_logger.info("Setting Up Example Fixture...")
    yield
    local_logger.info("Tearing Down Example Fixture...")
