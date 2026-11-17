"""
Оркестратор задач для воспроизводимого конвейера.
Заменяет Makefile на Windows-дружелюбный Python-инструмент.
"""
import nox

# Глобальная настройка: переиспользовать существующие виртуальные окружения
nox.options.reuse_existing_virtualenvs = True 

import shutil
from pathlib import Path

@nox.session
def data(session):
    """Генерация синтетических данных."""
    session.install("-r", "requirements.txt")
    session.run("python", "scripts/generate_synthetic_traffic.py")

@nox.session
def calc(session):
    """Выполнение эксперимента (с кэшированием)."""
    session.install("-r", "requirements.txt")
    session.run("python", "scripts/run_experiment.py")

@nox.session
def calc_force(session):
    """Выполнение эксперимента без кэша (принудительный пересчёт)."""
    session.install("-r", "requirements.txt")
    session.run("python", "scripts/run_experiment.py", "--force")

@nox.session
def page(session):
    """Генерация Markdown-страницы результатов."""
    session.install("-r", "requirements.txt")
    session.run("python", "scripts/generate_results_page.py")

@nox.session
def build(session):
    """Полная сборка: данные → эксперимент → страница → MkDocs."""
    session.install("-r", "requirements.txt")
    session.run("python", "scripts/generate_synthetic_traffic.py")
    session.run("python", "scripts/run_experiment.py")
    session.run("python", "scripts/generate_results_page.py")
    session.run("python", "-m", "mkdocs", "build", "--strict")

@nox.session
def serve(session):
    """Локальный предпросмотр сайта."""
    session.install("-r", "requirements.txt")
    session.run("python", "-m", "mkdocs", "serve")

@nox.session
def clean(session):
    """Очистка артефактов и кэша."""
    for p in ['site', 'data/processed', 'docs/assets/auto', '.nox']:
        pp = Path(p)
        if pp.exists():
            shutil.rmtree(pp)
            print(f"✓ Удалено: {p}")