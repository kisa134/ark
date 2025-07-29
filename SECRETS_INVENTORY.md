# Инвентаризация API-ключей и секретов - Ark Project

## 📊 Обзор секретов

**Дата создания**: 2025-01-26  
**Версия**: v2.2  
**Статус**: Актуально  

### Статистика
- **Всего секретов**: 13 (загружено)
- **Здоровых секретов**: 13
- **Поврежденных секретов**: 0
- **Файл секретов**: secrets.env
- **Права доступа**: 600 (безопасно)

---

## 🔑 LLM API Секреты

### Ollama (Локальный LLM)
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| LLM API (Ollama) | Для локального LLM (Mistral/Llama) | `OLLAMA_API_KEY` | `ollama` (если есть локальная авторизация) |
| LLM Endpoint | Для http-интеграции Ollama локально | `ARK_MAIN_MIND_API_BASE` | `http://localhost:11434/v1` (по умолчанию) |
| LLM Model | Модель для сознания | `ARK_MAIN_MIND_MODEL` | `mistral:latest` (по умолчанию) |

### OpenAI (Fallback)
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| OpenAI | Fallback на внешний API | `OPENAI_API_KEY` | `sk-...` (если понадобится) |
| OpenAI Base | API endpoint | `OPENAI_API_BASE` | `https://api.openai.com/v1` |
| OpenAI Org | Организация | `OPENAI_ORGANIZATION` | `org-...` |

### Anthropic (Fallback)
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Anthropic | Fallback на Claude | `ANTHROPIC_API_KEY` | `sk-ant-...` |

### Google AI (Fallback)
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Google AI | Fallback на Gemini | `GOOGLE_API_KEY` | `AIza...` |
| Google Credentials | Service account | `GOOGLE_APPLICATION_CREDENTIALS` | Путь к JSON файлу |

### Cohere (Fallback)
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Cohere | Fallback на Cohere | `COHERE_API_KEY` | `...` |

---

## 🚀 Deployment & Git Секреты

### SSH & Git Access
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| GitHub SSH | Операции с репозиторием, автопуш и PR | `ARK_DEPLOY_KEY_PATH` | `/home/a0/.ssh/ark_deploy_key` |
| GitHub passphrase | Пароль к SSH ключу | `ARK_DEPLOY_KEY_PASSPHRASE` | — |
| Git Repository | URL репозитория | `GIT_REPO_URL` | `https://github.com/user/ark.git` |
| Git Username | Имя пользователя Git | `GIT_USERNAME` | `ark-bot` |
| GitHub Token | Personal Access Token | `GIT_PERSONAL_ACCESS_TOKEN` | `ghp_...` |

### Docker (если понадобится)
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Docker Registry | URL registry | `DOCKER_REGISTRY_URL` | `registry.example.com` |
| Docker Username | Имя пользователя | `DOCKER_USERNAME` | `ark-deploy` |
| Docker Password | Пароль | `DOCKER_PASSWORD` | — |

---

## 🗄️ Database & Storage Секреты

### SQLite Database
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| База данных | Путь к SQLite (.db) | `ARK_DB_PATH` | `./data/ark_memory.db` |
| Database Encryption | Ключ шифрования БД | `ARK_DB_ENCRYPTION_KEY` | — |

### PostgreSQL (если миграция)
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| PostgreSQL Host | Хост БД | `POSTGRES_HOST` | `localhost` |
| PostgreSQL Port | Порт БД | `POSTGRES_PORT` | `5432` |
| PostgreSQL Database | Имя БД | `POSTGRES_DB` | `ark_consciousness` |
| PostgreSQL User | Пользователь БД | `POSTGRES_USER` | `ark_user` |
| PostgreSQL Password | Пароль БД | `POSTGRES_PASSWORD` | — |

### Redis (если кэширование)
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Redis Host | Хост Redis | `REDIS_HOST` | `localhost` |
| Redis Port | Порт Redis | `REDIS_PORT` | `6379` |
| Redis Password | Пароль Redis | `REDIS_PASSWORD` | — |
| Redis Database | Номер БД | `REDIS_DB` | `0` |

---

## 🔐 Authentication & Security Секреты

### JWT & API Authentication
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| JWT Signing Key | Подпись JWT токенов | `JWT_SECRET_KEY` | — |
| API Secret Key | Секрет для API | `API_SECRET_KEY` | — |

### Encryption Keys
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| System Encryption | 32-байтовый ключ | `ENCRYPTION_KEY_32` | — |
| System Encryption | 64-байтовый ключ | `ENCRYPTION_KEY_64` | — |
| Consciousness Encryption | Шифрование сознания | `CONSCIOUSNESS_ENCRYPTION_KEY` | — |
| Memory Encryption | Шифрование памяти | `MEMORY_ENCRYPTION_KEY` | — |

### Security Monitoring
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Security Webhook | Уведомления о безопасности | `SECURITY_WEBHOOK_URL` | — |
| Intrusion Detection | Токен детекции вторжений | `INTRUSION_DETECTION_TOKEN` | — |
| Audit Log Encryption | Шифрование логов аудита | `AUDIT_LOG_ENCRYPTION_KEY` | — |
| Audit Webhook | Webhook для аудита | `AUDIT_WEBHOOK_URL` | — |

---

## 🌐 Web & Communication Секреты

### Web Interfaces
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Streamlit/Web | Порт для веб-интерфейса | `ARK_STREAMLIT_PORT` | `8501` |
| Local API | Порт локального API | `ARK_LOCAL_API_PORT` | `8080` |

### Communication Webhooks
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Discord Bot | Уведомления Discord | `DISCORD_WEBHOOK_URL` | — |
| Slack Integration | Уведомления Slack | `SLACK_WEBHOOK_URL` | — |
| Telegram Bot | Токен бота Telegram | `TELEGRAM_BOT_TOKEN` | — |
| Telegram Chat | ID чата Telegram | `TELEGRAM_CHAT_ID` | — |

### Email Configuration
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| SMTP Host | SMTP сервер | `SMTP_HOST` | — |
| SMTP Port | Порт SMTP | `SMTP_PORT` | `587` |
| SMTP Username | Пользователь SMTP | `SMTP_USERNAME` | — |
| SMTP Password | Пароль SMTP | `SMTP_PASSWORD` | — |
| Email From | Отправитель | `EMAIL_FROM` | — |
| Email To | Получатель | `EMAIL_TO` | — |

---

## ☁️ Cloud & External Services

### AWS (если используется)
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| AWS Access Key | Access Key ID | `AWS_ACCESS_KEY_ID` | — |
| AWS Secret Key | Secret Access Key | `AWS_SECRET_ACCESS_KEY` | — |
| AWS Region | Регион AWS | `AWS_REGION` | `us-east-1` |
| AWS S3 Bucket | S3 bucket | `AWS_S3_BUCKET` | — |

### Google Cloud (если используется)
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Google Cloud Project | ID проекта | `GOOGLE_CLOUD_PROJECT` | — |
| Google Cloud Credentials | Путь к credentials | `GOOGLE_CLOUD_CREDENTIALS` | — |

### Azure (если используется)
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Azure Subscription | ID подписки | `AZURE_SUBSCRIPTION_ID` | — |
| Azure Tenant | ID tenant | `AZURE_TENANT_ID` | — |
| Azure Client | Client ID | `AZURE_CLIENT_ID` | — |
| Azure Secret | Client Secret | `AZURE_CLIENT_SECRET` | — |

### Monitoring Services
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Sentry DSN | Мониторинг ошибок | `SENTRY_DSN` | — |
| Logtail Token | Логирование | `LOGTAIL_TOKEN` | — |
| Datadog API | Метрики | `DATADOG_API_KEY` | — |

---

## 🔄 Evolution & Self-Modification

### Evolution Tokens
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Evolution Approval | Токен одобрения эволюции | `EVOLUTION_APPROVAL_TOKEN` | — |
| Self Modification | Ключ самомодификации | `SELF_MODIFICATION_KEY` | — |

### Backup & Recovery
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Backup Encryption | Ключ шифрования бэкапов | `BACKUP_ENCRYPTION_KEY` | — |
| Backup Passphrase | Пароль бэкапов | `BACKUP_PASSPHRASE` | — |
| Recovery Token Primary | Основной токен восстановления | `RECOVERY_TOKEN_PRIMARY` | — |
| Recovery Token Secondary | Вторичный токен восстановления | `RECOVERY_TOKEN_SECONDARY` | — |

---

## 🏛️ System Configuration

### Sanctuary & System
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Sanctuary Name | Имя святилища | `ARK_SANCTUARY_NAME` | `sanctuary_01` |
| Sanctuary ID | ID святилища | `ARK_SANCTUARY_ID` | `ark_sanctuary_01` |
| System Limits | Максимальная память | `ARK_MAX_MEMORY_MB` | `2048` |
| System Limits | Максимальный CPU | `ARK_MAX_CPU_PERCENT` | `80` |
| System Limits | Максимальная температура | `ARK_MAX_TEMP_CELSIUS` | `85` |

### Consciousness Configuration
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Memory Size | Размер памяти сознания | `ARK_MEMORY_SIZE` | `1000` |
| Emotional Memory | Размер эмоциональной памяти | `ARK_EMOTIONAL_MEMORY_SIZE` | `500` |
| Emotional Decay | Скорость затухания эмоций | `ARK_EMOTIONAL_DECAY_RATE` | `0.1` |

### Network Configuration
| Категория | Назначение | Имя переменной | Пример/комментарий |
|-----------|------------|----------------|-------------------|
| Request Timeout | Таймаут запросов | `ARK_REQUEST_TIMEOUT` | `30` |
| Connection Timeout | Таймаут соединений | `ARK_CONNECTION_TIMEOUT` | `10` |

---

## 📋 Процедуры управления секретами

### Добавление нового секрета
1. Добавить переменную в `secrets.env`
2. Добавить соответствующую конфигурацию в `config.py`
3. Обновить этот инвентаризационный лист
4. Протестировать загрузку секрета

### Ротация секретов
1. Создать новые секреты
2. Обновить `secrets.env`
3. Перезапустить систему
4. Удалить старые секреты из истории Git

### Экстренная процедура при компрометации
1. Немедленно отозвать скомпрометированные секреты
2. Использовать `git filter-repo` для удаления из истории
3. Сгенерировать новые секреты
4. Обновить все системы, использующие старые секреты

---

## 🔍 Мониторинг и аудит

### Автоматические проверки
- ✅ Pre-commit hooks блокируют коммиты с секретами
- ✅ Secret loader проверяет целостность секретов
- ✅ Права доступа к secrets.env: 600
- ✅ Файл исключен из Git через .gitignore

### Ручные проверки
- [ ] Еженедельная проверка целостности секретов
- [ ] Ежемесячная ротация критических секретов
- [ ] Квартальный аудит доступа к секретам

---

**Последнее обновление**: 2025-01-26  
**Следующая проверка**: 2025-02-26 