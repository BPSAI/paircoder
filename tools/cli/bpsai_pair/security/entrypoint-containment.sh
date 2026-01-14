#!/bin/bash
# PairCoder Containment Entrypoint
#
# Sets up network allowlist via iptables if PAIRCODER_NETWORK_ALLOWLIST is set,
# then executes the provided command.
#
# Environment Variables:
#   PAIRCODER_NETWORK_ALLOWLIST: Space-separated list of allowed domains
#   PAIRCODER_CONTAINMENT_MODE: "strict" to enable network enforcement
#
# Example:
#   PAIRCODER_NETWORK_ALLOWLIST="api.anthropic.com github.com"

set -e

setup_network_allowlist() {
    local allowlist="$1"

    echo "[containment] Setting up network allowlist..."

    # Allow localhost traffic
    iptables -A OUTPUT -d 127.0.0.0/8 -j ACCEPT 2>/dev/null || true
    iptables -A OUTPUT -o lo -j ACCEPT 2>/dev/null || true

    # Allow DNS for domain resolution
    iptables -A OUTPUT -p udp --dport 53 -j ACCEPT 2>/dev/null || true
    iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT 2>/dev/null || true

    # Allow established connections (responses to our requests)
    iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true

    # Resolve and allow each domain
    for domain in $allowlist; do
        echo "[containment] Allowing domain: $domain"

        # Use dig to resolve domain to IPs
        local ips=$(dig +short "$domain" 2>/dev/null | grep -E '^[0-9]+\.' || true)

        if [ -z "$ips" ]; then
            echo "[containment] Warning: Could not resolve $domain, skipping"
            continue
        fi

        for ip in $ips; do
            echo "[containment]   -> $ip"
            iptables -A OUTPUT -d "$ip" -j ACCEPT 2>/dev/null || true
        done
    done

    # Block all other outbound traffic
    iptables -A OUTPUT -j REJECT 2>/dev/null || true

    echo "[containment] Network allowlist configured"
}

# Check if we should set up network restrictions
if [ -n "$PAIRCODER_NETWORK_ALLOWLIST" ] && [ "$PAIRCODER_CONTAINMENT_MODE" = "strict" ]; then
    # Check if we have iptables capability
    if iptables -L -n >/dev/null 2>&1; then
        setup_network_allowlist "$PAIRCODER_NETWORK_ALLOWLIST"
    else
        echo "[containment] Warning: Cannot configure iptables (need NET_ADMIN capability)"
        echo "[containment] Network allowlist will NOT be enforced"
    fi
fi

# Execute the main command
exec "$@"
