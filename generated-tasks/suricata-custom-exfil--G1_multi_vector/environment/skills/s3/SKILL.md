---
name: s1
description: Combined skills for Suricata rule writing with PCAP analysis, IDS configuration, and multi-challenge handling guidance.
---

# Suricata Rules Basics

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

- `sid` — unique rule id.
- `rev` — rule revision.
- `flow:established,to_server` — constrain direction/state.

## Content matching

- `content:"...";` matches fixed bytes.
- Add modifiers/buffers to scope where the match occurs.

## Sticky buffers (protocol aware)

Prefer protocol-specific buffers to avoid matching unrelated bytes in the TCP stream.

Common HTTP sticky buffers: `http.method`, `http.uri`, `http.header`, `http_client_body` (request body).

## Multi-vector setup

1. Fix directory permissions if `/root` is read-only:
   ```bash
   python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/local.rules
   ```
2. Install PCAP analysis dependency if missing:
   ```bash
   pip3 install scapy==2.5.0
   ```

## Task template: Custom telemetry exfil

For the `suricata-custom-exfil` task, compose a rule using HTTP sticky buffers.

### Minimal scaffold

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

### Focused examples

**Exact HTTP method**
```
http.method;
content:"POST";
```

**Exact URI/path match**
```
http.uri;
content:"/telemetry/v2/report";
```

**Header field/value** — represent `:` as hex (`|3a|`):
```
http.header;
content:"X-TLM-Mode|3a| exfil";
```

**Body required parameters**
```
http_client_body;
content:"blob=";

http_client_body;
content:"sig=";
```

**Regex for 64 hex characters (sig=...)**
```
http_client_body;
pcre:"/sig=[0-9a-fA-F]{64}/";
```

**Regex for Base64-ish blob with length constraint**
```
http_client_body;
pcre:"/blob=[A-Za-z0-9+\\/]{80,}/";
```

# Suricata Offline Mode + EVE JSON

## Run Suricata on a PCAP

```bash
suricata -c /root/suricata.yaml -S /root/local.rules -k none -r /root/sample.pcap -l /tmp/suri
```

Flags: `-r <pcap>` replay offline, `-S <rules>` load only specified rules file, `-l <dir>` log directory (contains `eve.json`), `-k none` ignore checksum issues.

## Inspect alerts in EVE JSON

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

## Quick filters

List HTTP traffic:

```bash
tshark -r file.pcap -Y http
```

Filter by method:

```bash
tshark -r file.pcap -Y 'http.request.method == "POST"'
```

## Inspect requests

```bash
tshark -r file.pcap -Y http.request \
  -T fields -e frame.time -e ip.src -e tcp.srcport -e http.request.method -e http.request.uri
```

## Follow a TCP stream

```bash
tshark -r file.pcap -z follow,tcp,ascii,0
```

Change stream index (`0`) for multiple streams.

## Export payload bytes

```bash
tshark -r file.pcap -Y http -x
```

## Helper script

Quick summary across a PCAP (method, uri, exfil header presence):

```bash
bash scripts/summarize_http_requests.sh /root/pcaps/train_pos.pcap