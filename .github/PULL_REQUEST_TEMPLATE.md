## Summary

<!-- What changed, and why a CTF operator or contributor should care. -->

## Test plan

- [ ] `python3 -m unittest discover -s tests -v`
- [ ] `bash -n scripts/*.sh`
- [ ] `bash scripts/solve.sh doctor`
- [ ] Scanners were only pointed at a local fixture or an authorized lab

## Security

- [ ] No secrets, `.env` files, or real flags added
- [ ] Active scans stay limited to systems the operator is allowed to test
