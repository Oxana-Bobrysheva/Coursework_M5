import psycopg2

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class DBConnection:
    """Класс для подключения к базе данных PostgreSQL"""

    def __init__(self, params):
        self._params = params

    def connect_to_db(self):
        """Метод подключения к базе данных"""
        try:
            return psycopg2.connect(**self._params)
        except psycopg2.Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            raise

    def create_db(self):
        """Метод для создания базы данных"""
        print(self._params)
        conn = None
        try:
            # Создаем копию параметров и подключаемся к системной БД postgres
            params = self._params.copy()
            params['database'] = 'postgres'  # Подключаемся к системной БД

            conn = psycopg2.connect(**params)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s;",
                    (self._params["database"],)
                )
                exists = cur.fetchone()
                if not exists:
                    cur.execute(f'CREATE DATABASE "{self._params["database"]}";')
                    print(f"База данных '{self._params['database']}' создана.")
                else:
                    print(f"База данных '{self._params['database']}' уже существует.")
        except psycopg2.Error as e:
            print(f"Ошибка при создании базы данных: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def create_tables(self):
        """Создание таблиц в правильном порядке"""
        conn = None
        try:
            conn = self.connect_to_db()
            with conn.cursor() as cur:
                # Создаем таблицу companies
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS companies (
                        id SERIAL PRIMARY KEY,
                        hh_id VARCHAR(50) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        open_vacancies INTEGER
                    );
                """
                )

                # Создаем таблицу vacancies с внешним ключом
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS vacancies (
                        id SERIAL PRIMARY KEY,
                        company_id INTEGER REFERENCES companies(id),
                        name VARCHAR(255) NOT NULL,
                        salary_from INTEGER,
                        salary_to INTEGER,
                        requirement TEXT,
                        url TEXT NOT NULL
                    );
                """
                )
            conn.commit()
            print("Таблицы созданы успешно")
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            print(f"Ошибка при создании таблиц: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def db_filling_companies(self, employers_list: list):
        """Заполнение таблицы companies"""
        conn = self.connect_to_db()
        try:
            with conn.cursor() as cur:
                for employer in employers_list:
                    cur.execute(
                        """
                        INSERT INTO companies (hh_id, name, open_vacancies)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (hh_id) DO NOTHING;
                    """,
                        (
                            employer.get("id"),
                            employer.get("name"),
                            employer.get("open_vacancies"),
                        ),
                    )
            conn.commit()
            print("Данные о компаниях добавлены успешно")
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Ошибка при добавлении компаний: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def db_filling_vacancies(self, vacancies_list: list):
        """Заполнение таблицы vacancies"""
        conn = self.connect_to_db()
        try:
            with conn.cursor() as cur:
                for vacancy in vacancies_list:
                    # Обработка случая, когда salary отсутствует или None
                    salary = vacancy.get("salary") or {}

                    # Проверка employer, чтобы избежать ошибки, если employer None
                    employer = vacancy.get("employer") or {}

                    # Проверка snippet, чтобы избежать ошибки, если snippet None
                    snippet = vacancy.get("snippet") or {}

                    cur.execute(
                        """
                        INSERT INTO vacancies
                        (company_id, name, salary_from, salary_to, requirement, url)
                        VALUES (
                            (SELECT id FROM companies WHERE hh_id = %s),
                            %s, %s, %s, %s, %s
                        )
                    """,
                        (
                            employer.get("id"),
                            vacancy.get("name"),
                            salary.get("from"),
                            salary.get("to"),
                            snippet.get("requirement"),
                            vacancy.get("url"),
                        ),
                    )
            conn.commit()
            print("Данные по вакансиям добавлены успешно")
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при добавлении вакансий: {e}")
            raise
        finally:
            conn.close()
