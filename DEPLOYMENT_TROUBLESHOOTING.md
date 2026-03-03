# Deployment Troubleshooting Guide

Проблемы, возникающие при развёртывании и обновлении сервера, и способы их решения.

---

## Содержание

1. [Git: "dubious ownership in repository"](#1-git-dubious-ownership-in-repository)
2. [Git pull: конфликты слияния](#2-git-pull-конфликты-слияния)
3. [Systemctl: сервис не запускается](#3-systemctl-сервис-не-запускается)
4. [Port 8000 already in use](#4-port-8000-already-in-use)
5. [ModuleNotFoundError после обновления](#5-modulenotfounderror-после-обновления)
6. [Database migration issues](#6-database-migration-issues)
7. [Firewall: недоступен порт 8000](#7-firewall-недоступен-порт-8000)

---

## 1. Git: "dubious ownership in repository"

### Симптом
```bash
$ git pull
fatal: detected dubious ownership in repository at '/opt/file-exchanger'
```

### Причина
Git обнаружил, что директория репозитория принадлежит другому пользователю (не root). Это защита от несанкционированного доступа.

### Решение

**Вариант A: Исправить владельца (рекомендуется)**
```bash
sudo chown -R root:root /opt/file-exchanger
```

**Вариант B: Добавить путь в безопасные директории**
```bash
git config --global --add safe.directory /opt/file-exchanger
```

**Вариант C: Если сервис работает от www-data**
```bash
sudo chown -R www-data:www-data /opt/file-exchanger
```

### Проверка
```bash
ls -la /opt/ | grep file-exchanger
```

---

## 2. Git pull: конфликты слияния

### Симптом
```bash
$ git pull
CONFLICT (content): Merge conflict in server/routes/users.py
Automatic merge failed; fix conflicts and then commit the result.
```

### Причина
Локальные файлы были изменены вручную и конфликтуют с изменениями из GitHub.

### Решение

**Вариант A: Отменить слияние и принять версию из GitHub**
```bash
cd /opt/file-exchanger
git merge --abort
git fetch origin
git reset --hard origin/master
systemctl restart file-exchanger
```

**Вариант B: Принять локальные изменения**
```bash
cd /opt/file-exchanger
git checkout --ours .
git add .
git commit -m "Keep local changes"
git pull
systemctl restart file-exchanger
```

**Вариант C: Ручное разрешение конфликтов**
```bash
cd /opt/file-exchanger
# Откройте файлы с конфликтами в редакторе
nano server/routes/users.py
# Найдите маркеры конфликтов <<<<<<<, =======, >>>>>>>
# Отредактируйте файл, оставив нужный код
git add .
git commit -m "Resolve merge conflicts"
systemctl restart file-exchanger
```

### Профилактика
Не редактируйте файлы напрямую на сервере. Все изменения вносите через GitHub.

---

## 3. Systemctl: сервис не запускается

### Симптом
```bash
$ systemctl start file-exchanger
Job for file-exchanger.service failed because the control process exited with error code.
```

### Диагностика
```bash
# Проверка статуса
systemctl status file-exchanger --no-pager

# Просмотр логов
journalctl -u file-exchanger -n 50 --no-pager

# Проверка конфигурации сервиса
cat /etc/systemd/system/file-exchanger.service
```

### Частые причины и решения

**A. Неправильный путь к Python**
```ini
# В file-exchanger.service проверьте ExecStart
ExecStart=/opt/file-exchanger/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**B. Отсутствуют зависимости**
```bash
cd /opt/file-exchanger
/opt/file-exchanger/venv/bin/pip install -r server/requirements.txt
systemctl restart file-exchanger
```

**C. Ошибка в коде (SyntaxError, ImportError)**
```bash
# Проверка синтаксиса
/opt/file-exchanger/venv/bin/python -m py_compile server/main.py

# Запуск вручную для отладки
cd /opt/file-exchanger/server
../venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**D. Неправильные права доступа**
```bash
chmod -R 755 /opt/file-exchanger
chown -R www-data:www-data /opt/file-exchanger/server/storage
systemctl restart file-exchanger
```

---

## 4. Port 8000 already in use

### Симптом
```bash
$ journalctl -u file-exchanger -n 20
OSError: [Errno 98] Address already in use
```

### Причина
Порт 8000 занят другим процессом.

### Решение
```bash
# Найти процесс на порту 8000
sudo lsof -i :8000
# или
sudo netstat -tulpn | grep 8000

# Убить процесс
sudo kill -9 <PID>

# Или остановить все uvicorn процессы
sudo pkill -f uvicorn

# Перезапустить сервис
systemctl restart file-exchanger
```

### Профилактика
Убедитесь, что только один экземпляр сервиса запущен:
```bash
systemctl stop file-exchanger
systemctl start file-exchanger
```

---

## 5. ModuleNotFoundError после обновления

### Симптом
```bash
$ journalctl -u file-exchanger -n 20
ModuleNotFoundError: No module named 'fastapi'
```

### Причина
После `git pull` появились новые зависимости в `requirements.txt`.

### Решение
```bash
cd /opt/file-exchanger
/opt/file-exchanger/venv/bin/pip install --upgrade pip
/opt/file-exchanger/venv/bin/pip install -r server/requirements.txt
systemctl restart file-exchanger
```

### Проверка установленных пакетов
```bash
/opt/file-exchanger/venv/bin/pip list | grep -E "fastapi|uvicorn|sqlalchemy"
```

---

## 6. Database migration issues

### Симптом
```bash
$ journalctl -u file-exchanger -n 20
sqlalchemy.exc.OperationalError: no such table: users
```

### Причина
База данных не создана или отсутствует миграция.

### Решение

**A. Создание базы данных с нуля**
```bash
cd /opt/file-exchanger/server
# Остановите сервис
systemctl stop file-exchanger

# Удалите старую БД (если есть)
rm -f file_exchanger.db

# Запустите сервер для создания БД
../venv/bin/python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

# Запустите сервис
systemctl start file-exchanger
```

**B. Проверка существования таблиц**
```bash
cd /opt/file-exchanger/server
../venv/bin/python -c "
from database import SessionLocal
from models import User, PendingFile
db = SessionLocal()
print('Users:', db.query(User).count())
print('Files:', db.query(PendingFile).count())
db.close()
"
```

**C. Создание администратора по умолчанию**
```bash
cd /opt/file-exchanger/server
../venv/bin/python -c "
from database import SessionLocal
from models import User
from auth import hash_password

db = SessionLocal()
admin = User(
    username='admin',
    password_hash=hash_password('admin'),
    is_admin=True,
    force_change_password=True
)
db.add(admin)
db.commit()
db.close()
print('Admin user created')
"
```

---

## 7. Firewall: недоступен порт 8000

### Симптом
```bash
$ curl http://localhost:8000/health
{"status":"ok"}

# Но с внешнего IP:
$ curl http://<SERVER_IP>:8000/health
curl: (7) Failed to connect to <SERVER_IP> port 8000: Connection refused
```

### Причина
Порт 8000 заблокирован фаерволом или security group облачного провайдера.

### Решение

**A. Проверка UFW**
```bash
# Статус фаервола
sudo ufw status

# Если порт 8000 не открыт
sudo ufw allow 8000/tcp
sudo ufw reload
sudo ufw status
```

**B. Проверка security group (для облачных серверов)**

Для AWS, DigitalOcean, Hetzner и др.:
1. Зайдите в панель управления хостингом
2. Найдите раздел "Firewall" или "Security Groups"
3. Добавьте правило: TCP, порт 8000, источник 0.0.0.0/0

**C. Проверка iptables**
```bash
sudo iptables -L -n | grep 8000
```

---

## Быстрая диагностика: полный чеклист

```bash
# 1. Проверка владельца репозитория
ls -la /opt/ | grep file-exchanger

# 2. Проверка git статуса
cd /opt/file-exchanger && git status

# 3. Проверка сервиса
systemctl status file-exchanger --no-pager

# 4. Проверка логов
journalctl -u file-exchanger -n 30 --no-pager

# 5. Проверка порта
sudo lsof -i :8000

# 6. Проверка фаервола
sudo ufw status

# 7. Проверка зависимостей
/opt/file-exchanger/venv/bin/pip list | head -20

# 8. Проверка БД
ls -la /opt/file-exchanger/server/*.db
```

---

## Контакты и ресурсы

- **GitHub Repository:** https://github.com/buchgit/file-exchanger
- **Логи сервера:** `journalctl -u file-exchanger -f`
- **Статус сервиса:** `systemctl status file-exchanger`

---

## История изменений документа

| Дата | Изменение |
|------|-----------|
| 2026-03-04 | Добавлены решения для git pull проблем |
| 2026-03-04 | Добавлена секция про dubious ownership |
| 2026-03-04 | Добавлен полный чеклист диагностики |
