"""
IdeaGPT AI Gateway — Server-Side Request Forgery (SSRF) Protection.
Enforces deterministic validation of all outbound URL fetches:
  1. Scheme allowlist (HTTP/HTTPS only)
  2. Hostname validation (reject localhost, link-local, cloud metadata)
  3. Pre-flight DNS resolution (IPv4 & IPv6)
  4. IP address range blocking (RFC 1918, RFC 3927, RFC 4193, RFC 4291, loopback, multicast)
  5. Redirect chain validation
"""

import ipaddress
import socket
import logging
from urllib.parse import urlparse, urljoin
from typing import Optional, Set, Tuple, List
import httpx

logger = logging.getLogger(__name__)

# Blocked IP Networks
BLOCKED_IP_NETWORKS = [
    # IPv4 Private / Loopback / Link-Local / Multicast / Reserved
    ipaddress.ip_network("0.0.0.0/8"),          # Current network
    ipaddress.ip_network("10.0.0.0/8"),          # RFC 1918 Private
    ipaddress.ip_network("100.64.0.0/10"),       # Carrier-grade NAT
    ipaddress.ip_network("127.0.0.0/8"),        # Loopback
    ipaddress.ip_network("169.254.0.0/16"),     # Link-local / Cloud Metadata (AWS, Azure, GCP, DO)
    ipaddress.ip_network("172.16.0.0/12"),      # RFC 1918 Private
    ipaddress.ip_network("192.0.0.0/24"),       # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),       # TEST-NET-1
    ipaddress.ip_network("192.88.99.0/24"),     # 6to4 Relay Anycast
    ipaddress.ip_network("192.168.0.0/16"),     # RFC 1918 Private
    ipaddress.ip_network("198.18.0.0/15"),      # Network benchmark tests
    ipaddress.ip_network("198.51.100.0/24"),    # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),     # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),        # Multicast
    ipaddress.ip_network("240.0.0.0/4"),        # Reserved
    ipaddress.ip_network("255.255.255.255/32"), # Broadcast
    # IPv6 Loopback / Private / Link-Local / Unique Local
    ipaddress.ip_network("::1/128"),            # Loopback
    ipaddress.ip_network("::/128"),             # Unspecified
    ipaddress.ip_network("::ffff:0:0/96"),      # IPv4-mapped IPv6
    ipaddress.ip_network("100::/64"),           # Discard prefix
    ipaddress.ip_network("2001:db8::/32"),      # Documentation
    ipaddress.ip_network("fc00::/7"),           # Unique Local Address (ULA)
    ipaddress.ip_network("fe80::/10"),          # Link-Local Unicast
    ipaddress.ip_network("ff00::/8"),           # Multicast
]

BLOCKED_HOSTNAMES: Set[str] = {
    "localhost",
    "localhost.localdomain",
    "local",
    "internal",
    "metadata",
    "metadata.google.internal",
    "instance-data",
    "instance-data.ec2.internal",
    "169.254.169.254",
    "100.100.100.200",
    "kubernetes.default",
    "docker",
}


class SSRFSecurityException(Exception):
    """Raised when a URL violates SSRF security boundaries."""
    pass


class SSRFGuard:
    ALLOWED_SCHEMES: Set[str] = {"http", "https"}
    MAX_REDIRECT_HOPS: int = 3
    DEFAULT_TIMEOUT_SEC: float = 10.0
    MAX_CONTENT_BYTES: int = 5 * 1024 * 1024  # 5 MB max

    @classmethod
    def is_ip_blocked(cls, ip_obj: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
        """Checks whether an IP address falls within any prohibited network range."""
        # Handle NAT64 translation (64:ff9b::/96) by validating the embedded IPv4 address
        if ip_obj.version == 6 and ip_obj in ipaddress.ip_network("64:ff9b::/96"):
            embedded_ipv4_int = int(ip_obj) & 0xFFFFFFFF
            embedded_ipv4 = ipaddress.IPv4Address(embedded_ipv4_int)
            return cls.is_ip_blocked(embedded_ipv4)

        for network in BLOCKED_IP_NETWORKS:
            if ip_obj in network:
                return True
        return False

    @classmethod
    def validate_url(cls, url: str) -> Tuple[str, List[str]]:
        """
        Validates URL scheme, syntax, and resolves DNS to verify target IP safety.
        Returns the parsed hostname and list of resolved IP addresses.
        Raises SSRFSecurityException if any check fails.
        """
        if not url or not isinstance(url, str):
            raise SSRFSecurityException("Invalid URL: URL string is empty or missing.")

        url_clean = url.strip()
        try:
            parsed = urlparse(url_clean)
        except Exception as exc:
            raise SSRFSecurityException(f"Malformed URL structure: {exc}")

        # 1. Scheme Validation
        if parsed.scheme.lower() not in cls.ALLOWED_SCHEMES:
            raise SSRFSecurityException(
                f"Prohibited URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are allowed."
            )

        # 2. Hostname Validation
        hostname = parsed.hostname
        if not hostname:
            raise SSRFSecurityException("Invalid URL: Missing hostname.")

        hostname_lower = hostname.lower()
        if hostname_lower in BLOCKED_HOSTNAMES:
            raise SSRFSecurityException(f"Access to prohibited hostname '{hostname}' is blocked.")

        if any(hostname_lower.endswith(f".{b}") for b in ["local", "internal", "localhost", "lan"]):
            raise SSRFSecurityException(f"Access to internal domain '{hostname}' is blocked.")

        # 3. Direct IP Address Check
        try:
            ip_obj = ipaddress.ip_address(hostname_lower)
            if cls.is_ip_blocked(ip_obj):
                raise SSRFSecurityException(
                    f"Direct access to prohibited IP address '{ip_obj}' is blocked."
                )
            return hostname_lower, [str(ip_obj)]
        except ValueError:
            pass

        # 4. Pre-Flight DNS Resolution
        resolved_ips: List[str] = []
        try:
            addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            for item in addr_info:
                sockaddr = item[4]
                ip_str = sockaddr[0]
                ip_obj = ipaddress.ip_address(ip_str)
                if cls.is_ip_blocked(ip_obj):
                    raise SSRFSecurityException(
                        f"Domain '{hostname}' resolves to prohibited IP address '{ip_str}'."
                    )
                resolved_ips.append(ip_str)
        except socket.gaierror as err:
            raise SSRFSecurityException(f"Failed to resolve DNS for hostname '{hostname}': {err}")

        if not resolved_ips:
            raise SSRFSecurityException(f"No IP addresses resolved for hostname '{hostname}'.")

        return hostname_lower, resolved_ips

    @classmethod
    async def safe_fetch(
        cls,
        url: str,
        timeout: float = DEFAULT_TIMEOUT_SEC,
        headers: Optional[dict] = None
    ) -> Tuple[int, bytes, str]:
        """
        Executes a safe outbound HTTP GET request with SSRF validation,
        redirect tracking, size bounding, and timeout enforcement.
        """
        current_url = url
        hops = 0

        async with httpx.AsyncClient(
            follow_redirects=False,
            timeout=timeout,
            headers=headers or {"User-Agent": "IdeaGPT-SafeCrawler/1.0"}
        ) as client:
            while hops <= cls.MAX_REDIRECT_HOPS:
                cls.validate_url(current_url)

                try:
                    response = await client.get(current_url)
                except httpx.TimeoutException:
                    raise SSRFSecurityException(f"Outbound request to '{current_url}' timed out.")
                except Exception as exc:
                    raise SSRFSecurityException(f"Outbound request connection error: {exc}")

                if response.status_code in (301, 302, 303, 307, 308):
                    redirect_location = response.headers.get("Location")
                    if not redirect_location:
                        break
                    current_url = urljoin(current_url, redirect_location)
                    hops += 1
                    continue

                content = response.content
                if len(content) > cls.MAX_CONTENT_BYTES:
                    raise SSRFSecurityException(
                        f"Response size exceeded safety limit ({len(content)} > {cls.MAX_CONTENT_BYTES} bytes)."
                    )

                content_type = response.headers.get("content-type", "application/octet-stream")
                return response.status_code, content, content_type

            raise SSRFSecurityException(
                f"Exceeded maximum allowed redirect hops ({cls.MAX_REDIRECT_HOPS})."
            )
