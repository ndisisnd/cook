---
description: Prevent SSRF by validating and restricting outbound requests — allowlist trusted destinations, block internal ranges
alwaysApply: false
---

# Server-Side Request Forgery Prevention

SSRF is not HTTP-only — attackers exploit `file://`, `gopher://`, `phar://`, `data://`, `dict://`, FTP, SMB, and SMTP too.

## NEVER
- Accept complete URLs from users — URLs are hard to validate and parsers can be exploited
- Perform DNS resolution with a public resolver when checking if a domain is internal
- Follow HTTP redirects in outbound clients used for user-supplied destinations
- Allow non-HTTP/HTTPS protocols for dynamic external requests

## ALWAYS
- Accept only validated IP addresses or domain names, not full URLs
- Use established libraries for IP and domain validation to prevent encoding bypasses
- Disable HTTP redirects in all outbound HTTP clients
- Restrict protocols to HTTP/HTTPS via allowlist
- Apply network-layer firewall rules restricting application outbound access
- Migrate cloud deployments to IMDSv2 (AWS) and disable IMDSv1

## Case 1 — Known Trusted Destinations (Allowlist)

1. Validate IP with: Java `InetAddressValidator`, .NET `IPAddress.TryParse`, JS `ip-address`, Ruby `IPAddr`
2. Validate domain with: Java `DomainValidator`, .NET `Uri.CheckHostName`, JS `is-valid-domain`, Python `validators.domain`
3. Compare output of validation library (not raw input) against explicit allowlist (IPv4 + IPv6)
4. Monitor allowlisted domains for DNS pinning — alert when they resolve to private/internal IPs
5. Use firewalls and network segmentation as second layer

## Case 2 — Dynamic External Destinations (Block-list)

1. Validate format using same libraries as Case 1
2. For IPs: verify address is public (not private, loopback, link-local)
3. For domains: resolve via internal DNS that only resolves internal names; verify all returned IPs are public
4. Restrict to HTTP/HTTPS only
5. Require a secure token proving legitimate request:
   - 20-character random alphanumeric token
   - Passed as POST parameter with name matching `[a-z]{1,10}`
   - Endpoint accepts HTTP POST only
6. Build outbound request exclusively from validated data — never from raw user input

## Checklist
- [ ] No raw URL acceptance from users; only IP or domain name input
- [ ] Validated libraries used for IP/domain format checks
- [ ] Outbound HTTP clients have redirects disabled
- [ ] Allowlist uses validation-library output, not raw input string
- [ ] Dynamic destinations checked against private/loopback IP ranges
- [ ] Protocols restricted to HTTP/HTTPS
- [ ] Network firewall limits application outbound destinations
- [ ] AWS deployments use IMDSv2; IMDSv1 disabled
- [ ] Allowlisted domains monitored for DNS pinning to internal IPs
