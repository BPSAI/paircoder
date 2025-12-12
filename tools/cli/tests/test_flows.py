"""Tests for the flows module."""

import pytest
from pathlib import Path

from bpsai_pair import flows


class TestParseFlow:
    """Tests for parse_flow function."""

    def test_parse_valid_flow(self, tmp_path):
        """Parse a valid flow file with all fields."""
        flow_file = tmp_path / "test-flow.md"
        flow_file.write_text("""---
name: test-flow
description: A test flow for unit testing
tags: [testing, demo]
version: "2.0"
---

# Test Flow

This is the body of the test flow.

## Steps

1. Do something
2. Do something else
""")

        flow = flows.parse_flow(flow_file)

        assert flow.name == "test-flow"
        assert flow.description == "A test flow for unit testing"
        assert flow.tags == ["testing", "demo"]
        assert flow.version == "2.0"
        assert flow.path == flow_file
        assert "# Test Flow" in flow.body
        assert "1. Do something" in flow.body

    def test_parse_minimal_flow(self, tmp_path):
        """Parse a flow with only required fields."""
        flow_file = tmp_path / "minimal.md"
        flow_file.write_text("""---
name: minimal
description: Minimal flow
---

Simple body.
""")

        flow = flows.parse_flow(flow_file)

        assert flow.name == "minimal"
        assert flow.description == "Minimal flow"
        assert flow.tags == []
        assert flow.version == "1.0"  # default
        assert flow.body == "Simple body.\n"

    def test_parse_flow_missing_front_matter(self, tmp_path):
        """Raise error when front-matter is missing."""
        flow_file = tmp_path / "no-front-matter.md"
        flow_file.write_text("# Just markdown\n\nNo front matter here.")

        with pytest.raises(ValueError, match="must start with '---'"):
            flows.parse_flow(flow_file)

    def test_parse_flow_missing_closing_delimiter(self, tmp_path):
        """Raise error when closing delimiter is missing."""
        flow_file = tmp_path / "unclosed.md"
        flow_file.write_text("""---
name: unclosed
description: Missing close

Body without closing delimiter.
""")

        with pytest.raises(ValueError, match="missing closing '---'"):
            flows.parse_flow(flow_file)

    def test_parse_flow_missing_name(self, tmp_path):
        """Raise error when name field is missing."""
        flow_file = tmp_path / "no-name.md"
        flow_file.write_text("""---
description: Flow without name
---

Body.
""")

        with pytest.raises(ValueError, match="missing required 'name'"):
            flows.parse_flow(flow_file)

    def test_parse_flow_missing_description(self, tmp_path):
        """Raise error when description field is missing."""
        flow_file = tmp_path / "no-desc.md"
        flow_file.write_text("""---
name: no-desc
---

Body.
""")

        with pytest.raises(ValueError, match="missing required 'description'"):
            flows.parse_flow(flow_file)

    def test_parse_flow_invalid_yaml(self, tmp_path):
        """Raise error when YAML is invalid."""
        flow_file = tmp_path / "bad-yaml.md"
        flow_file.write_text("""---
name: bad
description: [invalid yaml
---

Body.
""")

        with pytest.raises(ValueError, match="Invalid YAML"):
            flows.parse_flow(flow_file)

    def test_parse_flow_file_not_found(self, tmp_path):
        """Raise error when file doesn't exist."""
        flow_file = tmp_path / "nonexistent.md"

        with pytest.raises(FileNotFoundError):
            flows.parse_flow(flow_file)

    def test_parse_flow_numeric_version(self, tmp_path):
        """Handle numeric version by converting to string."""
        flow_file = tmp_path / "numeric-version.md"
        flow_file.write_text("""---
name: numeric
description: Numeric version
version: 1.5
---

Body.
""")

        flow = flows.parse_flow(flow_file)
        assert flow.version == "1.5"

    def test_parse_flow_empty_body(self, tmp_path):
        """Parse flow with empty body."""
        flow_file = tmp_path / "empty-body.md"
        flow_file.write_text("""---
name: empty
description: Empty body flow
---
""")

        flow = flows.parse_flow(flow_file)
        assert flow.body == ""


class TestDiscoverFlows:
    """Tests for discover_flows function."""

    def test_discover_from_paircoder_flows(self, tmp_path):
        """Discover flows from .paircoder/flows/ directory."""
        flows_dir = tmp_path / ".paircoder" / "flows"
        flows_dir.mkdir(parents=True)

        (flows_dir / "flow-a.md").write_text("""---
name: flow-a
description: Flow A
---

Body A.
""")
        (flows_dir / "flow-b.md").write_text("""---
name: flow-b
description: Flow B
---

Body B.
""")

        discovered = flows.discover_flows(tmp_path)

        assert len(discovered) == 2
        assert discovered[0].name == "flow-a"
        assert discovered[1].name == "flow-b"

    def test_discover_from_fallback_flows(self, tmp_path):
        """Discover flows from flows/ fallback directory."""
        flows_dir = tmp_path / "flows"
        flows_dir.mkdir()

        (flows_dir / "fallback.md").write_text("""---
name: fallback
description: Fallback flow
---

Body.
""")

        discovered = flows.discover_flows(tmp_path)

        assert len(discovered) == 1
        assert discovered[0].name == "fallback"

    def test_discover_nested_flows(self, tmp_path):
        """Discover flows in nested subdirectories."""
        nested_dir = tmp_path / ".paircoder" / "flows" / "category" / "subcategory"
        nested_dir.mkdir(parents=True)

        (nested_dir / "nested.md").write_text("""---
name: nested
description: Nested flow
---

Body.
""")

        discovered = flows.discover_flows(tmp_path)

        assert len(discovered) == 1
        assert discovered[0].name == "nested"

    def test_discover_priority_paircoder_over_fallback(self, tmp_path):
        """Prefer .paircoder/flows/ over flows/ for duplicate names."""
        paircoder_dir = tmp_path / ".paircoder" / "flows"
        paircoder_dir.mkdir(parents=True)
        fallback_dir = tmp_path / "flows"
        fallback_dir.mkdir()

        (paircoder_dir / "duplicate.md").write_text("""---
name: duplicate
description: From .paircoder
---

Body from .paircoder.
""")
        (fallback_dir / "duplicate.md").write_text("""---
name: duplicate
description: From fallback
---

Body from fallback.
""")

        discovered = flows.discover_flows(tmp_path)

        assert len(discovered) == 1
        assert discovered[0].description == "From .paircoder"

    def test_discover_skips_invalid_flows(self, tmp_path):
        """Skip invalid flow files during discovery."""
        flows_dir = tmp_path / ".paircoder" / "flows"
        flows_dir.mkdir(parents=True)

        # Valid flow
        (flows_dir / "valid.md").write_text("""---
name: valid
description: Valid flow
---

Body.
""")
        # Invalid flow (no front matter)
        (flows_dir / "invalid.md").write_text("Just markdown, no front matter.")

        discovered = flows.discover_flows(tmp_path)

        assert len(discovered) == 1
        assert discovered[0].name == "valid"

    def test_discover_empty_directory(self, tmp_path):
        """Return empty list when no flows exist."""
        discovered = flows.discover_flows(tmp_path)
        assert discovered == []

    def test_discover_sorted_by_name(self, tmp_path):
        """Return flows sorted alphabetically by name."""
        flows_dir = tmp_path / ".paircoder" / "flows"
        flows_dir.mkdir(parents=True)

        # Create in non-alphabetical order
        for name in ["zebra", "apple", "mango"]:
            (flows_dir / f"{name}.md").write_text(f"""---
name: {name}
description: {name.title()} flow
---

Body.
""")

        discovered = flows.discover_flows(tmp_path)

        assert [f.name for f in discovered] == ["apple", "mango", "zebra"]

    def test_discover_ignores_non_md_files(self, tmp_path):
        """Ignore non-markdown files."""
        flows_dir = tmp_path / ".paircoder" / "flows"
        flows_dir.mkdir(parents=True)

        (flows_dir / "flow.md").write_text("""---
name: flow
description: Flow
---

Body.
""")
        (flows_dir / "notes.txt").write_text("Just a text file.")
        (flows_dir / "config.yaml").write_text("key: value")

        discovered = flows.discover_flows(tmp_path)

        assert len(discovered) == 1
        assert discovered[0].name == "flow"


class TestGetFlow:
    """Tests for get_flow function."""

    def test_get_existing_flow(self, tmp_path):
        """Get an existing flow by name."""
        flows_dir = tmp_path / ".paircoder" / "flows"
        flows_dir.mkdir(parents=True)

        (flows_dir / "my-flow.md").write_text("""---
name: my-flow
description: My flow
---

Body.
""")

        flow = flows.get_flow(tmp_path, "my-flow")

        assert flow is not None
        assert flow.name == "my-flow"

    def test_get_nonexistent_flow(self, tmp_path):
        """Return None for non-existent flow."""
        flow = flows.get_flow(tmp_path, "nonexistent")
        assert flow is None


class TestListFlowNames:
    """Tests for list_flow_names function."""

    def test_list_names(self, tmp_path):
        """List all flow names."""
        flows_dir = tmp_path / ".paircoder" / "flows"
        flows_dir.mkdir(parents=True)

        for name in ["alpha", "beta", "gamma"]:
            (flows_dir / f"{name}.md").write_text(f"""---
name: {name}
description: {name.title()}
---

Body.
""")

        names = flows.list_flow_names(tmp_path)

        assert names == ["alpha", "beta", "gamma"]

    def test_list_empty(self, tmp_path):
        """Return empty list when no flows."""
        names = flows.list_flow_names(tmp_path)
        assert names == []
