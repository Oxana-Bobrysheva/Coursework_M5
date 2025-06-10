import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


class DBConnection:
    """Класс для подключения к базе данных PostgreSQL"""

    def __init__(self, params):
        self._params = params
        self._database = os.getenv("DATABASE")


    def connect_to_db(self):
        """Метод подключения к базе данных"""
        try:
            return psycopg2.connect(dbname=self._database, **self._params)
        except psycopg2.Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            raise

    def create_db(self):
        """Метод для создания базы данных"""
        try:
            conn = psycopg2.connect(dbname=self._database, **self._params)
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("DROP DATABASE IF EXISTS employers_vacancy;")
                cur.execute("CREATE DATABASE employers_vacancy;")
            conn.close()
        except psycopg2.Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            raise

    def create_tables(self):
        """Method that creates all tables in proper order with error handling"""
        try:
            # First create employers table
            self.db_creating_employers()

            # Then create vacancies table with foreign key
            self.db_creating_vacancies()

        except psycopg2.Error as e:
            print(f"Error creating tables: {e}")
            raise

    def db_creating_employers(self) -> None:
        """Method that creates a table called <employers>"""
        execute_message = """CREATE TABLE IF NOT EXISTS employers 
            (employer_id varchar PRIMARY KEY,
            company_name varchar(50) UNIQUE,
            vacancies_count int)"""
        conn = self.connect_to_db()
        try:
            with conn.cursor() as cur:
                cur.execute(execute_message)
            conn.commit()
            print("Employers table was created successfully")
        finally:
            conn.close()

    def db_creating_vacancies(self) -> None:
        """Method that creates a table called <vacancies>"""
        execute_message = """CREATE TABLE IF NOT EXISTS vacancies 
            (vacancy_id varchar NOT NULL,
            vacancy_name varchar NOT NULL,
            salary_from int,
            salary_to int,
            requirement text,
            url varchar NOT NULL,
            employer_id varchar,
            FOREIGN KEY (employer_id) REFERENCES employers (employer_id))"""
        conn = self.connect_to_db()
        try:
            with conn.cursor() as cur:
                cur.execute(execute_message)
            conn.commit()
            print("Таблица с вакансиями успешно создана")
        except psycopg2.Error as e:
            print(f"Ошибка при создании таблицы вакансий: {e}")
            raise
        finally:
            conn.close()

    def db_filling_vacancies(self, vacancies_list: list):
        """Method that fills the table <vacancies> with data"""
        execute_message = """INSERT INTO vacancies 
                        (vacancy_id, vacancy_name, salary_from, salary_to, requirement, url, employer_id) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        conn = self.connect_to_db()
        try:
            with conn.cursor() as cur:
                for vacancy in vacancies_list:
                    params = (
                        vacancy.get("id"),
                        vacancy.get("name"),
                        (
                            vacancy.get("salary").get("from")
                            if vacancy.get("salary") is not None
                            else 0
                        ),
                        (
                            vacancy.get("salary").get("to")
                            if vacancy.get("salary") is not None
                            else 0
                        ),
                        (
                            vacancy.get("snippet").get("requirement")
                            if vacancy.get("snippet") is not None
                            else None
                        ),
                        vacancy.get("url"),
                        (
                            vacancy.get("employer").get("id")
                            if vacancy.get("employer") is not None
                            else None
                        ),
                    )
                    cur.execute(execute_message, params)
            conn.commit()
            print("Данные по вакансиям добавлены успешно")
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при добавлении вакансий: {e}")
            raise
        finally:
            conn.close()

    def db_filling_columns_for_emps(self, employers_id_list: list, employers_list: list):
        """Method that fills the table <employers> with data"""
        filtered_employers_list = [
            emp for emp in employers_list if emp["id"] in employers_id_list
        ]
        conn = self.connect_to_db()
        try:
            with conn.cursor() as cur:
                execute_message = """INSERT INTO employers (employer_id, company_name, vacancies_count) VALUES 
            (%s, %s, %s)"""
                for employer in filtered_employers_list:
                    params = (
                        employer.get("id"),
                        employer.get("name"),
                        employer.get("open_vacancies"),
                    )
                    cur.execute(execute_message, params)
            conn.commit()
            print("Данные по работодателям внесены в таблицу")
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при внесении данных о работодателях: {e}")
            raise
        finally:
            conn.close()
