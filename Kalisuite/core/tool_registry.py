"""
Simple dictionary‑based registry that defines the available tools,
their categories, command templates and required arguments.
"""

TOOL_REGISTRY = {
    "nmap": {
        "name": "nmap",
        "category": "recon",
        "description": "Network discovery and security auditing tool.",
        "command_template": "nmap {scan_type} {target}",
        "required_args": ["target", "scan_type"],
        "scan_types": {
            "quick": "-T4 -F",
            "version": "-sV",
            "full": "-A -T4",
            "all-ports": "-p-",
        },
    },
    "arpscan": {
        "name": "arp-scan",
        "category": "recon",
        "description": "ARP scanning tool for discovering hosts on a network.",
        "binary": "arp-scan",
        "command_template": "sudo arp-scan --interface={interface} {mode_flag}",
        "required_args": ["interface", "mode_flag"],
        "scan_modes": {
            "Local network": "--localnet",
            "Custom range": "",  # placeholder, will be replaced with user‑provided range
        },
    },
    "metasploit": {
        "name": "metasploit",
        "category": "exploitation",
        "description": "Metasploit Framework via RPC daemon.",
        "binary": "msfrpcd",
        # No command_template needed for RPC‑based interaction.
        "required_args": [],  # options are handled dynamically by the widget.
    },
    "siege": {
        "name": "siege",
        "category": "load testing",
        "description": "HTTP load testing tool.",
        "binary": "siege",
        "command_template": "siege -c {concurrent} -t {duration} -d {delay} {url}",
        "required_args": ["url", "concurrent", "duration", "delay"],
    },
    "theharvester": {
        "name": "theharvester",
        "category": "recon",
        "description": "Passive information gathering tool (theHarvester).",
        "binary": "theHarvester",
        "command_template": "theHarvester -d {domain} -b {source} -l {limit}",
        "required_args": ["domain", "source", "limit"],
    },
    "nikto": {
        "name": "nikto",
        "category": "recon",
        "description": "Web server scanner.",
        "binary": "nikto",
        "command_template": "nikto -h {target} -p {port} {ssl_flag}",
        "required_args": ["target", "port", "ssl_flag"],
    },
    "hydra": {
        "name": "hydra",
        "category": "password attacks",
        "description": "Parallelized login cracker supporting many protocols.",
        "binary": "hydra",
        "command_template": "hydra -l {username} -P {wordlist} -t {threads} {target} {service}",
        "required_args": ["username", "wordlist", "threads", "target", "service"],
    },
    "john": {
        "name": "john",
        "category": "password attacks",
        "description": "John the Ripper password cracking tool.",
        "binary": "john",
        "command_template": "john --format={format} {hashfile}",
        "required_args": ["format", "hashfile", "wordlist"],
    },
    "sqlmap": {
        "name": "sqlmap",
        "category": "web application",
        "description": "Automatic SQL injection and database takeover tool.",
        "binary": "sqlmap",
        "command_template": "sqlmap -u {url} --risk={risk} --level={level} {batch_flag}",
        "required_args": ["url", "risk", "level", "batch_flag"],
    },
    "gobuster": {
        "name": "gobuster",
        "category": "web application",
        "description": "Directory and file brute‑forcing tool.",
        "binary": "gobuster",
        "command_template": "gobuster dir -u {url} -w {wordlist} {ext_flag}",
        "required_args": ["url", "wordlist", "ext_flag"],
    },
    "tcpdump": {
        "name": "tcpdump",
        "category": "sniffing",
        "description": "Network packet capture tool.",
        "binary": "tcpdump",
        "command_template": "sudo tcpdump -i {interface} -c {count} {save_flag} {filter}",
        "required_args": ["interface", "count", "save_flag", "filter"],
    },
    "aircrack": {
        "name": "aircrack‑ng",
        "category": "wireless",
        "description": "Wireless network discovery/capture tool (airodump‑ng).",
        "binary": "airodump-ng",
        "command_template": "sudo airodump-ng {interface} {channel_opt} {write_opt}",
        "required_args": ["interface", "channel_opt", "write_opt"],
    },
    "wash": {
        "name": "wash",
        "category": "wireless",
        "description": "WPS scanner from the reaver suite (passive discovery).",
        "binary": "wash",
        "command_template": "sudo wash -i {interface} {channel_opt}",
        "required_args": ["interface", "channel_opt"],
    },
    "kismet": {
        "name": "kismet",
        "category": "wireless",
        "description": "Passive wireless detection/monitoring tool.",
        "binary": "kismet",
        "command_template": "kismet -c {interface}",
        "required_args": ["interface"],
    },
    # New Wireless tools added in version 0.1.0
    "reaver": {
        "name": "reaver",
        "category": "wireless",
        "description": "Performs a brute‑force attack against an access point's WPS PIN to recover the WPA/WPA2 passphrase.",
        "binary": "reaver",
        "command_template": "reaver -i {interface} -b {bssid} -vv {channel_opt} {pin_opt}",
        "required_args": ["interface", "bssid", "channel_opt", "pin_opt"],
    },
    "bully": {
        "name": "bully",
        "category": "wireless",
        "description": "Fast C‑based alternative to Reaver for attacking WPS.",
        "binary": "bully",
        "command_template": "bully -b {bssid} -i {interface} {channel_opt} {pin_opt}",
        "required_args": ["interface", "bssid", "channel_opt", "pin_opt"],
    },
    "pixiewps": {
        "name": "pixiewps",
        "category": "wireless",
        "description": "Leverages the Pixie Dust vulnerability to crack WPS PINs within seconds.",
        "binary": "pixiewps",
        "command_template": "pixiewps -i {interface} -b {bssid} -e {essid} {pin_opt}",
        "required_args": ["interface", "bssid", "essid", "pin_opt"],
    },
    # New Bluetooth tool
    "spooftooph": {
        "name": "spooftooph",
        "category": "bluetooth",
        "description": "Bluetooth MAC address spoofing tool.",
        "binary": "spooftooph",
        "command_template": "spooftooph -i {adapter} -t {target}",
        "required_args": ["adapter", "target"],
    },
    # Future tools can be added here following the same structure.
}
