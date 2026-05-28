---
description: Secure file handling and uploads — validation, storage isolation, scanning, safe delivery
alwaysApply: false
---

# File Handling & Uploads

## NEVER
- Trust the client-supplied Content-Type — it can be spoofed
- Validate filename or extension before decoding/canonicalization (defeats `.php%00.jpg` style bypass)
- Allow double extensions (`.jpg.php`) or extensions outside an explicit allow-list
- Use the user-supplied filename as the storage filename
- Store uploaded files in webroot with execute permission
- Accept ZIP/archive content without post-decompression size checks (zip bombs)
- Skip authentication on upload endpoints

## ALWAYS
- Allow-list extensions, never deny-list — list only what the business needs
- Validate file signature (magic number) in addition to MIME — both must match the expected type
- Generate server-side filenames (UUID/GUID); discard user filename for storage
- Enforce a maximum filename length; restrict characters to `[A-Za-z0-9 .-]`; reject leading `.` or `-`
- Apply size limits at the request layer; enforce post-decompression limits on archives
- Require authenticated session before accepting an upload; protect against CSRF
- Run AV/CDR scanning before file is made retrievable

## Storage isolation
- Store uploads outside webroot, on a separate server/bucket when possible
- If stored in webroot: write-only permissions; deliver via an application handler that maps opaque IDs → file paths
- Set filesystem permissions to the principle of least privilege
- Scan before granting execute permission (if execute is ever required, which it usually isn't)

## Content-specific handling
- Images: rewrite via an image library (re-encode) to destroy embedded payloads
- Office documents: validate with Apache POI or equivalent
- Compressed archives: use safe size-calculating extractors; cap decompression ratio
- Avoid accepting ZIP where alternatives exist — wide attack surface

## Monitoring
- Log upload activity (user, size, type, scan result)
- Provide a user-reporting mechanism for illegal/abusive content
- Keep file-processing libraries up to date

## Checklist
- [ ] Extension allow-list applied after canonicalization
- [ ] MIME + magic-number validation both pass
- [ ] Server-generated filenames; no traversal characters accepted
- [ ] Stored outside webroot or behind a handler; correct permissions
- [ ] Size + decompression limits enforced
- [ ] Authentication, authorization, and CSRF protection on upload endpoints
- [ ] AV/CDR scanning runs before file becomes retrievable
- [ ] Upload activity logged
