"""Tests for network allowlist guard.

This module tests the NetworkGuard class which restricts network access
to only allowed domains during containment mode.
"""

import pytest

from bpsai_pair.security.network import NetworkGuard, NetworkRestrictionError


class TestNetworkRestrictionError:
    """Tests for NetworkRestrictionError exception."""

    def test_is_exception(self):
        """NetworkRestrictionError is an Exception subclass."""
        assert issubclass(NetworkRestrictionError, Exception)

    def test_message(self):
        """Error includes the message passed to it."""
        error = NetworkRestrictionError("Test error message")
        assert str(error) == "Test error message"


class TestNetworkGuardInit:
    """Tests for NetworkGuard initialization."""

    def test_init_with_empty_list(self):
        """Can initialize with empty allowed domains list."""
        guard = NetworkGuard([])
        assert guard is not None

    def test_init_with_domains(self):
        """Can initialize with list of domains."""
        guard = NetworkGuard(["github.com", "api.trello.com"])
        assert guard is not None

    def test_allowed_domains_stored(self):
        """Allowed domains are stored internally."""
        guard = NetworkGuard(["github.com"])
        # Localhost variants should always be added
        assert "localhost" in guard.allowed
        assert "github.com" in guard.allowed


class TestNetworkGuardLocalhostAlwaysAllowed:
    """Tests that localhost is always allowed regardless of config."""

    def test_localhost_always_in_allowlist(self):
        """localhost is always in the allowlist."""
        guard = NetworkGuard([])
        assert "localhost" in guard.allowed

    def test_127_0_0_1_always_in_allowlist(self):
        """127.0.0.1 is always in the allowlist."""
        guard = NetworkGuard([])
        assert "127.0.0.1" in guard.allowed

    def test_ipv6_localhost_always_in_allowlist(self):
        """::1 (IPv6 localhost) is always in the allowlist."""
        guard = NetworkGuard([])
        assert "::1" in guard.allowed

    def test_localhost_url_passes(self):
        """URL to localhost passes check."""
        guard = NetworkGuard([])
        guard.check_url("http://localhost:8080/api")  # Should not raise

    def test_127_0_0_1_url_passes(self):
        """URL to 127.0.0.1 passes check."""
        guard = NetworkGuard([])
        guard.check_url("http://127.0.0.1:3000/")  # Should not raise

    def test_ipv6_localhost_url_passes(self):
        """URL to [::1] passes check."""
        guard = NetworkGuard([])
        guard.check_url("http://[::1]:8000/")  # Should not raise


class TestNetworkGuardAllowedDomains:
    """Tests for allowed domains passing through."""

    def test_exact_domain_allowed(self):
        """Exact domain in allowlist passes check."""
        guard = NetworkGuard(["github.com"])
        guard.check_url("https://github.com/user/repo")  # Should not raise

    def test_domain_with_port_allowed(self):
        """Domain with port passes check."""
        guard = NetworkGuard(["example.com"])
        guard.check_url("https://example.com:443/path")  # Should not raise

    def test_multiple_allowed_domains(self):
        """Multiple domains in allowlist all pass."""
        guard = NetworkGuard(["github.com", "api.trello.com", "pypi.org"])
        guard.check_url("https://github.com/")  # Should not raise
        guard.check_url("https://api.trello.com/1/boards")  # Should not raise
        guard.check_url("https://pypi.org/project/paircoder")  # Should not raise


class TestNetworkGuardSubdomainMatching:
    """Tests for subdomain matching."""

    def test_subdomain_of_allowed_domain_passes(self):
        """Subdomain of allowed domain passes check."""
        guard = NetworkGuard(["github.com"])
        guard.check_url("https://api.github.com/repos")  # Should not raise

    def test_nested_subdomain_passes(self):
        """Nested subdomain of allowed domain passes."""
        guard = NetworkGuard(["github.com"])
        # Multi-level subdomains should work
        guard.check_url("https://api.github.com/")  # Should not raise
        guard.check_url("https://raw.github.com/")  # Should not raise

    def test_different_domain_suffix_blocked(self):
        """Domain with similar suffix but different base is blocked."""
        guard = NetworkGuard(["github.com"])
        # githubusercontent.com is a different domain, not a subdomain of github.com
        with pytest.raises(NetworkRestrictionError):
            guard.check_url("https://raw.githubusercontent.com/")

    def test_deep_subdomain_passes(self):
        """Deep subdomain (multiple levels) passes."""
        guard = NetworkGuard(["example.com"])
        guard.check_url("https://api.v2.example.com/")  # Should not raise

    def test_similar_but_different_domain_blocked(self):
        """Domain that ends similarly but is different is blocked."""
        guard = NetworkGuard(["github.com"])
        with pytest.raises(NetworkRestrictionError):
            guard.check_url("https://fakegithub.com/malicious")


class TestNetworkGuardBlockedDomains:
    """Tests for blocked domains raising errors."""

    def test_unlisted_domain_blocked(self):
        """Domain not in allowlist raises error."""
        guard = NetworkGuard(["github.com"])
        with pytest.raises(NetworkRestrictionError) as exc_info:
            guard.check_url("https://evil.com/phishing")
        assert "evil.com" in str(exc_info.value)
        assert "blocked" in str(exc_info.value).lower()

    def test_blocked_error_includes_domain(self):
        """Error message includes the blocked domain."""
        guard = NetworkGuard(["github.com"])
        with pytest.raises(NetworkRestrictionError) as exc_info:
            guard.check_url("https://malicious-site.org/attack")
        assert "malicious-site.org" in str(exc_info.value)

    def test_blocked_error_includes_allowed_list(self):
        """Error message includes allowed domains for reference."""
        guard = NetworkGuard(["github.com", "api.trello.com"])
        with pytest.raises(NetworkRestrictionError) as exc_info:
            guard.check_url("https://blocked.com/")
        error_msg = str(exc_info.value)
        assert "github.com" in error_msg or "Allowed domains" in error_msg


class TestNetworkGuardURLParsing:
    """Tests for URL parsing edge cases."""

    def test_http_url(self):
        """HTTP URLs are parsed correctly."""
        guard = NetworkGuard(["example.com"])
        guard.check_url("http://example.com/page")  # Should not raise

    def test_https_url(self):
        """HTTPS URLs are parsed correctly."""
        guard = NetworkGuard(["example.com"])
        guard.check_url("https://example.com/page")  # Should not raise

    def test_url_with_path(self):
        """URL with complex path is parsed correctly."""
        guard = NetworkGuard(["api.github.com"])
        guard.check_url("https://api.github.com/repos/user/project/issues")

    def test_url_with_query_params(self):
        """URL with query parameters is parsed correctly."""
        guard = NetworkGuard(["example.com"])
        guard.check_url("https://example.com/search?q=test&page=1")

    def test_url_with_fragment(self):
        """URL with fragment is parsed correctly."""
        guard = NetworkGuard(["docs.python.org"])
        guard.check_url("https://docs.python.org/3/library/#index")

    def test_url_with_auth(self):
        """URL with authentication info is parsed correctly."""
        guard = NetworkGuard(["api.example.com"])
        guard.check_url("https://user:pass@api.example.com/endpoint")

    def test_url_with_port(self):
        """Port is correctly stripped when checking domain."""
        guard = NetworkGuard(["example.com"])
        guard.check_url("https://example.com:8443/api")  # Should not raise


class TestNetworkGuardIPAddressHandling:
    """Tests for IP address handling."""

    def test_ipv4_address_not_in_allowlist(self):
        """IPv4 address not in allowlist is blocked."""
        guard = NetworkGuard(["github.com"])
        with pytest.raises(NetworkRestrictionError):
            guard.check_url("http://192.168.1.1/admin")

    def test_ipv4_address_in_allowlist(self):
        """IPv4 address explicitly in allowlist passes."""
        guard = NetworkGuard(["10.0.0.1"])
        guard.check_url("http://10.0.0.1:8080/")  # Should not raise

    def test_ipv6_address_blocked(self):
        """IPv6 address not in allowlist is blocked."""
        guard = NetworkGuard(["github.com"])
        with pytest.raises(NetworkRestrictionError):
            guard.check_url("http://[2001:db8::1]/path")

    def test_ipv6_address_in_allowlist(self):
        """IPv6 address explicitly in allowlist passes."""
        guard = NetworkGuard(["2001:db8::1"])
        guard.check_url("http://[2001:db8::1]:8080/")  # Should not raise


class TestNetworkGuardIsAllowed:
    """Tests for _is_allowed internal method."""

    def test_direct_match(self):
        """Direct domain match returns True."""
        guard = NetworkGuard(["github.com"])
        assert guard._is_allowed("github.com") is True

    def test_subdomain_match(self):
        """Subdomain match returns True."""
        guard = NetworkGuard(["github.com"])
        assert guard._is_allowed("api.github.com") is True

    def test_no_match(self):
        """Non-matching domain returns False."""
        guard = NetworkGuard(["github.com"])
        assert guard._is_allowed("evil.com") is False

    def test_partial_match_rejected(self):
        """Partial domain match (suffix) is rejected."""
        guard = NetworkGuard(["github.com"])
        assert guard._is_allowed("notgithub.com") is False


class TestNetworkGuardEdgeCases:
    """Tests for edge cases and security considerations."""

    def test_empty_url_raises(self):
        """Empty URL should be handled gracefully."""
        guard = NetworkGuard(["github.com"])
        with pytest.raises((NetworkRestrictionError, ValueError)):
            guard.check_url("")

    def test_malformed_url_raises(self):
        """Malformed URL should be handled."""
        guard = NetworkGuard(["github.com"])
        with pytest.raises((NetworkRestrictionError, ValueError)):
            guard.check_url("not-a-valid-url")

    def test_case_insensitive_domain(self):
        """Domain matching should be case-insensitive."""
        guard = NetworkGuard(["GitHub.com"])
        guard.check_url("https://github.com/")  # Should not raise
        guard.check_url("https://GITHUB.COM/")  # Should not raise

    def test_trailing_dot_domain(self):
        """Domain with trailing dot (FQDN) should work."""
        guard = NetworkGuard(["github.com"])
        # Trailing dot indicates FQDN
        guard.check_url("https://github.com./")  # Should not raise

    def test_unicode_domain(self):
        """Unicode/IDN domains should be handled."""
        guard = NetworkGuard(["münchen.de"])
        guard.check_url("https://münchen.de/")  # Should not raise
