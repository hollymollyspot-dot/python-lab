"""
Замер времени сборки для стратегии 2 (mkdocs-jupyter).
"""
import time
import subprocess
from pathlib import Path

def measure_build():
    print("Очистка папки site/...")
    site_dir = Path('site')
    if site_dir.exists():
        import shutil
        shutil.rmtree(site_dir)
    
    print("Запуск mkdocs build --strict...")
    start = time.perf_counter()
    result = subprocess.run(
        ['mkdocs', 'build', '--strict'],
        capture_output=True,
        text=True
    )
    end = time.perf_counter()
    
    elapsed = end - start
    
    if result.returncode == 0:
        print(f"✓ Сборка успешна")
        print(f"✓ Время сборки: {elapsed:.3f} с")
        
        total_size = sum(f.stat().st_size for f in site_dir.rglob('*') if f.is_file())
        print(f"✓ Размер site/: {total_size / 1024:.1f} КБ")
    else:
        print(f"❌ Ошибка сборки:")
        print(result.stderr)
    
    return elapsed

if __name__ == '__main__':
    print("=" * 60)
    print("ЗАМЕР ВРЕМЕНИ СБОРКИ (СТРАТЕГИЯ 2: mkdocs-jupyter)")
    print("=" * 60)
    
    times = []
    for i in range(3):
        print(f"\nЗапуск {i+1}/3:")
        t = measure_build()
        times.append(t)
    
    avg_time = sum(times) / len(times)
    print(f"\n{'='*60}")
    print(f"СРЕДНЕЕ ВРЕМЯ СБОРКИ: {avg_time:.3f} с")
    print(f"{'='*60}")