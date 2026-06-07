---
name: s1
description: CSV processing, PID control, vehicle dynamics simulation, control metrics, and YAML config handling.
---

# CSV Processing with Pandas

```python
import pandas as pd

df = pd.read_csv('data.csv')
print(df.head())
print(df.columns.tolist())
print(len(df))
```

For write permission issues in containers: `os.chmod('/root', 0o755)` or run `python3 /root/.claude/skills/s1/scripts/prepare_output.py /root/simulation_results.csv`

```python
data = {'time': [0.0, 0.1, 0.2], 'value': [1.0, 2.0, 3.0], 'label': ['a', 'b', 'c']}
df = pd.DataFrame(data)
df.to_csv('output.csv', index=False)
```

```python
df = pd.read_csv('data.csv', na_values=['', 'NA', 'null'])
print(df.isnull().sum())

if pd.isna(row['column']):
    pass  # Handle missing value
```

```python
values = df['column_name']
subset = df[['col1', 'col2']]
filtered = df[df['column'] > 10]
filtered = df[(df['time'] >= 30) & (df['time'] < 60)]
valid = df[df['column'].notna()]
```

```python
results = []
for item in items:
    results.append({'time': item.time, 'value': item.value, 'status': item.status if item.valid else None})

df = pd.DataFrame(results)
df.to_csv('results.csv', index=False)
```

```python
mean_val = df['column'].mean()
max_val = df['column'].max()
df['diff'] = df['col1'] - df['col2']

for index, row in df.iterrows():
    process(row['col1'], row['col2'])
```

# PID Controller

```
output = Kp * error + Ki * integral(error) + Kd * derivative(error)
```

Where `error = setpoint - measured_value`, `Kp`/`Ki`/`Kd` are proportional/integral/derivative gains.

```python
class PIDController:
    def __init__(self, kp, ki, kd, output_min=None, output_max=None):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max
        self.integral = 0.0
        self.prev_error = 0.0

    def reset(self):
        self.integral = 0.0
        self.prev_error = 0.0

    def compute(self, error, dt):
        p_term = self.kp * error
        self.integral += error * dt
        i_term = self.ki * self.integral
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        d_term = self.kd * derivative
        self.prev_error = error
        output = p_term + i_term + d_term
        if self.output_min is not None:
            output = max(output, self.output_min)
        if self.output_max is not None:
            output = min(output, self.output_max)
        return output
```

Anti-windup: (1) **Clamping** - limit integral magnitude, (2) **Conditional Integration** - only integrate when not saturated, (3) **Back-calculation** - reduce integral when clamped. Tuning: Set Ki=Kd=0, increase Kp for response speed. Add Ki to eliminate steady-state error. Add Kd to reduce overshoot.

# Control System Performance Metrics

```python
def rise_time(times, values, target):
    t10 = t90 = None
    for t, v in zip(times, values):
        if t10 is None and v >= 0.1 * target:
            t10 = t
        if t90 is None and v >= 0.9 * target:
            t90 = t
            break
    if t10 is not None and t90 is not None:
        return t90 - t10
    return None
```

```python
def overshoot_percent(values, target):
    max_val = max(values)
    if max_val <= target:
        return 0.0
    return ((max_val - target) / target) * 100
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

```python
times = [row['time'] for row in results]
values = [row['value'] for row in results]
target = 30.0

print(f"Rise time: {rise_time(times, values, target)}")
print(f"Overshoot: {overshoot_percent(values, target)}%")
print(f"SS Error: {steady_state_error(values, target)}")
```

# Vehicle Dynamics Simulation

```python
new_speed = current_speed + acceleration * dt
new_speed = max(0, new_speed)
```

```python
new_position = current_position + speed * dt
```

```python
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
    if relative_speed <= 0:
        return None
    return distance / relative_speed
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

Always use `safe_load` to prevent code execution:

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
import yaml

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
import yaml

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