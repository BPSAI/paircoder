"""
Tests for MCP Server

Tests server initialization and tool listing.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestMCPServer:
    """Tests for the MCP server module."""

    def test_list_tools_returns_expected_tools(self):
        """list_tools returns all registered tools."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        tool_names = [t["name"] for t in tools]

        # Core task tools
        assert "paircoder_task_list" in tool_names
        assert "paircoder_task_next" in tool_names
        assert "paircoder_task_start" in tool_names
        assert "paircoder_task_complete" in tool_names

        # Planning tools
        assert "paircoder_plan_status" in tool_names
        assert "paircoder_plan_list" in tool_names

        # Context tools
        assert "paircoder_context_read" in tool_names

        # Orchestration tools
        assert "paircoder_orchestrate_analyze" in tool_names
        assert "paircoder_orchestrate_handoff" in tool_names

        # Metrics tools
        assert "paircoder_metrics_record" in tool_names
        assert "paircoder_metrics_summary" in tool_names

        # Trello tools
        assert "paircoder_trello_sync_plan" in tool_names
        assert "paircoder_trello_update_card" in tool_names

    def test_list_tools_contains_parameters(self):
        """Each tool has parameters listed."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()

        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert isinstance(tool["parameters"], list)

    def test_list_tools_task_list_params(self):
        """paircoder_task_list has correct parameters."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        task_list = next(t for t in tools if t["name"] == "paircoder_task_list")

        assert "status" in task_list["parameters"]
        assert "plan" in task_list["parameters"]
        assert "sprint" in task_list["parameters"]

    @patch("bpsai_pair.mcp.server.HAS_MCP", False)
    def test_create_server_raises_without_mcp(self):
        """create_server raises ImportError when MCP not installed."""
        # Need to reimport to get the patched version
        import importlib
        import bpsai_pair.mcp.server as server_module
        importlib.reload(server_module)

        with pytest.raises(ImportError, match="MCP package not installed"):
            server_module.create_server()

    @patch("bpsai_pair.mcp.server.HAS_MCP", False)
    def test_run_server_raises_without_mcp(self):
        """run_server raises ImportError when MCP not installed."""
        import importlib
        import bpsai_pair.mcp.server as server_module
        importlib.reload(server_module)

        with pytest.raises(ImportError, match="MCP package not installed"):
            server_module.run_server()
