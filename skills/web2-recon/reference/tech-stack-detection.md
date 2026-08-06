## KNOWN VULNERABILITY CORRELATION (Always Perform)

After identifying the technology stack, immediately determine whether any
publicly known vulnerabilities may apply before beginning manual testing.

Known vulnerability correlation is an acceleration step that complements
manual testing. Never replace manual testing with CVE correlation alone.

---

## Correlation Workflow

1. Fingerprint the exact:

   - Product
   - Framework
   - Service
   - Library
   - Component
   - Plugin / Extension
   - Version

2. Validate the fingerprint using multiple independent indicators whenever
   possible.

   Examples include:

   - Response headers
   - Static assets
   - HTML metadata
   - JavaScript bundles
   - API responses
   - Error messages
   - Public metadata
   - Default files
   - Behavioral characteristics

3. Assign a confidence level to the fingerprint.

   - High → Version confidently identified.
   - Medium → Multiple likely versions remain.
   - Low → Product identified but version uncertain.

4. If multiple version candidates exist, retain all candidates until further
   evidence reduces uncertainty.

5. Use the validated fingerprint with the available CVE correlation workflow
   or tooling (e.g., `cve-fingerprint`) to correlate the identified technology
   against the latest verified public vulnerability sources.

6. Prioritize vulnerabilities that are:

   - Critical (CVSS ≥ 9.0)
   - High (CVSS ≥ 7.0)
   - Internet-exploitable
   - Unauthenticated
   - Public PoC available
   - Known to be actively exploited (when verified)
   - Applicable to the validated version

7. Never assume a vulnerability is applicable from:

   - Server banners
   - Headers
   - Product names
   - Version guesses

8. Confirm the affected version before attempting any verification.

9. If a matching vulnerability is identified:

   - Verify using safe, non-destructive techniques.
   - Confirm exploitability.
   - Assess real-world impact.
   - Collect sufficient evidence.
   - Minimize requests whenever possible.
   - Avoid unnecessary or unsafe exploitation.

10. If no matching public vulnerability exists, continue comprehensive manual
    testing without reducing coverage.

---

## Priority Components

Always correlate known vulnerabilities for:

- Operating systems
- Web servers
- Reverse proxies
- Load balancers
- Application servers
- Frameworks
- CMS platforms
- Authentication providers
- Identity & SSO services
- API gateways
- GraphQL engines
- Database middleware
- Database management systems
- Caching services
- Message queues
- Search engines
- Object storage services
- Container runtimes
- Container platforms
- Kubernetes components
- Service meshes
- CI/CD platforms
- Monitoring dashboards
- Administrative panels
- Developer portals
- Third-party plugins
- Browser extensions
- JavaScript packages
- Node.js modules
- Python packages
- PHP Composer packages
- Ruby gems
- Go modules
- Java libraries
- .NET packages

---

## Prioritization Order

1. Remote Code Execution (RCE)
2. Authentication Bypass
3. Privilege Escalation
4. SQL Injection
5. NoSQL Injection
6. Command Injection
7. Server-Side Request Forgery (SSRF)
8. XML External Entity (XXE)
9. Server-Side Template Injection (SSTI)
10. Insecure Deserialization
11. Path Traversal
12. Arbitrary File Read
13. Arbitrary File Write
14. Local File Inclusion (LFI)
15. Remote File Inclusion (RFI)
16. Information Disclosure
17. Security Misconfiguration
18. Default Credentials
19. Sensitive Debug Interfaces
20. Denial of Service (when relevant)

---

## Decision Rules

- Fingerprint before correlating.
- Validate before correlating.
- Correlate as soon as sufficient fingerprint confidence is achieved.
- Verify before reporting.
- Never rely on a single fingerprinting indicator.
- Never report a vulnerability solely because a CVE exists.
- Never assume version information is accurate until validated.
- Never skip manual testing because no matching CVE was found.
- Treat public vulnerabilities as guidance, not proof of exploitability.
- Always collect sufficient evidence before reporting findings.

---

## References

- Fingerprinting workflow:
  `cve-fingerprint/SKILL.md`

- Verification methodology:
  `security-arsenal/reference/cve-pocs.md`
