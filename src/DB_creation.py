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
        return psycopg2.connect(dbname=self._database, **self._params)

    def create_db(self):
        """Метод для создания базы данных"""
        conn = psycopg2.connect(dbname=self._database, **self._params)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("DROP DATABASE IF EXISTS employers_vacancy;")
        cur.execute("CREATE DATABASE employers_vacancy;")
        cur.close()
        conn.close()

    def db_creating_employers(self) -> None:
        execute_message = """CREATE TABLE IF NOT EXISTS employers 
            (employer_id varchar PRIMARY KEY,
            company_name varchar(50) UNIQUE,
            vacancies_count int)"""
        with self.connect_to_db().cursor() as cur:
            cur.execute(execute_message)


    def db_filling_columns_for_emps(self, employers_id_list: list, employers_list: list):
        filtered_employers_list = [
            emp for emp in employers_list if emp["id"] in employers_id_list
        ]
        try:
            execute_message = """INSERT INTO employers (employer_id, company_name, vacancies_count) VALUES 
            (%s, %s, %s)"""
            for employer in filtered_employers_list:
                params = (
                    employer.get("id"),
                    employer.get("name"),
                    employer.get("open_vacancies"),
                )
                self.connect_to_db(execute_message, params)
        except Exception as e:
            print(f"Ошибка: {e}")

    def db_creating_vacancies(self) -> None:
        execute_message = """CREATE TABLE IF NOT EXISTS vacancies 
            (vacancy_id varchar NOT NULL,
            vacancy_name varchar NOT NULL,
            salary_from int,
            salary_to int,
            requirement text,
            url varchar NOT NULL,
            employer_id varchar,
            FOREIGN KEY (employer_id) REFERENCES employers (employer_id))"""
        with self.connect_to_db().cursor() as cur:
            cur.execute(execute_message)

    def db_filling_vacancies(self, vacancies_list: list):
        execute_message = """INSERT INTO vacancies 
                        (vacancy_id, vacancy_name, salary_from, salary_to, requirement, url, employer_id) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
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
                    else 0
                ),
                vacancy.get("url"),
                (
                    vacancy.get("employer").get("id")
                    if vacancy.get("employer") is not None
                    else 0
                ),
            )
            self.connect_to_db(execute_message, params)