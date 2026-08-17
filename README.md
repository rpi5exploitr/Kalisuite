# KaliSuite

**KaliSuite** is a Python + PyQt6 graphical user interface that wraps a collection of popular security tools found in Kali Linux (e.g., `nmap`, `arp-scan`, `hydra`, `sqlmap`, `gobuster`, `tcpdump`, `aircrack-ng`, etc.).  
The UI provides convenient forms, live output streaming, and basic result parsing, allowing you to run the tools without typing commands manually.

> **⚠️ Legal notice**  
> This software is intended **only** for use on systems you own or have explicit permission to test. Running the wrapped tools against unauthorized targets may be illegal.

## Prerequisites

KaliSuite does **not** ship the underlying security tools. You must have them installed on the host system (usually via `apt` on Debian‑based distributions). The tools currently referenced by the UI are:

- `nmap`
- `arp-scan`
- `theharvester`
- `nikto`
- `hydra`
- `john`
- `sqlmap`
- `gobuster`
- `tcpdump`
- `airodump-ng` (aircrack‑ng suite)
- `wash`
- `kismet`
- `reaver`
- `bully`
- `pixiewps`
- `spooftooph`

<img width="995" height="624" alt="Screenshot_2026-08-17_11-23-46" src="https://github.com/user-attachments/assets/4ccddf78-be2a-45e8-aa62-73972b3dbf8b" />
