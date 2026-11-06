"""
Быстрая проверка сгенерированного датасета.
"""
import pandas as pd
from pathlib import Path

def main():
    csv_path = Path('data/raw/traffic_features.csv')
    if not csv_path.exists():
        print("❌ Файл не найден. Сначала запустите generate_synthetic_traffic.py")
        return
    
    df = pd.read_csv(csv_path)
    
    print("=" * 60)
    print("ИНСПЕКЦИЯ ДАТАСЕТА")
    print("=" * 60)
    print(f"Размер: {df.shape[0]} строк × {df.shape[1]} столбцов")
    print(f"\nПервые 5 строк:")
    print(df.head().to_string())
    print(f"\nСтатистика:")
    print(df.describe().to_string())
    print(f"\nПропущенные значения:")
    print(df.isnull().sum().to_string())
    print(f"\nТипы данных:")
    print(df.dtypes.to_string())

if __name__ == '__main__':
    main()