#!/usr/bin/env python

"""Tests for `data_file_profiler_utils` package."""


import unittest
from click.testing import CliRunner

from data_file_profiler_utils import data_file_profiler_utils
from data_file_profiler_utils import cli


class TestData_file_profiler_utils(unittest.TestCase):
    """Tests for `data_file_profiler_utils` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'data_file_profiler_utils.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
