---
description: PHP secure configuration — php.ini hardening for production to prevent information disclosure and RCE
alwaysApply: false
---

# PHP Secure Configuration

## NEVER
- Display errors in production (`display_errors = On`, `display_startup_errors = On`)
- Enable `allow_url_fopen` or `allow_url_include` (enables RFI escalation)
- Leave dangerous functions enabled if not used by the application
- Use a PHP version that no longer receives security updates

## ALWAYS
- Set `expose_php = Off`
- Log all errors (`log_errors = On`, `error_reporting = E_ALL`) to a protected log path
- Restrict filesystem access with `open_basedir` to the document root
- Disable functions not used by the application (`disable_functions`)
- Use strict session settings: `use_strict_mode`, `use_only_cookies`, `cookie_secure`, `cookie_httponly`, `cookie_samesite = Strict`
- Rename the session cookie (`session.name`)
- Set resource limits (`memory_limit`, `post_max_size`, `max_execution_time`)
- Consider Snuffleupagus for additional runtime hardening

## Error Handling
```ini
expose_php             = Off
error_reporting        = E_ALL
display_errors         = Off
display_startup_errors = Off
log_errors             = On
error_log              = /valid_path/PHP-logs/php_error.log
```

## Critical Settings

| Setting | Secure value |
|---------|-------------|
| `allow_url_fopen` | Off |
| `allow_url_include` | Off |
| `session.use_only_cookies` | 1 |
| `session.cookie_secure` | 1 |
| `session.cookie_httponly` | 1 |
| `session.cookie_samesite` | Strict |
| `session.use_strict_mode` | 1 |
| `session.sid_length` | 256 |
| `session.cookie_lifetime` | 14400 |
| `zend.exception_ignore_args` | On |
| `html_errors` | Off |

## Dangerous functions to disable (if unused)
`system, exec, shell_exec, passthru, phpinfo, show_source, highlight_file, popen, proc_open, putenv, chdir, mkdir, rmdir, chmod, rename`

## File Uploads
- Set `upload_tmp_dir` to a dedicated, non-public path
- Set `upload_max_filesize = 2M`, `max_file_uploads = 2`
- If uploads not needed: `file_uploads = Off`

## Checklist
- [ ] PHP version actively supported and receiving security patches
- [ ] `expose_php = Off`; errors logged, not displayed
- [ ] `allow_url_fopen` and `allow_url_include` disabled
- [ ] `open_basedir` restricted to document root
- [ ] Unused dangerous functions listed in `disable_functions`
- [ ] Session cookie flags: `secure`, `httponly`, `samesite=Strict`, `use_only_cookies`
- [ ] Resource limits (`memory_limit`, `max_execution_time`) set
