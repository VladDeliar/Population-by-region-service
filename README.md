# Сервіс населення країн

Сервіс завантажує дані про населення країн з інтернету, зберігає їх у PostgreSQL
(окремим рядком по кожній країні) і виводить зведення по регіонах, порахувавши
його одним SQL-запитом.

## Як запустити

```bash
git clone <repo-url>
cd <repo-dir>
docker-compose up get_data
docker-compose up print_data
```

PostgreSQL підніметься автоматично — обидві команди чекають, поки база буде готова.

- **get_data** — завантажує сторінку джерела, парсить її і зберігає країни в базу.
- **print_data** — виводить по кожному регіону:

```
Назва регіону: 
Загальне населення регіону:
Назва найбільшої країни в регіоні (за населенням): 
Населення найбільшої країни в регіоні: 
Назва найменшої країни в регіоні: 
Населення найменшої країни в регіоні:
```

## Перемикання джерела даних (бонус)

Джерело обирається змінною оточення `SOURCE`:

| `SOURCE`                     | Звідки дані                                                  |
|------------------------------|--------------------------------------------------------------|
| `wikipedia` (за замовчуванням) | Вікіпедія — список країн за населенням (ООН), зафіксована версія сторінки |
| `statisticstimes`            | statisticstimes.com — країни за населенням                   |


скопіюйте [.env.example](.env.example) у `.env` і впишіть потрібне
значення — docker-compose підхопить файл сам.

Кожне джерело зберігається в базі окремо (колонка `source`), тому вони не
перезаписують одне одного.

## HTTP API (FastAPI)

```bash
docker-compose up api
```

- http://localhost:8000/regions — зведення по регіонах у JSON
- http://localhost:8000/countries — сирі дані по країнах
- http://localhost:8000/docs — Swagger-документація

Обидва ендпоінти приймають параметр `?source=wikipedia|statisticstimes`.

## Як це влаштовано

- Все асинхронне: `aiohttp` (завантаження сторінок), SQLAlchemy 2.0 async +
  `asyncpg` (робота з базою), FastAPI (бонусний API).
- Парсери — класи зі спільним предком `BaseParser`
  ([app/parsers/base.py](app/parsers/base.py)). Яке джерело використати,
  вирішує `ParserFactory` за значенням `SOURCE`. Нове джерело = один новий
  клас + один рядок у фабриці.
- Дані зберігаються неагреговано: таблиця `countries`, один рядок — одна країна.
- Агрегація — один SQL-запит (`GROUP BY region`; назва найбільшої/найменшої
  країни береться як перший елемент `array_agg(name ORDER BY population)`) —
  див. `CountryRepository.get_region_stats` у [app/repository.py](app/repository.py).

```
app/
├── main.py              # точка входу: get_data | print_data
├── config.py            # налаштування зі змінних оточення (DATABASE_URL, SOURCE)
├── database.py          # підключення до бази (async engine + сесії)
├── models.py            # ORM-модель Country
├── dto.py               # CountryRecord — проміжний об'єкт "парсер → база"
├── repository.py        # робота з таблицею + агрегувальний запит
├── services.py          # сценарії get_data і print_data
├── api.py               # бонусний FastAPI-застосунок
└── parsers/
    ├── base.py          # BaseParser: завантаження сторінки + контракт parse()
    ├── wikipedia.py     # парсер Вікіпедії
    ├── statisticstimes.py  # парсер statisticstimes.com
    └── __init__.py      # ParserFactory — вибір парсера за SOURCE
```
