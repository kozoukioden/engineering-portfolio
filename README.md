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
| [EV Charging Hub Distribution & Dynamic Load Management](autocad/sarj-otoparki-dagitim) | AutoCAD / DWG | 20x 22kW AC + 4x 120kW DC fast chargers, 1000 kVA substation, 400x100mm cable tray layout, and DLM scheme (.dwg). |
| [Raspberry Pi Industrial Edge Gateway](gomulu-elektronik/rpi-kenar-ag-gecidi) | Embedded / Edge | Modbus RTU/TCP telemetry collector, local SQLite store-and-forward buffer, and MQTT cloud bridge with Docker support. |
| [EV PMSM Field Oriented Control (FOC) Drive](matlab-simulink/ev-pmsm-foc-surucu) | Simulink / Drive | 60 kW permanent magnet synchronous motor dq vector control, MTPA, cascade speed/current PI loops (.slx binary model). |
| [ESP32 BLE RSSI + IMU Indoor Positioning EKF](haberlesme/esp32-ble-rssi-imu-ekf) | Communications / RF | Log-distance path loss calibration, trilateration, and 4-state Extended Kalman Filter sensor fusion (RMSE: 1.42 m). |
| [34.5/0.4 kV 1600 kVA Substation & TCC Relay Protection](autocad/kompakt-trafo-merkezi) | AutoCAD / DWG | Prefabricated concrete kiosk layout, MV switchgear, transformer oil pit, and IEC 60255 IDMT relay coordination curves (.dwg). |
| [4th-Order Linkwitz-Riley Active Crossover & Bass Boost](gomulu-elektronik/aktif-crossover-bas-guclendirici) | Electronics / Analog | LR4 80 Hz low-pass, 20 Hz subsonic high-pass, 0-180 deg phase control, +6dB bass boost, KiCad schematic (.pdf/.kicad_sch/.kicad_pcb). |
| [PV Partial Shading Multi-Peak MPPT & PSO Optimization](matlab-simulink/pv-kismi-golgelenme-mppt) | MATLAB / Energy | 4-module bypass diode analytical multi-peak P-V curve, P&O local trap demonstration, and Particle Swarm Optimization (+32.5% energy gain). |
| [LoRa-like Chirp Spread Spectrum (CSS) Modem Core](haberlesme/lora-css-modem-matlab) | Communications / RF | From-scratch CSS chirp modulator, dechirp+FFT demodulator, AWGN BER-SNR curves, and 868 MHz Okumura-Hata urban link budget. |
| [Industrial Plant Lighting (EN 12464-1) & Emergency Route (EN 1838)](autocad/uretim-hali-aydinlatma) | AutoCAD / DWG | 60x24m factory hall 500 lux point-by-point lumen method, uniformity U0=0.74, 3h battery emergency exit routes, and AYP panel (.dwg). |
| [ESP32 12-Step Automatic Power Factor Controller (APFC)](gomulu-elektronik/esp32-kompanzasyon-rolesi) | Embedded / Power | 12-stage capacitor bank, rotational equal wear leveling, harmonic resonance detection (THD-V > 5%), and contactor lifecycle counter. |
| [6-DOF Quadrotor Flight Dynamics & Cascade PID Control](matlab-simulink/quadrotor-6dof-dinamik) | Simulink / Robotics | 6-DOF Newton-Euler flight model, inner attitude PD + outer position PID, wind gust rejection, and motor saturation (.slx binary model). |
| [2.45 GHz Microstrip Patch & Smart Antenna MVDR Beamforming](haberlesme/anten-dizisi-huzme-yonlendirme) | Communications / RF | Inset-fed microstrip patch analytical design, 8-element ULA array factor, Dolph-Chebyshev SLL, and MVDR -60 dB adaptive jammer nulling. |

## About

**Hakan OĞUZ** — Electrical & Electronics Engineer
Focus areas: embedded systems, communications, robotics, power & control systems.

---
*New projects are added regularly.*
