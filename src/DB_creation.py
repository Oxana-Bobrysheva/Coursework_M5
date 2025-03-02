import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


class DBConnection:
    """Класс для подключения к базе данных PostgreSQL"""

    def __init__(self):
        self._host = os.getenv("HOST")
        self._database = os.getenv("DATABASE")
        self._username = os.getenv("USERNAME")
        self._port = os.getenv("PORT")
        self._password = os.getenv("PASSWORD")

    def connect_to_db(self, query, params=None):
        conn = psycopg2.connect(
                    host=self._host,
                    database=self._database,
                    user=self._username,
                    port=self._port,
                    password=self._password)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(query, params)

        cur.close()
        conn.close()

    def create_db(self):
        """Метод для создания базы данных"""
        try:
            self._database = "postgres"
            execute_message_drop = "DROP DATABASE IF EXISTS employers_vacancy;"
            self.connect_to_db(execute_message_drop)
        except Exception as e:
            print(f'Ошибка с подключением: {e}')
        execute_message_create = "CREATE DATABASE employers_vacancy;"
        self.connect_to_db(execute_message_create)

    def db_creating_employers(self) -> None:
        execute_message = """CREATE TABLE IF NOT EXISTS employers 
            (employer_id varchar PRIMARY KEY,
            company_name varchar(50) UNIQUE,
            vacancies_count int)"""
        return self.connect_to_db(execute_message)

    def db_filling_columns_for_emps(self, employers_id_list: list, employers_list: list):
        filtered_employers_list = [
            emp for emp in employers_list if emp["id"] in employers_id_list
        ]
        try:
            execute_message = """INSERT INTO employers (employer_id, company_name, vacancies_count) VALUES (%s, %s, %s)"""
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
        return self.connect_to_db(execute_message)

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