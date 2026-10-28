# Engineering Portfolio — Hakan OĞUZ

Electrical & Electronics Engineer. This repository collects my hands-on engineering
work across embedded systems, electronics, communications, power/electrical design,
CAD, MATLAB/Simulink modeling and PLC automation.

Each project lives in its own folder with a dedicated README that covers the goal, the
engineering reasoning behind the design, how to run or simulate it, and the results.

## Areas

- **autocad/** — Electrical CAD: layouts, single-line diagrams, panel and lighting design (DXF).
- **gomulu-elektronik/** — Embedded & electronics: ESP32 (ESP-IDF), PIC, Raspberry Pi, analog/digital circuits, RF & communications.
- **matlab-simulink/** — Modeling & simulation: motors, power electronics, energy systems, control, robotics.
- **plc/** — Industrial automation: IEC 61131-3 Structured Text (OpenPLC).

## Projects

| Project | Area | Summary |
|---|---|---|
| [110 kWp Rooftop Grid-Tied PV — Layout & SLD](autocad/cati-ustu-ges-saha-yerlesimi) | AutoCAD/DXF | Parameter-driven site layout and single-line diagram (ezdxf); string sizing, MPPT window and shading pitch calculations. |
| [Three-Phase Energy Analyzer Node](gomulu-elektronik/uc-faz-enerji-analizoru) | Embedded (ESP32) | True-RMS / power / PF / THD DSP core over Modbus TCP; firmware core validated on host against a numpy reference. |
| [10 kW Grid-Tied LCL Inverter — dq Vector Control](matlab-simulink/sebeke-baglantili-lcl-evirici) | MATLAB / Simulink | 3-phase grid-tied inverter with LCL filter, passive damping resonance attenuation, and decoupled dq frame current control (.slx model). |
| [6-DOF Manipulator Kinematics & Quintic Trajectory](matlab-simulink/manipulator-kinematik-yorunge) | MATLAB / Simulink | DH analytical kinematic model, C2 continuous 5th-order spline joint trajectory interpolator (.slx model), and Yoshikawa manipulability tracking. |
| [Industrial LV Single-Line Diagram & Panel Layout](autocad/isletme-kuvvetli-akim-sld) | AutoCAD / DXF | 160 kVA factory single-line diagram (SLD), short-circuit & voltage drop calculations, selectivity notes, and 2000x2000 mm modular panel enclosure layout. |
| [Building Grounding & Lightning Protection (LPS)](autocad/bina-topraklama-ve-yildirimsavar) | AutoCAD / DXF | IEC 62305 Class II roof air-termination mesh, down-conductors, foundation/ring ground loop, and R < 1.0 Ohm earth resistance verification. |
| [CAN (TWAI) Distributed Sensor Node](gomulu-elektronik/can-twai-sensor-dugumu) | Embedded (ESP32) | 500 kbps CAN 2.0B vibration/temperature telemetry, packed payloads, error counters (TEC/REC), and automatic bus-off recovery state machine. |
| [Multi-Channel Thermocouple & Anti-Windup PID](gomulu-elektronik/cok-kanalli-termokupl-pid) | Embedded (ESP32) | MAX31856 SPI K-type thermocouple acquisition with cold-junction compensation and clamping anti-windup PID heater duty regulation. |
| [Corn Processing Plant MCC & VFD Control](autocad/misir-isleme-mcc-vfd) | AutoCAD / DWG | Corn mill & fan MCC power/control single-line diagram, Form 3b 4-bay enclosure layout (.dwg), and parametric voltage drop calculations. |
| [ESP32 Predictive Maintenance Node (PdM)](gomulu-elektronik/esp32-kestirimci-bakim) | Embedded (ESP32) | Bearing defect frequency analysis (BPFO/BPFI), Hilbert envelope demodulation, ISO 10816 vibration zones, and MCSA broken rotor bar detection. |
| [Li-Ion 2RC Battery Modeling & EKF SOC](matlab-simulink/li-ion-2rc-ekf-soc) | MATLAB / Energy | 18650 NMC 2RC Thevenin equivalent circuit model, HPPC pulsed current profile, and Extended Kalman Filter state-of-charge tracking. |
| [125 kHz EM4100 RFID Reader & Demodulator](haberlesme/rfid-125khz-em4100-okuyucu) | Communications / RF | 125 kHz LC resonant tank driver (Q=65), envelope detector, Manchester decoding C core, and KiCad schematic (.kicad_sch/.pdf). |

## About

**Hakan OĞUZ** — Electrical & Electronics Engineer
Focus areas: embedded systems, communications, robotics, power & control systems.

---
*New projects are added regularly.*
