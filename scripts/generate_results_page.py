"""
Генерирует docs/results.md из артефактов эксперимента.
Включает метки версии: хеш коммита, дата сборки, версия датасета.
"""
import subprocess
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent

def git_hash() -> str:
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=ROOT, text=True
        ).strip()
    except Exception:
        return 'unknown'

def git_date() -> str:
    try:
        return subprocess.check_output(
            ['git', 'log', '-1', '--format=%ci'],
            cwd=ROOT, text=True
        ).strip()
    except Exception:
        return 'unknown'

def main():
    latest = ROOT / 'data' / 'processed' / 'latest.json'
    if not latest.exists():
        print("❌ Нет результатов эксперимента. Сначала запустите run_experiment.py")
        return
    
    res = json.loads(latest.read_text(encoding='utf-8'))
    metrics_md = (ROOT / 'docs' / 'assets' / 'auto' / 'metrics_table.md').read_text(encoding='utf-8')
    
    page = f"""# Результаты эксперимента (P3: Автоматический конвейер)

!!! warning "Происхождение данных"
    Синтетический учебный набор, {res['n_samples']} наблюдений. Эти числа не являются замером реальной системы.

## Методика

Для классификации типов сетевого трафика (HTTP/HTTPS/SSH/DNS/TLS1.3) по статистическим признакам пакетов использован классификатор **Random Forest** (100 деревьев, max_depth=10).

Метрики вычислены на тестовой выборке (20%) и через 5-кратную кросс-валидацию.

## График и таблица

![Confusion Matrix](assets/auto/confusion_matrix.png)

![Feature Importance](assets/auto/feature_importance.png)

{metrics_md}

CV F1 (5-fold): **{res['cv_f1_mean']:.3f} ± {res['cv_f1_std']:.3f}**

## Артефакты и версия

| Поле | Значение |
|------|----------|
| Хеш коммита | `{git_hash()}` |
| Дата коммита | {git_date()} |
| Дата сборки | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} |
| Хеш датасета (SHA-256) | `{res['data_hash']}` |
| Объём выборки | {res['n_samples']} |
| Время расчёта | {res['elapsed_seconds']} с |
| Accuracy | {res['accuracy']:.4f} |
| F1 (weighted) | {res['f1_weighted']:.4f} |
"""
    (ROOT / 'docs' / 'results.md').write_text(page, encoding='utf-8')
    print(f"✓ Сгенерирована страница docs/results.md (commit={git_hash()})")


if __name__ == '__main__':
    main()