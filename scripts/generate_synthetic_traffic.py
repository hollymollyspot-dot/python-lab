"""
Генератор синтетического датасета признаков сетевого трафика.
Имитирует признаки, извлекаемые при пассивном анализе TLS-сессий:
длина пакетов, направление, интервалы, энтропия.

Датасет используется для задачи классификации типов трафика
(HTTP/HTTPS/SSH/DNS/TLS 1.3) методами машинного обучения.
"""
import numpy as np
import pandas as pd
from pathlib import Path

def generate_traffic_data(n_samples=5000, seed=42):
    """
    Генерирует синтетический датасет признаков сетевого трафика.
    
    Параметры:
        n_samples: общее количество наблюдений
        seed: случайное зерно для воспроизводимости
    
    Возвращает:
        pd.DataFrame с признаками и метками классов
    """
    rng = np.random.default_rng(seed)
    
    protocols = ['HTTP', 'HTTPS', 'SSH', 'DNS', 'TLS1.3']
    n_per_class = n_samples // len(protocols)
    
    rows = []
    for proto in protocols:
        for i in range(n_per_class):
            # Признаки, типичные для пассивного анализа трафика
            if proto == 'HTTP':
                pkt_len_mean = rng.normal(512, 100)
                pkt_len_std = rng.normal(200, 50)
                direction_ratio = rng.normal(0.5, 0.1)  # симметричный трафик
                inter_arrival_mean = rng.normal(0.01, 0.005)
                entropy = rng.normal(6.5, 0.5)
                tls_handshake = 0
            elif proto == 'HTTPS':
                pkt_len_mean = rng.normal(1024, 200)
                pkt_len_std = rng.normal(400, 100)
                direction_ratio = rng.normal(0.3, 0.1)
                inter_arrival_mean = rng.normal(0.02, 0.01)
                entropy = rng.normal(7.8, 0.2)
                tls_handshake = 1
            elif proto == 'SSH':
                pkt_len_mean = rng.normal(256, 80)
                pkt_len_std = rng.normal(100, 30)
                direction_ratio = rng.normal(0.5, 0.05)
                inter_arrival_mean = rng.normal(0.05, 0.02)
                entropy = rng.normal(7.9, 0.1)
                tls_handshake = 1
            elif proto == 'DNS':
                pkt_len_mean = rng.normal(128, 40)
                pkt_len_std = rng.normal(50, 20)
                direction_ratio = rng.normal(0.5, 0.1)
                inter_arrival_mean = rng.normal(0.005, 0.002)
                entropy = rng.normal(5.5, 0.8)
                tls_handshake = 0
            else:  # TLS 1.3
                pkt_len_mean = rng.normal(1200, 300)
                pkt_len_std = rng.normal(500, 150)
                direction_ratio = rng.normal(0.4, 0.15)
                inter_arrival_mean = rng.normal(0.03, 0.015)
                entropy = rng.normal(7.95, 0.05)
                tls_handshake = 1
            
            rows.append({
                'protocol': proto,
                'pkt_len_mean': max(0, pkt_len_mean),
                'pkt_len_std': max(0, pkt_len_std),
                'direction_ratio': np.clip(direction_ratio, 0, 1),
                'inter_arrival_mean': max(0.001, inter_arrival_mean),
                'entropy': np.clip(entropy, 0, 8),
                'tls_handshake': tls_handshake,
                'n_packets': int(rng.integers(10, 1000)),
            })
    
    df = pd.DataFrame(rows)
    return df

if __name__ == '__main__':
    print("Генерация синтетического датасета...")
    df = generate_traffic_data(n_samples=5000, seed=42)
    
    out = Path('data/raw/traffic_features.csv')
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    
    print(f"✓ Сгенерировано {len(df)} записей")
    print(f"✓ Сохранено в {out}")
    print(f"✓ Размер файла: {out.stat().st_size / 1024:.1f} КБ")
    print(f"\nРаспределение классов:")
    print(df['protocol'].value_counts().to_string())