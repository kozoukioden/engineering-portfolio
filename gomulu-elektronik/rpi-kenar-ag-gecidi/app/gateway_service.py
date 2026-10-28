"""
Author : Hakan OĞUZ - Elektrik Elektronik Mühendisi
Project: Raspberry Pi Kenar Ağ Geçidi (Modbus -> MQTT -> SQLite)
Date   : 2026-10-28
License: MIT
Desc   : Modbus RTU/TCP cihazlarından veri okuma, SQLite yerel arabellekleme (store-and-forward) ve MQTT yayıncısı
"""
import time
import json
import sqlite3
import random
import os

DB_PATH = "gateway_buffer.db"

class EdgeGateway:
    def __init__(self, db_file=DB_PATH):
        self.db_file = db_file
        self.init_database()
        self.mqtt_connected = False

    def init_database(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS telemetry_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    device_id TEXT,
                    tag_name TEXT,
                    value REAL,
                    status TEXT,
                    sent INTEGER DEFAULT 0
                )
            ''')
            conn.commit()

    def read_modbus_device(self, slave_id=1):
        """Modbus RTU/TCP cihazından gelen analog register okumasını simüle eder"""
        # Örnek: Giriş gerilimi (230 V), Akım (15 A), Sıcaklık (45 C)
        return {
            "timestamp": time.time(),
            "device_id": f"PLC_SLAVE_{slave_id}",
            "voltage_v": 230.0 + random.uniform(-2.5, 2.5),
            "current_a": 15.0 + random.uniform(-1.0, 1.0),
            "temperature_c": 45.0 + random.uniform(-0.5, 0.5)
        }

    def buffer_telemetry(self, data):
        """Bağlantı kopsa bile veriyi SQLite kuyruğuna kaydeder"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            ts = data["timestamp"]
            dev = data["device_id"]
            for tag, val in [("voltage", data["voltage_v"]), ("current", data["current_a"]), ("temp", data["temperature_c"])]:
                cursor.execute('''
                    INSERT INTO telemetry_queue (timestamp, device_id, tag_name, value, status, sent)
                    VALUES (?, ?, ?, ?, ?, 0)
                ''', (ts, dev, tag, val, "QUEUED"))
            conn.commit()

    def flush_queue_to_mqtt(self):
        """MQTT bağlantısı sağlandığında yerelde biriken kuyruktaki verileri sırayla iletir"""
        if not self.mqtt_connected:
            return 0

        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, timestamp, device_id, tag_name, value FROM telemetry_queue WHERE sent = 0 ORDER BY timestamp ASC LIMIT 50')
            rows = cursor.fetchall()
            
            sent_count = 0
            for r in rows:
                row_id, ts, dev, tag, val = r
                payload = json.dumps({"ts": ts, "device": dev, "tag": tag, "val": val})
                # Simüle edilmiş MQTT yayın: client.publish(f"factory/telemetry/{dev}", payload)
                cursor.execute('UPDATE telemetry_queue SET sent = 1, status = "TRANSMITTED" WHERE id = ?', (row_id,))
                sent_count += 1
            conn.commit()
            return sent_count

    def get_queue_size(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM telemetry_queue WHERE sent = 0')
            return cursor.fetchone()[0]
