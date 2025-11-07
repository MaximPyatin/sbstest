# Инструкция по Push в Git

## Шаг 1: Добавить файлы в индекс

```bash
git add .
```

Или выборочно:
```bash
git add .gitignore
git add README.md
git add alembic.ini
git add alembic/
git add app/
git add docker-compose.yml
git add entrypoint.py
git add requirements.txt
```

## Шаг 2: Проверить, что будет закоммичено

```bash
git status
```

## Шаг 3: Создать первый коммит

```bash
git commit -m "Initial commit: Setup PostgreSQL 18 + Alembic migrations"
```

## Шаг 4: Настроить удаленный репозиторий

### Вариант А: GitHub

1. Создайте репозиторий на GitHub (https://github.com)
2. Скопируйте URL репозитория (например: `https://github.com/username/repo-name.git`)
3. Добавьте remote:

```bash
git remote add origin https://github.com/username/repo-name.git
```

### Вариант Б: GitLab

```bash
git remote add origin https://gitlab.com/username/repo-name.git
```

### Вариант В: Другой Git-сервер

```bash
git remote add origin <URL_вашего_репозитория>
```

## Шаг 5: Проверить remote

```bash
git remote -v
```

## Шаг 6: Push в удаленный репозиторий

### Первый push (создание ветки):

```bash
git push -u origin master
```

Или если используется `main`:

```bash
git branch -M main
git push -u origin main
```

### Последующие push:

```bash
git push
```

## Проверка результата

После успешного push проверьте на сайте вашего Git-хостинга, что все файлы загружены.

---

## Быстрая команда (если уже настроен remote):

```bash
git add .
git commit -m "Initial commit: Setup PostgreSQL 18 + Alembic migrations"
git push -u origin master
```

---

## Важно!

⚠️ **Перед push убедитесь:**
- ✅ `.gitignore` настроен правильно (venv/, __pycache__/ исключены)
- ✅ Нет чувствительных данных (пароли, ключи) в коде
- ✅ Все необходимые файлы добавлены

## Текущий статус файлов:

- ✅ `.gitignore` - создан
- ✅ `README.md` - документация
- ✅ `requirements.txt` - зависимости
- ✅ `docker-compose.yml` - PostgreSQL конфигурация
- ✅ `alembic.ini` - конфигурация Alembic
- ✅ `alembic/` - директория миграций
- ✅ `app/` - код приложения
- ✅ `entrypoint.py` - скрипт авто-миграций

Все готово к коммиту! 🚀

