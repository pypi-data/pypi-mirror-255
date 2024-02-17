#!/usr/bin/env python

"""Tests for `simple_template_toolkit` package."""


import unittest
from click.testing import CliRunner

from simple_template_toolkit import simple_template_toolkit
from simple_template_toolkit import cli


class TestSimple_template_toolkit(unittest.TestCase):
    """Tests for `simple_template_toolkit` package."""

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
        assert 'simple_template_toolkit.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
