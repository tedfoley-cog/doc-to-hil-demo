# Diagnostic Trouble Code (DTC) Matrix

**Document**: DIAG-SPEC-2024-002  
**Revision**: 1.5  
**Status**: Released  
**Standard**: ISO 15031-6 / SAE J2012

---

## 1. Powertrain DTCs (P-Codes)

| DTC | Description | Enable Condition | Fault Action | Debounce | MIL |
|-----|-------------|-----------------|-------------|----------|-----|
| P0101 | MAF Sensor Range/Performance | Engine running > 2s | Reduce torque 20% | 3 consecutive trips | Yes |
| P0117 | Coolant Temp Sensor Low | Engine running > 30s | Use default 90°C | 2 consecutive trips | Yes |
| P0300 | Random Misfire Detected | RPM > 500, load > 10% | Fuel cut on affected cyl | 50 misfires / 200 rev | Yes |
| P0335 | Crankshaft Position Sensor | Cranking or running | No start / stall | Immediate | Yes |
| P0500 | Vehicle Speed Sensor | Vehicle moving, no ABS fault | Disable cruise control | 3 consecutive trips | Yes |
| P0562 | System Voltage Low | Engine running > 5s | Load shed non-essential | 5 seconds continuous | Yes |
| P0602 | PCM Not Programmed | Key on | Prevent start | Immediate | Yes |
| P0700 | Transmission Control System | TCM reports fault | Limp mode (3rd gear lock) | Per TCM debounce | Yes |
| P0715 | Turbine Speed Sensor | Shift in progress | Abort shift, limp mode | 2 consecutive shifts | Yes |
| P0730 | Incorrect Gear Ratio | Shift complete | Log event, request diag | 3 consecutive shifts | No |

## 2. Chassis DTCs (C-Codes)

| DTC | Description | Enable Condition | Fault Action | Debounce | MIL |
|-----|-------------|-----------------|-------------|----------|-----|
| C0035 | LF Wheel Speed Sensor | Vehicle speed > 10 km/h | Disable ABS on LF | 2 seconds continuous | ABS lamp |
| C0040 | RF Wheel Speed Sensor | Vehicle speed > 10 km/h | Disable ABS on RF | 2 seconds continuous | ABS lamp |
| C0045 | LR Wheel Speed Sensor | Vehicle speed > 10 km/h | Disable ABS on LR | 2 seconds continuous | ABS lamp |
| C0050 | RR Wheel Speed Sensor | Vehicle speed > 10 km/h | Disable ABS on RR | 2 seconds continuous | ABS lamp |
| C0121 | Valve Relay Circuit | Key on | Full ABS disable | Immediate | ABS lamp |
| C0550 | ECU Internal Fault | Key on | Full ABS disable | 3 key cycles | ABS lamp |

## 3. Body DTCs (B-Codes)

| DTC | Description | Enable Condition | Fault Action | Debounce | MIL |
|-----|-------------|-----------------|-------------|----------|-----|
| B1000 | BCM Internal Fault | Key on | Safe mode (locks only) | 3 key cycles | None |
| B1318 | Battery Voltage Low | Key on, engine off | Disable interior lights | 30 seconds continuous | None |
| B1600 | PATS Key Not Programmed | Key on | Prevent start | Immediate | Theft lamp |
| B2100 | Door Ajar Circuit | Key on | Override dome light | 500ms debounce | None |

## 4. DTC Cross-References

| DTC | Related Requirement | Related Signal | ECU |
|-----|-------------------|---------------|-----|
| P0101 | REQ-PM-004 | EMS_Status_1.IntakeAirTemp | EMS |
| P0335 | REQ-PM-001 | EMS_Status_1.EngineRPM | EMS |
| P0562 | REQ-PM-004 | PCM_Status_1.BatteryVoltage | PCM |
| P0700 | REQ-TR-009 | TCM_Status_1.ShiftAbortFlag | TCM |
| P0715 | REQ-TR-008 | TCM_Status_1.ShiftPhase | TCM |
| P0730 | REQ-TR-009 | TCM_Status_1.CurrentGear | TCM |
| C0035 | REQ-TR-003 | ABS_WheelSpeed.WheelSpeed_FL | ABS |
