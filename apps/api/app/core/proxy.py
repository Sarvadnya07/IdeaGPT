"""
IdeaGPT API — Trusted Proxy & Client Identity Module

Implements secure client IP resolution behind reverse proxies:
- Configurable trusted proxy topology via `settings.FORWARDED_ALLOW_IPS`.
- Rejects header spoofing from untrusted direct peers (X-Forwarded-For/X-Real-IP are ignored).
- Right-to-left traversal of the proxy chain (RFC 7239 compliant) when the direct peer is a trusted proxy.
- Strict IP syntax validation via Python's standard `ipaddress` library.
- Fails closed to the direct socket address if headers are malformed or missing.
"""

import ipaddress
import logging
from typing import List, Union, Optional
from starlette.requests import Request

from app.core.config import settings

logger = logging.getLogger("ideagpt.proxy")

IPNetwork = Union[ipaddress.IPv4Network, ipaddress.IPv6Network]
IPAddress = Union[ipaddress.IPv4Address, ipaddress.IPv6Address]


def _parse_trusted_networks(raw_config: str) -> List[IPNetwork]:
    """
    Parses a comma-separated list of IP addresses or CIDR networks into ipaddress Network objects.
    Invalid entries are logged and safely omitted.
    """
    networks: List[IPNetwork] = []
    if not raw_config:
        return networks

    for item in raw_config.split(","):
        entry = item.strip()
        if not entry or entry == "*":
            continue
        try:
            # ip_network with strict=False accepts both host addresses ('127.0.0.1' -> /32) and subnets ('10.0.0.0/8')
            net = ipaddress.ip_network(entry, strict=False)
            networks.append(net)
        except ValueError:
            logger.warning("Invalid trusted proxy network configuration entry: '%s'", entry)

    return networks


def is_trusted_proxy(ip_str: str, trusted_networks: Optional[List[IPNetwork]] = None) -> bool:
    """
    Checks if a given IP address belongs to any configured trusted proxy network.
    """
    if not ip_str:
        return False

    if trusted_networks is None:
        trusted_networks = _parse_trusted_networks(settings.FORWARDED_ALLOW_IPS)

    try:
        ip = ipaddress.ip_address(ip_str.strip())
        return any(ip in net for net in trusted_networks)
    except ValueError:
        return False


def get_client_ip(request: Request) -> str:
    """
    Resolves the true client IP address for the given request.

    Algorithm:
    1. Determine direct socket peer IP (`request.client.host`). Fallback to "127.0.0.1" if None.
    2. Check whether direct peer is a configured trusted proxy.
       - If direct peer is NOT trusted: Return direct peer IP immediately.
         Any client-supplied `X-Forwarded-For` or `X-Real-IP` headers are untrusted and IGNORED.
       - If direct peer IS trusted:
         a. Parse `X-Forwarded-For` (comma-separated list: "client, proxy1, proxy2").
            Traverse hops from right to left (upstream to downstream).
            The first untrusted IP encountered is the originating client IP.
         b. If no untrusted hop is found or header missing, check `X-Real-IP`.
         c. If valid IP found, return it.
         d. Otherwise, fallback to the direct peer IP.
    """
    direct_ip = "127.0.0.1"
    if request.client and request.client.host:
        direct_ip = request.client.host.strip()

    trusted_nets = _parse_trusted_networks(settings.FORWARDED_ALLOW_IPS)

    # If the direct peer is not in our trusted proxy topology, reject forwarded headers
    if not is_trusted_proxy(direct_ip, trusted_nets):
        return direct_ip

    # Direct peer is a verified trusted proxy: inspect forwarding headers
    xff = request.headers.get("x-forwarded-for")
    if xff:
        hops = [h.strip() for h in xff.split(",") if h.strip()]
        # Traverse right-to-left (from proxy nearest to us backwards to caller)
        for hop in reversed(hops):
            try:
                parsed_hop = ipaddress.ip_address(hop)
                # The first IP that is NOT a trusted proxy is the real client
                if not any(parsed_hop in net for net in trusted_nets):
                    return str(parsed_hop)
            except ValueError:
                # Malformed IP entry — ignore this hop
                continue

        # If all hops in XFF were trusted, the earliest hop (leftmost) is the client
        if hops:
            try:
                leftmost = ipaddress.ip_address(hops[0])
                return str(leftmost)
            except ValueError:
                pass

    # Fallback to X-Real-IP if present
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        try:
            parsed_real = ipaddress.ip_address(x_real_ip.strip())
            return str(parsed_real)
        except ValueError:
            pass

    return direct_ip
