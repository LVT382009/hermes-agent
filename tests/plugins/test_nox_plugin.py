"""
Tests for NOX Plugin
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch

from plugins.nox import NOXPlugin


@pytest.fixture
def nox_plugin():
    """Create a NOX plugin instance."""
    return NOXPlugin()


@pytest.fixture
def temp_status_file(tmp_path):
    """Create a temporary status file."""
    status_file = tmp_path / "nox_status.json"
    return status_file


class TestNOXPlugin:
    """Test NOX plugin functionality."""
    
    def test_plugin_initialization(self, nox_plugin):
        """Test plugin initializes correctly."""
        assert nox_plugin.name == "nox"
        assert nox_plugin.version == "1.0.0"
        assert nox_plugin.description == "Latency-constrained proof-carrying e-graph compiler"
    
    def test_plugin_disabled_by_default(self, nox_plugin):
        """Test plugin is disabled by default."""
        assert not nox_plugin.is_enabled()
    
    def test_enable_plugin(self, nox_plugin, temp_status_file):
        """Test enabling the plugin."""
        # Mock the status file path
        nox_plugin.status_file = temp_status_file
        
        result = nox_plugin.enable()
        
        assert result.get("success") is True
        assert nox_plugin.is_enabled()
        
        # Check status file was created
        with open(temp_status_file, 'r') as f:
            status = json.load(f)
            assert status["enabled"] is True
            assert status["mode"] == "balanced"
    
    def test_disable_plugin(self, nox_plugin, temp_status_file):
        """Test disabling the plugin."""
        # Mock the status file path
        nox_plugin.status_file = temp_status_file
        
        # First enable
        nox_plugin.enable()
        assert nox_plugin.is_enabled()
        
        # Then disable
        result = nox_plugin.disable()
        
        assert result.get("success") is True
        assert not nox_plugin.is_enabled()
        
        # Check status file was updated
        with open(temp_status_file, 'r') as f:
            status = json.load(f)
            assert status["enabled"] is False
    
    def test_get_status(self, nox_plugin):
        """Test getting plugin status."""
        status = nox_plugin.get_status()
        
        assert "enabled" in status
        assert "stats" in status
        assert isinstance(status["stats"], dict)
    
    def test_post_llm_call_when_disabled(self, nox_plugin):
        """Test post_llm_call returns original response when disabled."""
        response = "This is a test response"
        messages = []
        config = {}
        
        result = nox_plugin.post_llm_call(response, messages, config)
        
        assert result == response
    
    def test_post_llm_call_when_enabled(self, nox_plugin, temp_status_file):
        """Test post_llm_call optimizes response when enabled."""
        # Mock the status file path
        nox_plugin.status_file = temp_status_file
        
        # Enable the plugin
        nox_plugin.enable()
        
        response = "This is a test response"
        messages = []
        config = {}
        
        result = nox_plugin.post_llm_call(response, messages, config)
        
        # Result should be a string (optimized or original)
        assert isinstance(result, str)
    
    def test_handle_enable_command(self, nox_plugin, temp_status_file):
        """Test /nox enable command."""
        # Mock the status file path
        nox_plugin.status_file = temp_status_file
        
        result = nox_plugin.handle_command(["enable"])
        
        assert "enabled" in result.lower()
        assert nox_plugin.is_enabled()
    
    def test_handle_disable_command(self, nox_plugin, temp_status_file):
        """Test /nox disable command."""
        # Mock the status file path
        nox_plugin.status_file = temp_status_file
        
        # First enable
        nox_plugin.enable()
        
        result = nox_plugin.handle_command(["disable"])
        
        assert "disabled" in result.lower()
        assert not nox_plugin.is_enabled()
    
    def test_handle_status_command(self, nox_plugin):
        """Test /nox status command."""
        result = nox_plugin.handle_command(["status"])
        
        assert "status" in result.lower()
        assert "NOX" in result
    
    def test_handle_unknown_command(self, nox_plugin):
        """Test handling unknown command."""
        result = nox_plugin.handle_command(["unknown"])
        
        assert "Unknown NOX command" in result
    
    def test_handle_empty_command(self, nox_plugin):
        """Test handling empty command (should show status)."""
        result = nox_plugin.handle_command([])
        
        assert "status" in result.lower()
    
    def test_determine_path_fast(self, nox_plugin):
        """Test path determination for short responses."""
        response = "Short response"
        config = {}
        
        path = nox_plugin._determine_path(response, config)
        
        assert path == "fast"
    
    def test_determine_path_deep(self, nox_plugin):
        """Test path determination for long responses."""
        response = "A" * 1500  # Long response
        config = {}
        
        path = nox_plugin._determine_path(response, config)
        
        assert path == "deep"
    
    def test_determine_path_with_config(self, nox_plugin):
        """Test path determination respects config override."""
        response = "Short response"
        config = {"path": "deep"}
        
        path = nox_plugin._determine_path(response, config)
        
        assert path == "deep"
    
    def test_apply_nox_validation_with_parse_errors(self, nox_plugin):
        """Test NOX validation falls back on parse errors."""
        response = "Invalid response that cannot be parsed"
        messages = []
        config = {}
        
        optimized_response, metadata = nox_plugin.apply_nox_validation(
            response, messages, config
        )
        
        # Should fall back to original
        assert optimized_response == response
        assert metadata["fallback_triggered"] is True
        assert "Parse errors" in metadata["reason"]
    
    def test_stats_tracking(self, nox_plugin, temp_status_file):
        """Test statistics are tracked correctly."""
        # Mock the status file path
        nox_plugin.status_file = temp_status_file
        
        # Enable plugin
        nox_plugin.enable()
        
        # Get initial stats
        initial_stats = nox_plugin.get_status()["stats"]
        
        # Simulate some validations
        nox_plugin._stats["total_validations"] = 10
        nox_plugin._stats["total_time_ms"] = 500.0
        nox_plugin._stats["total_token_savings"] = 1000
        
        # Get updated stats
        updated_stats = nox_plugin.get_status()["stats"]
        
        assert updated_stats["total_validations"] == 10
        assert updated_stats["total_time_ms"] == 500.0
        assert updated_stats["total_token_savings"] == 1000


class TestNOXPluginIntegration:
    """Test NOX plugin integration with Hermes."""
    
    def test_plugin_discovery(self):
        """Test NOX plugin can be discovered."""
        # This test verifies the plugin structure is correct
        plugin_dir = Path(__file__).parent.parent.parent / "plugins" / "nox"
        
        assert plugin_dir.exists()
        assert (plugin_dir / "__init__.py").exists()
        assert (plugin_dir / "plugin.yaml").exists()
    
    def test_plugin_yaml_structure(self):
        """Test plugin.yaml has required fields."""
        plugin_dir = Path(__file__).parent.parent.parent / "plugins" / "nox"
        plugin_yaml = plugin_dir / "plugin.yaml"
        
        import yaml
        
        with open(plugin_yaml, 'r') as f:
            data = yaml.safe_load(f)
        
        assert "name" in data
        assert data["name"] == "nox"
        assert "version" in data
        assert "description" in data
        assert "hooks" in data
        assert "commands" in data
        assert "settings" in data
    
    def test_plugin_has_required_methods(self, nox_plugin):
        """Test plugin has all required methods."""
        assert hasattr(nox_plugin, "post_llm_call")
        assert hasattr(nox_plugin, "handle_command")
        assert hasattr(nox_plugin, "enable")
        assert hasattr(nox_plugin, "disable")
        assert hasattr(nox_plugin, "get_status")
        assert hasattr(nox_plugin, "is_enabled")
        assert hasattr(nox_plugin, "apply_nox_validation")


class TestNOXPluginPerformance:
    """Test NOX plugin performance characteristics."""
    
    def test_fast_path_latency(self, nox_plugin, temp_status_file):
        """Test fast path stays within latency budget."""
        import time
        
        # Mock the status file path
        nox_plugin.status_file = temp_status_file
        nox_plugin.enable()
        
        response = "Short test response"
        messages = []
        config = {}
        
        start = time.time()
        result = nox_plugin.post_llm_call(response, messages, config)
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        # Fast path should be < 100ms
        assert elapsed < 100, f"Fast path took {elapsed}ms, exceeds 100ms budget"
    
    def test_plugin_overhead_when_disabled(self, nox_plugin):
        """Test plugin has minimal overhead when disabled."""
        import time
        
        response = "Test response"
        messages = []
        config = {}
        
        start = time.time()
        result = nox_plugin.post_llm_call(response, messages, config)
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        # When disabled, should be very fast (< 1ms)
        assert elapsed < 1, f"Disabled plugin took {elapsed}ms, exceeds 1ms budget"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
