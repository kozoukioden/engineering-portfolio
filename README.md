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

## About

**Hakan OĞUZ** — Electrical & Electronics Engineer
Focus areas: embedded systems, communications, robotics, power & control systems.

---
*New projects are added regularly.*
