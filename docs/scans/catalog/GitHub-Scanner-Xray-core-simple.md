# XTLS/Xray-core — Simple Report

**Verdict: ✗ Critical.** Don't install this — material risks identified.

Xray-core — 37k-star Go network proxy + anti-censorship tool (v2ray-core fork; VMess, VLESS, Shadowsocks, Trojan, WireGuard, REALITY). Critical verdict driven by C20: no branch protection, no rulesets, no CODEOWNERS, 2.3% formal PR review on a privileged tool whose blast radius is every user's traffic. Mitigations exist — .dgst per release, Dependabot on gomod, OSSF-indexed 5.1/10. Verify .dgst out-of-band, pin a reviewed tag.

**Scanned:** 2026-04-20 · main @ b465036 · 37,309 stars · MPL-2.0 · Go

---

## Trust scorecard

- ✗ **Does anyone check the code?** No — 2.3% formal review, no branch protection, no CODEOWNERS on a privileged tool
- ⚠ **Do they fix problems quickly?** Partly — 0 open security issues + 100 releases (3 days old), but a 77-day-old hardening PR sits unmerged
- ⚠ **Do they tell you about problems?** Partly — SECURITY.md with private channel, but 0 published advisories in 5.5 years
- ⚠ **Is it safe out of the box?** Partly — .dgst checksums (MD5+SHA1+SHA256+SHA512) on every release, but no GPG / Sigstore / SLSA

## Top concerns

1. **[Critical] Governance single-point-of-failure on a privileged 37k-star network-proxy tool (C20)** The supply-chain blast radius for Xray-core is large.

2. **[Warning] 2.3% formal PR review + 7.7% any-review over 300-PR sample** External contributors who submit even security-flavored PRs should expect long review lags.

3. **[Warning] Zero published GHSA advisories across 5.5 years despite heightened threat model** There is no reliable machine-readable signal to a consumer that 'a security-relevant fix shipped in release X'.

## What should I do?

**Don't install this.** Verify the release .dgst checksum yourself from an independent terminal before trusting any binary.

---

*stop-git-std · scanned 2026-04-20 · [XTLS/Xray-core](https://github.com/XTLS/Xray-core)*
