# Linux Systems Triage & Auto-Remediation Toolkit

A modular systems reliability toolkit engineered in Python 3 and POSIX Bash for Linux kernel diagnostics, process triage, network latency probing, and automated batch recovery.

## Architecture & Tooling Matrix

| Component | Technology | Primary Functionality |
| :--- | :--- | :--- |
| **System Triage CLI** | Python 3 (`argparse`, `subprocess`) | Parses `/proc` filesystem telemetry to surface CPU load, memory thresholds, and kernel process execution states (`R`, `S`, `D`, `Z`). |
| **Synthetic Network Probes** | Python 3 (`socket`, `ssl`) | Synthetic checks for TLS 1.3 handshakes, TCP connection states, and CoreDNS latency with exponential backoff and jitter. |
| **Atomic Automation Runbooks** | POSIX Bash (`flock`, `trap`) | Idempotent system maintenance runbooks utilizing atomic file locking and POSIX signal traps for safe lifecycle teardown. |

## Author
**Sanjaya Kumar Swain** — [github.com/Sanjaya03](https://github.com/Sanjaya03)
