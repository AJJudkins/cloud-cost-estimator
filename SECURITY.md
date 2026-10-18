# Security policy

## Scope and safety
offline and read-only: it only reads the resource and price files you give it, makes no API calls and needs no cloud credentials.

## What was and was not tested
**Tested (automated, in CI and locally):** cost math, input validation and CLI errors on the bundled example prices.

**Not tested:** accuracy against any real cloud bill or price list (prices are examples, not quotes), other pricing models (spot, reserved, tiers), and non-Linux platforms.

## Reporting a problem
This is a small personal portfolio project, not a supported product. If you find a security issue, please open a GitHub issue **without** secrets, credentials or real system details, or use GitHub's "Report a vulnerability" button on the Security tab if it is enabled.
