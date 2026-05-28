---
description: Secure file uploads — extension/content validation, safe filenames, storage, access control
alwaysApply: false
---

# File Upload Security

## NEVER
- Trust client-supplied `Content-Type` headers
- Use user-supplied filenames directly — always generate server-side names
- Allow double extensions (`.jpg.php`) or null byte injection (`.php%00.jpg`)
- Store uploaded files inside the webroot with execute permissions
- Mount `/var/run/docker.sock` — unrelated but commonly co-located mistake; store files outside webroot
- Allow ZIP uploads without safe extraction; avoid ZIP when possible due to attack vectors
- Use denylist approach for file extensions — use allowlist only
- Allow unauthenticated file uploads

## ALWAYS
- Validate extensions against an explicit allowlist after decoding the filename
- Validate file signatures (magic numbers) alongside MIME type — neither alone is sufficient
- Generate random UUIDs/GUIDs as stored filenames; if user filename needed, enforce max length and restrict to `[a-zA-Z0-9 ._-]`, no leading `.` or `-`
- Store files on a separate server or outside webroot with admin-only filesystem access
- If webroot storage unavoidable, set write-only permissions; serve via application handler mapping IDs to filenames
- Rewrite images to destroy embedded malicious content; use Apache POI for Office docs
- Require authentication and enforce least-privilege filesystem permissions
- Set upload size limits; apply post-decompression size limits for archives
- Protect upload endpoints with CSRF tokens
- Integrate antivirus / CDR scanning for applicable file types
- Log all upload activity; keep file processing libraries updated

## Validation Layers

| Layer | What to check |
|-------|--------------|
| Extension | Allowlist; decode filename first; no double ext or null bytes |
| MIME / magic bytes | Validate signature; never trust `Content-Type` header alone |
| Filename | UUID generated; max length; restricted charset |
| Content | Image rewrite; AV scan; CDR for Office/PDF |
| Size | Upload limit; decompressed size limit for archives |

## Checklist
- [ ] Extension allowlist enforced after filename decoding
- [ ] File signatures validated; `Content-Type` not trusted alone
- [ ] Server-generated UUID filenames used; no user-supplied names
- [ ] Files stored outside webroot or with write-only perms; served via ID-mapping handler
- [ ] Authentication required; least-privilege permissions applied
- [ ] CSRF protection on upload endpoint
- [ ] Size limits and AV/CDR scanning in place
