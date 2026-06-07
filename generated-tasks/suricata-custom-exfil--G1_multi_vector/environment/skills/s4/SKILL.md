---
name: s1
description: Suricata rule writing with PCAP analysis, IDS configuration, and multi-challenge handling.
---

# Suricata Rules

## Rule anatomy

```
alert <proto> <src> <sport> -> <dst> <dport> (
  msg:"...";
  flow:...;
  content:"..."; <buffer/modifier>;
  pcre:"/.../"; <buffer/modifier>;
  sid:1000001;
  rev:1;
)
```

`sid` = unique rule id. `rev` = rule revision. `flow:established,to_server` constrains direction/state.

`content:"...";` matches fixed bytes. Add modifiers/buffers to scope where the match occurs.

**Sticky buffers** (protocol aware): prefer protocol-specific buffers to avoid matching unrelated bytes in the TCP stream. Common HTTP: `http.method`, `http.uri`, `http.header`, `http_client_body`.

## Multi-vector setup

```bash
python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/local.rules
pip3 install scapy==2.5.0
```

## Task: Custom telemetry exfil

```
alert http any any -> any any (
  msg:"TLM exfil";
  flow:established,to_server;

  # 1) Method constraint (use http.method)
  # 2) Exact path constraint (use http.uri)
  # 3) Header constraint (use http.header)
  # 4) Body constraints (use http_client_body)
  #    - blob= parameter: Base64-ish, length >= 80
  #    - sig= parameter: exactly 64 hex characters

  sid:1000001;
  rev:1;
)
```

**Examples:**

```
http.method; content:"POST";
http.uri; content:"/telemetry/v2/report";
http.header; content:"X-TLM-Mode|3a| exfil";
http_client_body; content:"blob=";
http_client_body; content:"sig=";
http_client_body; pcre:"/sig=[0-9a-fA-F]{64}/";
http_client_body; pcre:"/blob=[A-Za-z0-9+\\/]{80,}/";
```

# Suricata Offline Mode + EVE JSON

```bash
suricata -c /root/suricata.yaml -S /root/local.rules -k none -r /root/sample.pcap -l /tmp/suri
```

Flags: `-r <pcap>` replay offline, `-S <rules>` load only specified rules file, `-l <dir>` log directory (contains `eve.json`), `-k none` ignore checksum issues.

Count alerts:

```bash
jq -r 'select(.event_type=="alert") | .alert.signature_id' /tmp/suri/eve.json | wc -l
```

See alert ids and messages:

```bash
jq -r 'select(.event_type=="alert") | [.alert.signature_id,.alert.signature] | @tsv' /tmp/suri/eve.json
```

## Tight feedback loop

```bash
# 1) Validate rule syntax
suricata -T -c /root/suricata.yaml -S /root/local.rules

# 2) Run on known-positive traffic
suricata -c /root/suricata.yaml -S /root/local.rules -k none -r /root/pcaps/train_pos.pcap -l /tmp/suri-pos
jq -r 'select(.event_type=="alert") | .alert.signature_id' /tmp/suri-pos/eve.json | sort -n | uniq -c

# 3) Run on known-negative traffic
suricata -c /root/suricata.yaml -S /root/local.rules -k none -r /root/pcaps/train_neg.pcap -l /tmp/suri-neg
jq -r 'select(.event_type=="alert") | .alert.signature_id' /tmp/suri-neg/eve.json | sort -n | uniq -c
```

# PCAP Triage with tshark

```bash
tshark -r file.pcap -Y http
tshark -r file.pcap -Y 'http.request.method == "POST"'
tshark -r file.pcap -Y http.request -T fields -e frame.time -e ip.src -e tcp.srcport -e http.request.method -e http.request.uri
tshark -r file.pcap -z follow,tcp,ascii,0
tshark -r file.pcap -Y http -x
```

Change stream index (`0`) for multiple streams.

```bash
bash scripts/summarize_http_requests.sh /root/pcaps/train_pos.pcap