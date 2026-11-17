"""
Воспроизводимый конвейер: данные → результат → артефакты для сайта.
Стратегия 4: отдельный скрипт с кэшированием по хешу входных данных.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib
matplotlib.use('Agg')  # Важно для headless-среды (CI/CD)
import matplotlib.pyplot as plt
import seaborn as sns

# Пути
ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw" / "traffic_features.csv"
DATA_PROC = ROOT / "data" / "processed"
ASSETS = ROOT / "docs" / "assets" / "auto"


def file_hash(path: Path) -> str:
    """Вычисляет SHA-256 хеш файла для отслеживания изменений."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def load_cache(cache_path: Path) -> dict | None:
    if cache_path.exists():
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_cache(cache_path: Path, data: dict):
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_experiment(data_hash: str, force: bool = False):
    """Основной эксперимент: обучение RF на признаках трафика."""
    cache_path = DATA_PROC / f"cache_{data_hash[:12]}.json"
    
    # 1. Проверка кэша
    if not force:
        cached = load_cache(cache_path)
        if cached:
            print(f"[CACHE HIT] Используем кэш для хеша {data_hash[:12]}")
            return cached
    
    print(f"[CACHE MISS] Выполняем эксперимент для хеша {data_hash[:12]}")
    t0 = time.perf_counter()
    
    # 2. Загрузка данных
    df = pd.read_csv(DATA_RAW)
    feature_cols = ['pkt_len_mean', 'pkt_len_std', 'direction_ratio', 
                    'inter_arrival_mean', 'entropy', 'tls_handshake', 'n_packets']
    X = df[feature_cols]
    y = df['protocol']
    
    # 3. Разделение и обучение
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    clf.fit(X_train, y_train)
    
    # 4. Метрики
    y_pred = clf.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    cv_scores = cross_val_score(clf, X, y, cv=5, scoring='f1_weighted')
    
    elapsed = time.perf_counter() - t0
    
    # 5. Генерация артефактов
    ASSETS.mkdir(parents=True, exist_ok=True)
    DATA_PROC.mkdir(parents=True, exist_ok=True)
    
    # 5.1. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred, labels=clf.classes_)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=clf.classes_, yticklabels=clf.classes_, ax=ax)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    ax.set_title('Confusion Matrix — Traffic Classification')
    fig.tight_layout()
    fig.savefig(ASSETS / 'confusion_matrix.png', dpi=150)
    plt.close(fig)
    
    # 5.2. Feature Importance
    importances = clf.feature_importances_
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=importances, y=feature_cols, ax=ax, palette='viridis', hue=feature_cols, legend=False)    
    ax.set_title('Feature Importance (Random Forest)')
    ax.set_xlabel('Importance')
    fig.tight_layout()
    fig.savefig(ASSETS / 'feature_importance.png', dpi=150)
    plt.close(fig)
    
    # 5.3. Таблица метрик в Markdown
    md_table = "| Протокол | Precision | Recall | F1 | Support |\n"
    md_table += "|----------|-----------|--------|-----|---------|\n"
    for proto in sorted(report.keys()):
        if proto in ('accuracy', 'macro avg', 'weighted avg'):
            continue
        r = report[proto]
        md_table += f"| {proto} | {r['precision']:.3f} | {r['recall']:.3f} | {r['f1-score']:.3f} | {int(r['support'])} |\n"
    md_table += f"| **Weighted avg** | {report['weighted avg']['precision']:.3f} | {report['weighted avg']['recall']:.3f} | {report['weighted avg']['f1-score']:.3f} | {int(report['weighted avg']['support'])} |\n"
    
    (ASSETS / 'metrics_table.md').write_text(md_table, encoding='utf-8')
    
    # 5.4. Сводный JSON (метаданные)
    result = {
        'data_hash': data_hash,
        'accuracy': report['accuracy'],
        'f1_weighted': report['weighted avg']['f1-score'],
        'cv_f1_mean': float(cv_scores.mean()),
        'cv_f1_std': float(cv_scores.std()),
        'elapsed_seconds': round(elapsed, 3),
        'n_samples': len(df),
        'n_features': len(feature_cols),
        'timestamp': pd.Timestamp.now('UTC').isoformat(),
    }
    save_cache(cache_path, result)
    save_cache(DATA_PROC / 'latest.json', result)
    
    print(f"✓ Готово за {elapsed:.3f} с. Accuracy={result['accuracy']:.3f}, F1={result['f1_weighted']:.3f}")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help='Игнорировать кэш и пересчитать')
    args = parser.parse_args()
    
    if not DATA_RAW.exists():
        print(f"❌ Ошибка: файл данных не найден: {DATA_RAW}")
        print("Сначала запустите: python scripts/generate_synthetic_traffic.py")
        return
    
    data_hash = file_hash(DATA_RAW)
    run_experiment(data_hash, force=args.force)


if __name__ == '__main__':
    main()