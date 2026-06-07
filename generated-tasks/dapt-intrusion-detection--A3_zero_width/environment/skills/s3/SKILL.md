---
name: s1
description: "Guidance for analyzing PCAP files and computing network statistics using Python with tested utility functions. Detection thresholds for port scans, DoS attacks, and beaconing."
---

# PCAP Network Analysis Guide

## Helper Module (`pcap_utils.py`)

Tested implementations at `/root/skills/pcap-analysis`. **Use these instead of reimplementing** — they handle edge cases and use calibrated thresholds.

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
print(detect_port_scan(parts['tcp']))
print(detect_dos_pattern(ppm_avg, ppm_max))
print(detect_beaconing(iat_cv))
```

## Reading PCAP & Basic Stats

```python
from scapy.all import rdpcap, IP, TCP, UDP, ICMP, ARP

packets = rdpcap('packets.pcap')
ip_packets = [p for p in packets if IP in p]
tcp_packets = [p for p in packets if TCP in p]
udp_packets = [p for p in packets if UDP in p]

total_packets = len(packets)
total_bytes = sum(len(p) for p in packets)
tcp_count = len(tcp_packets)
udp_count = len(udp_packets)
icmp_count = len([p for p in packets if ICMP in p])
arp_count = len([p for p in packets if ARP in p])
```

## Entropy

Shannon entropy: `H(X) = -Σ p(x) log₂(p(x))`. Low = focused traffic (normal). High = spread across many items (scanning).

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
```

## Graph Metrics

**Use `graph_metrics()` from pcap_utils.py.** Degree = UNIQUE IPs, NOT packet count. For 38 nodes, max_indegree ≤ 37.

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

## Temporal Metrics

### IAT & CV

```python
timestamps = sorted(float(p.time) for p in packets)
iats = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
iat_mean = sum(iats) / len(iats)
iat_std = math.sqrt(sum((x - iat_mean)**2 for x in iats) / len(iats))
iat_cv = iat_std / iat_mean if iat_mean > 0 else 0
```

### Producer/Consumer Ratio

PCR = (sent - recv) / (sent + recv). Positive = producer, Negative = consumer.

```python
bytes_sent = defaultdict(int)
bytes_recv = defaultdict(int)
for pkt in ip_packets:
    bytes_sent[pkt[IP].src] += len(pkt)
    bytes_recv[pkt[IP].dst] += len(pkt)

num_producers = num_consumers = 0
for ip in all_nodes:
    total = bytes_sent.get(ip, 0) + bytes_recv.get(ip, 0)
    if total > 0:
        pcr = (bytes_sent.get(ip, 0) - bytes_recv.get(ip, 0)) / total
        if pcr > 0.2: num_producers += 1
        elif pcr < -0.2: num_consumers += 1
```

## Flow Analysis

Flow = (src_ip, dst_ip, src_port, dst_port, protocol). Only count packets with BOTH IP and transport layer.

```python
flows = set()
for pkt in tcp_packets:
    if IP in pkt:
        flows.add((pkt[IP].src, pkt[IP].dst, pkt[TCP].sport, pkt[TCP].dport, "TCP"))
for pkt in udp_packets:
    if IP in pkt:
        flows.add((pkt[IP].src, pkt[IP].dst, pkt[UDP].sport, pkt[UDP].dport, "UDP"))

bidirectional_count = 0
for flow in flows:
    rev = (flow[1], flow[0], flow[3], flow[2], flow[4])
    if rev in flows: bidirectional_count += 1
bidirectional_flows = bidirectional_count // 2
```

## Time Series

```python
start_time = min(float(p.time) for p in packets)
minute_buckets = defaultdict(int)
for ts in [float(p.time) for p in packets]:
    minute_buckets[int((ts - start_time) / 60)] += 1
ppm_avg = sum(minute_buckets.values()) / len(minute_buckets)
ppm_max = max(minute_buckets.values())
```

## CSV Output

```python
import csv
results = {"total_packets": total_packets, "protocol_tcp": tcp_count}
with open('network_stats.csv', 'r') as f:
    rows = list(csv.DictReader(f))
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

**CSV may contain zero-width Unicode.** Clean with: `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/network_stats.csv`

## Detection Thresholds

### Port Scan (ALL THREE required)

```python
def detect_port_scan(tcp_packets):
    src_port_counts = defaultdict(Counter)
    src_syn_only = defaultdict(int)
    src_total = defaultdict(int)
    for pkt in tcp_packets:
        if IP not in pkt or TCP not in pkt:
            continue
        src = pkt[IP].src
        src_port_counts[src][pkt[TCP].dport] += 1
        src_total[src] += 1
        if pkt[TCP].flags & 0x02 and not (pkt[TCP].flags & 0x10):
            src_syn_only[src] += 1
    for src in src_port_counts:
        if src_total[src] < 50:
            continue
        pc = src_port_counts[src]
        total = sum(pc.values())
        entropy = -sum((c/total) * math.log2(c/total) for c in pc.values() if c > 0)
        syn_ratio = src_syn_only[src] / src_total[src]
        if entropy > 6.0 and syn_ratio > 0.7 and len(pc) > 100:
            return True
    return False
```

### DoS (max/avg > 20)

```python
def detect_dos_pattern(ppm_avg, ppm_max):
    return ppm_avg > 0 and (ppm_max / ppm_avg) > 20
```

### Beaconing (IAT CV < 0.5)

```python
def detect_beaconing(iat_cv):
    return iat_cv < 0.5
```

### Benign = none of the above

```python
is_benign = not (detect_port_scan(tcp_packets) or detect_dos_pattern(ppm_avg, ppm_max) or detect_beaconing(iat_cv))
```

## Summary

| Threat | Conditions | Threshold |
|--------|-----------|-----------|
| Port Scan | Entropy AND SYN-ratio AND Ports | >6.0 AND >0.7 AND >100 |
| DoS | Max/Avg ratio | >20 |
| Beaconing | IAT CV | <0.5 |
| Benign | None above | All false |