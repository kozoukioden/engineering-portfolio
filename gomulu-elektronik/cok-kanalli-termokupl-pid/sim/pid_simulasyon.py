"""
Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
Project: Çok Kanallı Termokupl Veri Toplama ve PID Isı Kontrolü
Date   : 2026-10-26
License: MIT
Desc   : Termal sistem diferansiyel denklem simülasyonu, anti-windup PID basamak yanıtı ve MAX31856 doğrulama
"""
import os
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SEK  = os.path.abspath(os.path.join(HERE, "..", "sekiller"))

def max31856_raw_to_celsius(b0, b1, b2):
    raw = (b0 << 16) | (b1 << 8) | b2
    raw >>= 5
    if b0 & 0x80:
        raw -= (1 << 19)
    return raw * 0.0078125

def test_sensor_conversion():
    # 100.0 °C doğrulaması -> raw = 100 / 0.0078125 = 12800 -> 12800 << 5 = 409600 (0x064000)
    # b0 = 0x06, b1 = 0x40, b2 = 0x00
    temp_calc = max31856_raw_to_celsius(0x06, 0x40, 0x00)
    assert abs(temp_calc - 100.0) < 1e-4, f"Sensor conversion mismatch: {temp_calc}"
    print(f"MAX31856 Dönüşüm Doğrulandı: 0x064000 -> {temp_calc:.4f} °C")

class AntiWindupPID:
    def __init__(self, kp, ki, kd, dt, out_min=0.0, out_max=100.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt
        self.out_min = out_min
        self.out_max = out_max
        self.integral = 0.0
        self.prev_measurement = 0.0

    def compute(self, setpoint, measurement):
        error = setpoint - measurement
        p_term = self.kp * error
        self.integral += error * self.dt
        d_term = -self.kd * (measurement - self.prev_measurement) / self.dt
        
        raw_out = p_term + (self.ki * self.integral) + d_term
        
        # Clamping anti-windup
        out = raw_out
        if raw_out > self.out_max:
            out = self.out_max
            if error > 0:
                self.integral -= error * self.dt
        elif raw_out < self.out_min:
            out = self.out_min
            if error < 0:
                self.integral -= error * self.dt
                
        self.prev_measurement = measurement
        return out

def run_thermal_simulation():
    os.makedirs(SEK, exist_ok=True)
    test_sensor_conversion()

    # Birinci dereceden gecikmeli ısıtıcı modeli:
    # dT/dt = (1/tau) * (k_plant * Duty - (T - T_amb))
    tau_plant = 45.0    # Termal zaman sabiti [s] (termal kütle)
    k_plant   = 2.2     # Isıtıcı kazancı [°C / %PWM] -> %100 PWM ile ortam üstü ~220 °C artış
    T_amb     = 25.0    # Ortam sıcaklığı [°C]
    dt        = 0.5     # Kontrol adımı [s]
    total_time = 300.0  # Toplam simülasyon süresi [s] (5 dakika)

    steps = int(total_time / dt)
    t_vec = [i * dt for i in range(steps)]

    # Hedef Profil: t=0..150s: 180 °C, t=150s..300s: 210 °C
    sp_vec = [180.0 if t < 150.0 else 210.0 for t in t_vec]

    pid = AntiWindupPID(kp=3.5, ki=0.08, kd=1.5, dt=dt, out_min=0.0, out_max=100.0)

    T_curr = T_amb
    temp_history = []
    pwm_history  = []

    for i in range(steps):
        sp = sp_vec[i]
        duty = pid.compute(sp, T_curr)
        
        # Termal durum güncellemesi (Euler)
        dT = (1.0 / tau_plant) * (k_plant * duty - (T_curr - T_amb)) * dt
        T_curr += dT
        
        temp_history.append(T_curr)
        pwm_history.append(duty)

    # 1. Grafik: PID Sıcaklık Takibi ve Setpoint Yanıtı
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t_vec, sp_vec, 'r--', label='Hedef Sıcaklık (Setpoint) [°C]')
    plt.plot(t_vec, temp_history, 'b-', linewidth=1.8, label='Ölçülen Sıcaklık (K-Tipi) [°C]')
    plt.axhline(220.0, color='m', linestyle=':', label='Emniyet Kesme Eşiği (220 °C)')
    plt.grid(True)
    plt.ylabel('Sıcaklık [°C]')
    plt.title('K-Tipi Termokupl PID Isı Kontrolü Basamak Yanıtı (Hakan OĞUZ)')
    plt.legend(loc='lower right')

    plt.subplot(2, 1, 2)
    plt.plot(t_vec, pwm_history, 'g-', linewidth=1.5, label='Isıtıcı PWM Çıkışı [%]')
    plt.grid(True)
    plt.xlabel('Zaman [s]')
    plt.ylabel('PWM [%]')
    plt.ylim(-5, 105)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(SEK, "pid_sicaklik_yaniti.png"), dpi=150)
    plt.close()

    # 2. Grafik: 4 Kanal Veri Toplama Karşılaştırması
    ch_offsets = [0.0, -12.0, 8.0, -22.0] # Farklı bölgelerin sıcaklık gradyantı
    plt.figure(figsize=(10, 5))
    for ch in range(4):
        ch_temps = [T + ch_offsets[ch] for T in temp_history]
        plt.plot(t_vec, ch_temps, label=f'Kanal {ch+1} (MAX31856 Zone {ch+1})')
    plt.grid(True)
    plt.xlabel('Zaman [s]')
    plt.ylabel('Sıcaklık [°C]')
    plt.title('4 Kanallı Termokupl Proses İzleme Profili')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(SEK, "cok_kanalli_termokupl_izleme.png"), dpi=150)
    plt.close()

    print("PID ısı simülasyon grafikleri sekiller/ dizinine kaydedildi.")

if __name__ == "__main__":
    run_thermal_simulation()
