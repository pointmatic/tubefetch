# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.8.x   | :white_check_mark: |
| < 0.8.0 | :x:                |

## Reporting a Vulnerability

We take the security of yt-fetch seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please Do Not

- Open a public GitHub issue for security vulnerabilities
- Disclose the vulnerability publicly before it has been addressed

### Please Do

**Report security vulnerabilities by emailing:** security@pointmatic.com

Please include the following information in your report:

- Type of vulnerability (e.g., remote code execution, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability, including how an attacker might exploit it

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Communication**: We will keep you informed about our progress in addressing the vulnerability
- **Timeline**: We aim to release a fix within 30 days for critical vulnerabilities
- **Credit**: We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Update Process

1. Security vulnerability is reported privately
2. Vulnerability is confirmed and assessed
3. Fix is developed and tested
4. Security advisory is drafted
5. Fix is released in a new version
6. Security advisory is published
7. Users are notified via GitHub Security Advisories

## Security Best Practices

When using yt-fetch:

- **Keep dependencies updated**: Regularly update yt-fetch and its dependencies
- **Validate inputs**: Always validate and sanitize video IDs and URLs from untrusted sources
- **API keys**: Store YouTube API keys securely (environment variables, not in code)
- **Rate limiting**: Use built-in rate limiting to avoid service abuse
- **Network security**: Be aware that yt-fetch makes external network requests to YouTube

## Known Security Considerations

### External Dependencies

yt-fetch relies on external services and libraries:
- `yt-dlp`: Video metadata extraction
- `youtube-transcript-api`: Transcript fetching
- Network requests to YouTube servers

Users should be aware that:
- Video IDs and URLs are sent to YouTube servers
- Downloaded content comes from external sources
- Malicious video metadata could potentially cause issues

### Input Validation

yt-fetch validates video IDs and URLs, but users should:
- Sanitize inputs from untrusted sources
- Be cautious with user-provided video IDs
- Validate downloaded content before use

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find similar problems
3. Prepare fixes for all supported versions
4. Release new versions as soon as possible

We appreciate your efforts to responsibly disclose your findings and will make every effort to acknowledge your contributions.

## Contact

For security issues: security@pointmatic.com  
For general issues: https://github.com/pointmatic/tubefetch/issues

Thank you for helping keep yt-fetch and its users safe!
