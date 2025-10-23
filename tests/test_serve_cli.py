import glob
import os
import tempfile
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from pycottas_endpoint.__main__ import cli

runner = CliRunner()


# NOTE: Needs to run last tests, for some reason patching uvicorn as a side effects on follow up tests


@patch("pycottas_endpoint.__main__.uvicorn.run")
def test_serve(mock_run: MagicMock) -> None:
    """Test serve, mock uvicorn.run to prevent API hanging"""
    mock_run.return_value = None
    result = runner.invoke(
        cli,
        [
            "serve",
            "tests/resources/test.nq",
            "tests/resources/test2.ttl",
            "tests/resources/another.jsonld",
        ],
    )
    assert result.exit_code == 0
