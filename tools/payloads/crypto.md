# Encoding / crypto first moves

1. Base64 decode (repeat until stable)
2. Hex decode
3. URL decode
4. ROT13 / Caesar all shifts
5. Single-byte XOR brute
6. If `n,e,c` → factor small n / Wiener / small e

```bash
python3 - <<'PY'
import base64,binascii,codecs
s=b'PASTE'
for _ in range(5):
    try:
        s=base64.b64decode(s); print('b64',s[:80])
    except Exception: break
PY
```
