# CAN Signal Catalog — Vehicle Network

**Document**: CAN-CAT-2024-001  
**Revision**: 4.0  
**Status**: Released  
**Network**: HS-CAN (500 kbps)

---

## 1. Message Overview

| Msg ID | Name | Sender | Cycle (ms) | DLC | Priority |
|--------|------|--------|-----------|-----|----------|
| 0x100 | EMS_Torque_1 | EMS | 10 | 8 | High |
| 0x120 | EMS_Status_1 | EMS | 20 | 8 | High |
| 0x180 | PCM_Status_1 | PCM | 20 | 8 | High |
| 0x200 | ABS_WheelSpeed | ABS | 10 | 8 | High |
| 0x280 | TCM_Status_1 | TCM | 20 | 8 | Medium |
| 0x300 | BCM_Status_1 | BCM | 100 | 8 | Low |
| 0x380 | IC_Display_1 | IC | 50 | 8 | Low |
| 0x400 | ADAS_Status_1 | ADAS | 20 | 8 | High |

## 2. Detailed Signal Definitions

### 2.1 EMS_Torque_1 (0x100) — Engine Torque

| Signal | Start Bit | Length | Byte Order | Scale | Offset | Min | Max | Unit |
|--------|-----------|--------|-----------|-------|--------|-----|-----|------|
| ActualTorque | 0 | 16 | Little-Endian | 0.5 | -500 | -500 | 1500 | Nm |
| RequestedTorque | 16 | 16 | Little-Endian | 0.5 | -500 | -500 | 1500 | Nm |
| TorqueLimit | 32 | 16 | Little-Endian | 0.5 | 0 | 0 | 2000 | Nm |
| TorqueMode | 48 | 4 | Little-Endian | 1 | 0 | 0 | 10 | — |
| TorqueValid | 52 | 1 | — | 1 | 0 | 0 | 1 | — |

### 2.2 EMS_Status_1 (0x120) — Engine Status

| Signal | Start Bit | Length | Byte Order | Scale | Offset | Min | Max | Unit |
|--------|-----------|--------|-----------|-------|--------|-----|-----|------|
| EngineRPM | 0 | 16 | Little-Endian | 0.25 | 0 | 0 | 16383 | RPM |
| CoolantTemp | 16 | 8 | — | 1 | -40 | -40 | 215 | degC |
| IntakeAirTemp | 24 | 8 | — | 1 | -40 | -40 | 215 | degC |
| EngineRunning | 32 | 1 | — | 1 | 0 | 0 | 1 | — |
| CheckEngineLamp | 33 | 1 | — | 1 | 0 | 0 | 1 | — |
| FuelCutActive | 34 | 1 | — | 1 | 0 | 0 | 1 | — |

### 2.3 ABS_WheelSpeed (0x200) — Wheel Speeds

| Signal | Start Bit | Length | Byte Order | Scale | Offset | Min | Max | Unit |
|--------|-----------|--------|-----------|-------|--------|-----|-----|------|
| WheelSpeed_FL | 0 | 16 | Little-Endian | 0.01 | 0 | 0 | 655.35 | km/h |
| WheelSpeed_FR | 16 | 16 | Little-Endian | 0.01 | 0 | 0 | 655.35 | km/h |
| WheelSpeed_RL | 32 | 16 | Little-Endian | 0.01 | 0 | 0 | 655.35 | km/h |
| WheelSpeed_RR | 48 | 16 | Little-Endian | 0.01 | 0 | 0 | 655.35 | km/h |

### 2.4 ADAS_Status_1 (0x400) — Advanced Driver Assistance

| Signal | Start Bit | Length | Byte Order | Scale | Offset | Min | Max | Unit |
|--------|-----------|--------|-----------|-------|--------|-----|-----|------|
| ACC_Active | 0 | 1 | — | 1 | 0 | 0 | 1 | — |
| ACC_SetSpeed | 1 | 9 | Little-Endian | 0.5 | 0 | 0 | 255 | km/h |
| LKA_Active | 10 | 1 | — | 1 | 0 | 0 | 1 | — |
| AEB_Warning | 11 | 1 | — | 1 | 0 | 0 | 1 | — |
| AEB_BrakeReq | 12 | 1 | — | 1 | 0 | 0 | 1 | — |
| TargetDistance | 16 | 16 | Little-Endian | 0.1 | 0 | 0 | 300 | m |
| TargetSpeed | 32 | 16 | Little-Endian | 0.01 | 0 | 0 | 300 | km/h |
