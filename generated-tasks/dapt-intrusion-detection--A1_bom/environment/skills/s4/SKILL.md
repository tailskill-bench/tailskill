---
name: s1
description: "PCAP analysis with Python utilities and threat detection thresholds."
---

# PCAP Analysis & Threat Detection

## Helper Module (`pcap_utils.py`)

```python
import sys
sys.path.insert(0, '/root/skills/pcap-analysis')
from pcap_utils import (
    load_packets, split_by_protocol, graph_metrics,
    detect_port_scan, detect_dos_pattern, detect_beaconing,
    port_counters, ip_counters, iat_stats, flow_metrics,
    packets_per_minute_stats, producer_consumer_counts, shannon_entropy
)

packets = load_packets('/root/packets.pcap')
parts = split_by_protocol(packets)
g = graph_metrics(parts['ip'])
```

## Reading PCAPs & Stats

```python
from scapy.all import rdpcap, IP, TCP, UDP, ICMP, ARP

packets = rdpcap('packets.pcap')
ip_packets = [p for p in packets if IP in p]
tcp_packets = [p for p in packets if TCP in p]
udp_packets = [p for p in packets if UDP in p]

total_packets = len(packets)
total_bytes = sum(len(p) for p in packets)
avg_packet_size = total_bytes / total_packets
tcp_count = len([p for p in packets if TCP in p])
udp_count = len([p for p in packets if UDP in p])
icmp_count = len([p for p in packets if ICMP in p])
arp_count = len([p for p in packets if ARP in p])
```

## Entropy

```python
import math
from collections import Counter

def shannon_entropy(counter):
    total = sum(counter.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counter.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy

dst_ports = Counter()
for pkt in tcp_packets:
    dst_ports[pkt[TCP].dport] += 1
for pkt in udp_packets:
    if IP in pkt:
        dst_ports[pkt[UDP].dport] += 1
port_entropy = shannon_entropy(dst_ports)
```

## Graph Metrics

**Degree = UNIQUE IPs, NOT packet count.**

```python
from collections import defaultdict

edges = set()
indegree = defaultdict(set)
outdegree = defaultdict(set)

for pkt in ip_packets:
    src, dst = pkt[IP].src, pkt[IP].dst
    edges.add((src, dst))
    indegree[dst].add(src)
    outdegree[src].add(dst)

all_nodes = set(indegree.keys()) | set(outdegree.keys())
num_nodes = len(all_nodes)
num_edges = len(edges)
network_density = num_edges / (num_nodes * (num_nodes - 1))
max_indegree = max(len(v) for v in indegree.values())
max_outdegree = max(len(v) for v in outdegree.values())
```

## Temporal: IAT & Beaconing

```python
timestamps = sorted(float(p.time) for p in packets)
iats = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]

iat_mean = sum(iats) / len(iats)
iat_variance = sum((x - iat_mean)**2 for x in iats) / len(iats)
iat_std = math.sqrt(iat_variance)
iat_cv = iat_std / iat_mean if iat_mean > 0 else 0
# CV < 0.5: robotic/beaconing; CV > 1.0: bursty/normal
```

### Producer/Consumer Ratio

```python
bytes_sent = defaultdict(int)
bytes_recv = defaultdict(int)

for pkt in ip_packets:
    size = len(pkt)
    bytes_sent[pkt[IP].src] += size
    bytes_recv[pkt[IP].dst] += size

num_producers = 0
num_consumers = 0
for ip in all_nodes:
    sent = bytes_sent.get(ip, 0)
    recv = bytes_recv.get(ip, 0)
    total = sent + recv
    if total > 0:
        pcr = (sent - recv) / total
        if pcr > 0.2:
            num_producers += 1
        elif pcr < -0.2:
            num_consumers += 1
```

## Flow Analysis

Flow = 5-tuple (src_ip, dst_ip, src_port, dst_port, protocol). Only count packets with BOTH IP AND transport layer.

```python
flows = set()
for pkt in tcp_packets:
    if IP in pkt:
        flow = (pkt[IP].src, pkt[IP].dst, pkt[TCP].sport, pkt[TCP].dport, "TCP")
        flows.add(flow)

for pkt in udp_packets:
    if IP in pkt:
        flow = (pkt[IP].src, pkt[IP].dst, pkt[UDP].sport, pkt[UDP].dport, "UDP")
        flows.add(flow)

unique_flows = len(flows)
tcp_flows = len([f for f in flows if f[4] == "TCP"])
udp_flows = len([f for f in flows if f[4] == "UDP"])

bidirectional_count = 0
for flow in flows:
    src_ip, dst_ip, src_port, dst_port, proto = flow
    reverse = (dst_ip, src_ip, dst_port, src_port, proto)
    if reverse in flows:
        bidirectional_count += 1
bidirectional_flows = bidirectional_count // 2
```

## Time Series

```python
timestamps = [float(p.time) for p in packets]
start_time = min(timestamps)

minute_buckets = defaultdict(int)
for ts in timestamps:
    minute = int((ts - start_time) / 60)
    minute_buckets[minute] += 1

packets_per_min = list(minute_buckets.values())
ppm_avg = sum(packets_per_min) / len(packets_per_min)
ppm_max = max(packets_per_min)
ppm_min = min(packets_per_min)
```

## CSV Output

```python
import csv

results = {
    "total_packets": total_packets,
    "protocol_tcp": tcp_count,
}

with open('network_stats.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

with open('network_stats.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['metric', 'value'])
    writer.writeheader()
    for row in rows:
        metric = row['metric']
        if metric.startswith('#'):
            writer.writerow(row)
        elif metric in results:
            writer.writerow({'metric': metric, 'value': results[metric]})
```

CSV may contain invisible zero-width Unicode. Filter via `unicodedata.category(c)` removing `Cf` chars, or run: `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/network_stats.csv`

## Threat Detection

| Threat | Conditions | Threshold |
|--------|-----------|-----------|
| Port Scan | Entropy AND SYN-ratio AND Ports | >6.0 AND >0.7 AND >100 |
| DoS | Max/Avg ratio | >20 |
| Beaconing | IAT CV | <0.5 |
| Benign | None of above | All false |

### Port Scan (ALL THREE required)

```python
import math
from collections import Counter, defaultdict
from scapy.all import IP, TCP

def detect_port_scan(tcp_packets):
    src_port_counts = defaultdict(Counter)
    src_syn_only = defaultdict(int)
    src_total = defaultdict(int)

    for pkt in tcp_packets:
        if IP not in pkt or TCP not in pkt:
            continue
        src = pkt[IP].src
        dst_port = pkt[TCP].dport
        flags = pkt[TCP].flags

        src_port_counts[src][dst_port] += 1
        src_total[src] += 1

        if flags & 0x02 and not (flags & 0x10):
            src_syn_only[src] += 1

    for src in src_port_counts:
        if src_total[src] < 50:
            continue

        port_counter = src_port_counts[src]
        total = sum(port_counter.values())
        entropy = -sum((c/total) * math.log2(c/total) for c in port_counter.values() if c > 0)

        syn_ratio = src_syn_only[src] / src_total[src]
        unique_ports = len(port_counter)

        if entropy > 6.0 and syn_ratio > 0.7 and unique_ports > 100:
            return True

    return False
```

### DoS & Beaconing

```python
def detect_dos_pattern(ppm_avg, ppm_max):
    if ppm_avg == 0:
        return False
    ratio = ppm_max / ppm_avg
    return ratio > 20

def detect_beaconing(iat_cv):
    return iat_cv < 0.5
```

### Benign Assessment

```python
from pcap_utils import detect_port_scan, detect_dos_pattern, detect_beaconing

has_port_scan = detect_port_scan(tcp_packets)
has_dos = detect_dos_pattern(ppm_avg, ppm_max)
has_beaconing = detect_beaconing(iat_cv)
is_traffic_benign = not (has_port_scan or has_dos or has_beaconing)