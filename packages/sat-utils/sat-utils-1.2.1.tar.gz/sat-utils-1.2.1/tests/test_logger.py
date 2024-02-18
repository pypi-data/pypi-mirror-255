import logging
import os
from unittest import mock

TMP_FILE = "/tmp/test.log"


@mock.patch.dict(os.environ, {"USELESS": "VALUE"}, clear=True)
def test_default_logger(caplog):
    """Test the default logger"""
    from sat.logs import SATLogger

    logger = SATLogger()
    logger.info("Test message")
    assert "Test message" in caplog.text
    logger.debug("DEBUG message")
    assert "DEBUG message" not in caplog.text
    logger.error("ERROR message")
    assert "ERROR message" in caplog.text


@mock.patch.dict(os.environ, {"DEBUG": "1"}, clear=True)
def test_debug_logger(caplog):
    """Test the debug logger"""
    from sat.logs import SATLogger

    logger = SATLogger()
    logger.debug("DEBUG message")
    assert "DEBUG message" in caplog.text


def test_add_handlers(caplog):
    """Test adding handlers to the logger"""
    from sat.logs import SATLogger

    logger = SATLogger()
    logger.add_handlers([(logging.FileHandler(TMP_FILE), logging.Formatter("%(message)s"))])
    logger.info("Test message")
    assert "Test message" in caplog.text
    assert os.path.exists(TMP_FILE)
