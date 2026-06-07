---
name: s1
description: CSV/pandas data processing, PID control loops, vehicle dynamics simulation, and YAML config handling.
---

# CSV Processing with Pandas

```python
import pandas as pd

df = pd.read_csv('data.csv')
print(df.head())
print(df.columns.tolist())
print(len(df))
```

Strip invisible zero-width Unicode characters (U+200B, U+200C, U+200D) that break numeric parsing: run `python3 /root/.claude/skills/s1/scripts/clean_data.py /root/sensor_data.csv` or filter `unicodedata.category(c)` for `Cf`.

```python
df = pd.read_csv('data.csv', na_values=['', 'NA', 'null'])
print(df.isnull().sum())
```

```python
values = df['column_name']
subset = df[['col1', 'col2']]
filtered = df[df['column'] > 10]
filtered = df[(df['time'] >= 30) & (df['time'] < 60)]
valid = df[df['column'].notna()]
```

```python
data = {'time': [0.0, 0.1, 0.2], 'value': [1.0, 2.0, 3.0]}
df = pd.DataFrame(data)
df.to_csv('output.csv', index=False)
```

```python
results = []
for item in items:
    row = {'time': item.time, 'value': item.value}
    results.append(row)
df = pd.DataFrame(results)
df.to_csv('results.csv', index=False)
```

# PID Controller

Control law: `output = Kp * error + Ki * integral(error) + Kd * derivative(error)` where `error = setpoint - measured_value`.

```python
class PIDController:
    def __init__(self, kp, ki, kd, output_min=None, output_max=None):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.output_min, self.output_max = output_min, output_max
        self.integral, self.prev_error = 0.0, 0.0

    def reset(self):
        self.integral, self.prev_error = 0.0, 0.0

    def compute(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        self.prev_error = error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        if self.output_min is not None:
            output = max(output, self.output_min)
        if self.output_max is not None:
            output = min(output, self.output_max)
        return output
```

Anti-windup: mitigate integral accumulation during saturation via clamping, conditional integration, or back-calculation. Tuning: set Ki=Kd=0, increase Kp for speed; add Ki to eliminate steady-state error; add Kd to reduce overshoot.

# Performance Metrics

```python
def rise_time(times, values, target):
    t10 = t90 = None
    for t, v in zip(times, values):
        if t10 is None and v >= 0.1 * target:
            t10 = t
        if t90 is None and v >= 0.9 * target:
            t90 = t
            break
    return (t90 - t10) if t10 is not None and t90 is not None else None
```

```python
def overshoot_percent(values, target):
    max_val = max(values)
    return ((max_val - target) / target) * 100 if max_val > target else 0.0
```

```python
def steady_state_error(values, target, final_fraction=0.1):
    n = len(values)
    start = int(n * (1 - final_fraction))
    final_avg = sum(values[start:]) / len(values[start:])
    return abs(target - final_avg)
```

```python
def settling_time(times, values, target, tolerance=0.02):
    band = target * tolerance
    lower, upper = target - band, target + band
    settled_at = None
    for t, v in zip(times, values):
        if v < lower or v > upper:
            settled_at = None
        elif settled_at is None:
            settled_at = t
    return settled_at
```

# Vehicle Dynamics

```python
new_speed = max(0, current_speed + acceleration * dt)
new_position = current_position + speed * dt
relative_speed = ego_speed - lead_speed
new_distance = current_distance - relative_speed * dt
```

```python
def safe_following_distance(speed, time_headway, min_distance):
    return speed * time_headway + min_distance
```

```python
def time_to_collision(distance, ego_speed, lead_speed):
    relative_speed = ego_speed - lead_speed
    return distance / relative_speed if relative_speed > 0 else None
```

```python
def clamp_acceleration(accel, max_accel, max_decel):
    return max(max_decel, min(accel, max_accel))
```

```python
def determine_mode(lead_present, ttc, ttc_threshold):
    if not lead_present:
        return 'cruise'
    if ttc is not None and ttc < ttc_threshold:
        return 'emergency'
    return 'follow'
```

# YAML Configuration

Always use `safe_load` to prevent code execution.

```python
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
value = config['section']['key']
```

```python
data = {'settings': {'param1': 1.5, 'param2': 0.1}}
with open('output.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
```

```python
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    config = {}
except yaml.YAMLError as e:
    print(f"YAML parse error: {e}")
    config = {}
```

```python
import os

def load_config(filepath, defaults=None):
    if defaults is None:
        defaults = {}
    if not os.path.exists(filepath):
        return defaults
    with open(filepath, 'r') as f:
        loaded = yaml.safe_load(f) or {}
    result = defaults.copy()
    result.update(loaded)
    return result