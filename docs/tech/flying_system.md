# 🦅 Flying System Design

## Core Components

### Mount Types
```python
class FlyingMount:
    name: str
    base_speed: float  # km/h
    acceleration_time: float  # seconds
    summon_time: float  # seconds
    model_type: str  # for visual representation
    required_level: int
```

### Speed Tiers
- Basic Mounts: 150 km/h
- Advanced Mounts: 218 km/h
- Premium Mounts: 276 km/h

### Flying Level System
- Experience gained from aerial combat
- Benefits:
  - Reduced summon time (-0.1s per level)
  - Faster acceleration (-0.05s per level)
  - No impact on max speed

## Implementation Details

### Physics
```python
class FlyingPhysics:
    current_speed: Vector2
    max_speed: float
    acceleration: float
    altitude: float
    max_altitude: float = 1000  # units
    min_altitude: float = 0
```

### Controls
- Space: Ascend
- Shift: Descend
- WASD: Directional movement
- Double-tap Space: Quick ascend
- Double-tap Shift: Quick descend
- Q: Mount/Dismount

### Mount Examples
```python
MOUNTS = {
    "training_broom": {
        "speed": 150,
        "accel_time": 2.0,
        "summon_time": 3.0,
        "req_level": 20
    },
    "sky_board": {
        "speed": 218,
        "accel_time": 1.5,
        "summon_time": 2.0,
        "req_level": 30
    },
    "cloud_rider": {
        "speed": 276,
        "accel_time": 1.0,
        "summon_time": 1.5,
        "req_level": 40
    }
}
```

### Flying Experience System
```python
class FlyingStats:
    level: int
    experience: int
    total_flight_time: float
    aerial_kills: int
    
    def calculate_summon_time(self, base_time: float) -> float:
        return max(0.5, base_time - (self.level * 0.1))
        
    def calculate_accel_time(self, base_time: float) -> float:
        return max(0.3, base_time - (self.level * 0.05))
```

## Visual Effects
- Mount summoning animation
- Speed lines at high velocities
- Altitude clouds/particles
- Wind streaks during sharp turns
- Mount-specific particle trails

## Combat Integration
- Aerial combat enabled flag
- Special aerial-only abilities
- Height advantage mechanics
- Aerial monster spawning zones

## Future Enhancements
- [ ] Mount customization
- [ ] Special aerial-only zones
- [ ] Flying races/time trials
- [ ] Mount evolution system
- [ ] Aerial guild battles 