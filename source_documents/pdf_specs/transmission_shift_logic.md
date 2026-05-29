# Transmission Shift Logic Specification

**Document**: TCM-SPEC-2024-003  
**Revision**: 2.1  
**Status**: Released  
**ASIL**: B  
**Subsystem**: Transmission Control Module — Shift Scheduler

---

## 1. Overview

The Shift Scheduler determines optimal gear selection based on vehicle speed,
throttle position, engine load, and driver-selected mode. It implements a
table-driven shift schedule with hysteresis to prevent gear hunting.

## 2. Shift Flow Diagram

```
  ┌─────────────────┐
  │  Shift Request   │
  │  (from schedule) │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐     No    ┌──────────────┐
  │ Torque Capacity  │────────▶│ Reject Shift  │
  │ Check Passed?    │         └──────────────┘
  └────────┬────────┘
           │ Yes
           ▼
  ┌─────────────────┐     No    ┌──────────────┐
  │ Engine Speed     │────────▶│ Wait & Retry  │
  │ Within Range?    │         └──────────────┘
  └────────┬────────┘
           │ Yes
           ▼
  ┌─────────────────┐
  │ Reduce Torque    │
  │ (torque phase)   │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Apply Clutch     │
  │ (inertia phase)  │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Synchronize RPM  │
  │ (speed match)    │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐     No    ┌──────────────┐
  │ Shift Complete   │────────▶│ Abort Shift   │
  │ Verified?        │         │ (DTC logged)  │
  └────────┬────────┘         └──────────────┘
           │ Yes
           ▼
  ┌─────────────────┐
  │ Restore Torque   │
  │ (end phase)      │
  └─────────────────┘
```

## 3. Shift Schedule Tables

### 3.1 Upshift Schedule (Normal Mode)

| Current Gear | Throttle 0-25% | Throttle 25-50% | Throttle 50-75% | Throttle 75-100% |
|-------------|----------------|-----------------|-----------------|------------------|
| 1 → 2 | 15 km/h | 25 km/h | 35 km/h | 45 km/h |
| 2 → 3 | 25 km/h | 40 km/h | 55 km/h | 70 km/h |
| 3 → 4 | 35 km/h | 55 km/h | 75 km/h | 95 km/h |
| 4 → 5 | 45 km/h | 65 km/h | 90 km/h | 115 km/h |
| 5 → 6 | 55 km/h | 75 km/h | 100 km/h | 130 km/h |

### 3.2 Downshift Schedule (Normal Mode)

| Current Gear | Throttle 0-25% | Throttle 25-50% | Throttle 50-75% | Throttle 75-100% |
|-------------|----------------|-----------------|-----------------|------------------|
| 2 → 1 | 10 km/h | 18 km/h | 28 km/h | 38 km/h |
| 3 → 2 | 20 km/h | 32 km/h | 45 km/h | 60 km/h |
| 4 → 3 | 28 km/h | 45 km/h | 65 km/h | 85 km/h |
| 5 → 4 | 38 km/h | 55 km/h | 80 km/h | 105 km/h |
| 6 → 5 | 48 km/h | 65 km/h | 90 km/h | 120 km/h |

### 3.3 Hysteresis Band

The difference between upshift and downshift speeds at the same throttle
position constitutes the hysteresis band, typically 5–8 km/h. This prevents
oscillation between gears on grades or during varying throttle input.

## 4. Gear Range State Machine

```
     ┌───┐   Brake + Button    ┌───┐
     │ P │◄────────────────────│ R │
     └─┬─┘                     └─┬─┘
       │ Brake + Button           │ Brake + Button
       ▼                          ▼
     ┌───┐                      ┌───┐
     │ R │                      │ N │
     └─┬─┘                      └─┬─┘
       │ Brake + Button           │ Speed < 5 km/h
       ▼                          ▼
     ┌───┐                      ┌───┐
     │ N │ ─────────────────── │ D │
     └───┘      Release Brake   └───┘
```

### 4.1 Range Interlock Conditions

| From | To | Condition | Safety Requirement |
|------|----|-----------|-------------------|
| P | R | Brake pedal pressed + shift button | REQ-TR-001 |
| R | N | Brake pedal pressed + shift button | REQ-TR-002 |
| N | D | Vehicle speed < 5 km/h | REQ-TR-003 |
| D | N | Brake pedal pressed + shift button | REQ-TR-004 |
| N | R | Vehicle speed < 3 km/h + brake pedal | REQ-TR-005 |
| Any | P | Vehicle speed < 2 km/h + brake pedal + shift button | REQ-TR-006 |

## 5. Safety Requirements

- **REQ-TR-001**: Reverse engagement shall require brake pedal application.
- **REQ-TR-002**: Neutral engagement from reverse shall require brake pedal.
- **REQ-TR-003**: Drive engagement shall be inhibited above 5 km/h.
- **REQ-TR-004**: Shift to neutral from drive requires brake pedal at any speed.
- **REQ-TR-005**: Reverse from neutral inhibited above 3 km/h.
- **REQ-TR-006**: Park engagement inhibited above 2 km/h.
- **REQ-TR-007**: Torque reduction shall complete within 100ms of shift initiation.
- **REQ-TR-008**: Total shift time (torque phase + inertia phase) shall not exceed 400ms.
- **REQ-TR-009**: Shift abort shall log DTC P0730 (Incorrect Gear Ratio).

## 6. CAN Interface

Transmission status is broadcast on CAN message `TCM_Status_1` (0x280):

| Signal | Start Bit | Length | Scale | Offset | Unit | Range |
|--------|-----------|--------|-------|--------|------|-------|
| CurrentGear | 0 | 4 | 1 | 0 | — | 0–8 |
| TargetGear | 4 | 4 | 1 | 0 | — | 0–8 |
| ShiftInProgress | 8 | 1 | 1 | 0 | — | 0–1 |
| ShiftPhase | 9 | 3 | 1 | 0 | — | 0–5 |
| GearRange | 12 | 3 | 1 | 0 | — | 0–4 |
| VehicleSpeed | 16 | 16 | 0.01 | 0 | km/h | 0–655 |
| ThrottlePosition | 32 | 8 | 0.392 | 0 | % | 0–100 |
| EngineLoad | 40 | 8 | 0.392 | 0 | % | 0–100 |
| TorqueReductionReq | 48 | 1 | 1 | 0 | — | 0–1 |
| ShiftAbortFlag | 49 | 1 | 1 | 0 | — | 0–1 |
