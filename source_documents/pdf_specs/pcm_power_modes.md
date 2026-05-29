# PCM Power Mode Specification

**Document**: PCM-SPEC-2024-001  
**Revision**: 3.2  
**Status**: Released  
**ASIL**: B  
**Subsystem**: Powertrain Control Module — Power Mode Manager

---

## 1. Overview

The Power Mode Manager controls the ignition state machine within the Powertrain
Control Module (PCM). It governs transitions between vehicle power states based
on ignition switch position, battery voltage, engine RPM, and safety interlocks.

## 2. State Machine — Power Modes

```
                    ┌─────────┐
        ┌───────────│   OFF   │◄──────────────────────┐
        │           └────┬────┘                        │
        │                │ IGN_SW = ACC                 │
        │                ▼                              │
        │           ┌─────────┐                        │
        │     ┌─────│   ACC   │─────┐                  │
        │     │     └────┬────┘     │                  │
        │     │          │ IGN_SW   │ IGN_SW = OFF     │
        │     │          │ = RUN    │                   │
        │     │          ▼          │                   │
        │     │     ┌─────────┐    │                   │
        │     │     │   RUN   │────┘                   │
        │     │     └────┬────┘                        │
        │     │          │ START_REQ                    │
        │     │          │ = TRUE                       │
        │     │          ▼                              │
        │     │     ┌─────────┐                        │
        │     │     │  CRANK  │                        │
        │     │     └────┬────┘                        │
        │     │          │ RPM > 500                    │
        │     │          ▼                              │
        │     │     ┌─────────────┐                    │
        │     │     │ RUN_ENGINE  │                    │
        │     │     └──────┬──────┘                    │
        │     │            │ FAULT_CRITICAL = TRUE      │
        │     │            ▼                            │
        │     │     ┌──────────────────┐               │
        │     └────▶│ EMERGENCY_STOP   │───────────────┘
        │           └──────────────────┘
        │                  │
        └──────────────────┘
```

### 2.1 State Definitions

| State | ID | Description | Active Subsystems |
|-------|-----|-------------|-------------------|
| OFF | 0x00 | Vehicle fully powered down | None |
| ACC | 0x01 | Accessory mode — radio, windows, USB | Body electronics, infotainment |
| RUN | 0x02 | Ignition on, engine off — all ECUs powered | All ECUs, fuel pump primed |
| CRANK | 0x03 | Starter motor engaged | Starter relay, fuel injection |
| RUN_ENGINE | 0x04 | Engine running, normal operation | All systems |
| EMERGENCY_STOP | 0x05 | Critical fault detected, controlled shutdown | Safety-critical only |

### 2.2 Transition Conditions

| From | To | Condition | Timeout (ms) | Guard |
|------|----|-----------|-------------|-------|
| OFF | ACC | IGN_SW == ACC | — | BATT_V > 9.0V |
| ACC | RUN | IGN_SW == RUN | — | BATT_V > 10.5V |
| ACC | OFF | IGN_SW == OFF | 200 | — |
| RUN | CRANK | START_REQ == TRUE | — | TRANS_RANGE == P or N |
| CRANK | RUN_ENGINE | ENGINE_RPM > 500 | — | OIL_PRESS > 15 kPa |
| CRANK | RUN | CRANK_TIMEOUT | 10000 | — |
| RUN_ENGINE | RUN | IGN_SW == RUN && ENGINE_RPM < 100 | 3000 | — |
| RUN_ENGINE | EMERGENCY_STOP | FAULT_CRITICAL == TRUE | — | — |
| RUN | ACC | IGN_SW == ACC | 500 | — |
| RUN | OFF | IGN_SW == OFF | 500 | — |
| EMERGENCY_STOP | OFF | FAULT_CLEARED && IGN_SW == OFF | 5000 | — |

### 2.3 Safety Requirements

- **REQ-PM-001**: The system shall transition to EMERGENCY_STOP within 50ms of
  a critical fault detection.
- **REQ-PM-002**: The CRANK state shall not persist for more than 10 seconds
  (starter motor protection).
- **REQ-PM-003**: Transition from RUN to CRANK shall be inhibited unless
  transmission range is PARK or NEUTRAL.
- **REQ-PM-004**: Battery voltage below 9.0V shall prevent any upward state
  transition from OFF.
- **REQ-PM-005**: The EMERGENCY_STOP state shall maintain fuel pump shutoff and
  ignition disable until faults are cleared AND ignition is cycled to OFF.

## 3. CAN Interface

Power mode state is broadcast on CAN message `PCM_Status_1` (0x180):

| Signal | Start Bit | Length | Scale | Offset | Unit | Range |
|--------|-----------|--------|-------|--------|------|-------|
| PowerModeState | 0 | 4 | 1 | 0 | — | 0–5 |
| BatteryVoltage | 4 | 12 | 0.05 | 0 | V | 0–200 |
| EngineRPM | 16 | 16 | 0.25 | 0 | RPM | 0–16383 |
| IgnitionSwitch | 32 | 3 | 1 | 0 | — | 0–4 |
| StartRequest | 35 | 1 | 1 | 0 | — | 0–1 |
| FaultCritical | 36 | 1 | 1 | 0 | — | 0–1 |
| TransRange | 37 | 3 | 1 | 0 | — | 0–5 |
| OilPressure | 40 | 8 | 1 | 0 | kPa | 0–255 |
| CrankTimer | 48 | 16 | 1 | 0 | ms | 0–65535 |
