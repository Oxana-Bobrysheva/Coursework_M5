import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


class DBManager:
    """Класс для взаимодействия с базой данных"""

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

    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        conn = None
        try:
            conn = self.connect_to_db()
            with conn.cursor() as cur:
                cur.execute(query, params)
                if cur.description:  # If there are results to fetch
                    result = cur.fetchall()
                else:
                    result = None
            conn.commit()
            return result
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Ошибка при выполнении запроса: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_companies_and_vacancies_count(self):
        """Получает список всех компаний и количество вакансий у каждой компании"""
        query = """
        SELECT c.name, COUNT(v.id) as vacancies_count
        FROM companies c
        LEFT JOIN vacancies v ON c.id = v.company_id
        GROUP BY c.id
        ORDER BY vacancies_count DESC
        """
        results = self.execute_query(query)
        if not results:
            return "Нет данных о компаниях"

        output = ["Компании и количество вакансий:"]
        for company, count in results:
            output.append(f"{company}: {count} вакансий")
        return "\n".join(output)

    def get_all_vacancies(self):
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию"""
        query = """
        SELECT c.name as company, v.name as vacancy,
               CASE
                   WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL
                       THEN (v.salary_from + v.salary_to) / 2
                   WHEN v.salary_from IS NOT NULL THEN v.salary_from
                   WHEN v.salary_to IS NOT NULL THEN v.salary_to
                   ELSE NULL
               END as salary,
               v.url
        FROM vacancies v
        JOIN companies c ON v.company_id = c.id
        ORDER BY salary DESC NULLS LAST
        LIMIT 20
        """
        results = self.execute_query(query)
        if not results:
            return "Вакансий не найдено"

        output = ["Список вакансий (первые 20):"]
        for company, vacancy, salary, url in results:
            salary_info = f"Зарплата: {salary}" if salary else "Зарплата не указана"
            output.append(f"{company} - {vacancy}\n{salary_info}\nСсылка: {url}\n")
        return "\n".join(output)

    def get_avg_salary(self):
        """Получает среднюю зарплату по вакансиям"""
        query = """
        SELECT AVG(
            CASE
                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                    THEN (salary_from + salary_to) / 2
                WHEN salary_from IS NOT NULL THEN salary_from
                WHEN salary_to IS NOT NULL THEN salary_to
                ELSE NULL
            END
        ) as avg_salary
        FROM vacancies
        """
        results = self.execute_query(query)
        if not results or not results[0][0]:
            return "Нет данных о зарплатах"
        return f"Средняя зарплата: {int(results[0][0])} руб."

    def get_vacancies_with_higher_salary(self):
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        query = """
        SELECT v.name as vacancy, c.name as company,
               CASE
                   WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL
                       THEN (v.salary_from + v.salary_to) / 2
                   WHEN v.salary_from IS NOT NULL THEN v.salary_from
                   WHEN v.salary_to IS NOT NULL THEN v.salary_to
                   ELSE NULL
               END as salary,
               v.url
        FROM vacancies v
        JOIN companies c ON v.company_id = c.id
        WHERE (
            CASE
                WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL
                    THEN (v.salary_from + v.salary_to) / 2
                WHEN v.salary_from IS NOT NULL THEN v.salary_from
                WHEN v.salary_to IS NOT NULL THEN v.salary_to
                ELSE NULL
            END
        ) > (
            SELECT AVG(
                CASE
                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                        THEN (salary_from + salary_to) / 2
                    WHEN salary_from IS NOT NULL THEN salary_from
                    WHEN salary_to IS NOT NULL THEN salary_to
                    ELSE NULL
                END
            )
            FROM vacancies
        )
        ORDER BY salary DESC
        LIMIT 20
        """
        results = self.execute_query(query)
        if not results:
            return "Нет вакансий с зарплатой выше средней"

        output = ["Вакансии с зарплатой выше средней (первые 20):"]
        for vacancy, company, salary, url in results:
            output.append(
                f"{company} - {vacancy}\nЗарплата: {int(salary)} руб.\nСсылка: {url}\n"
            )
        return "\n".join(output)

    def get_vacancies_with_keyword(self, keyword: str):
        """Получает список всех вакансий, в названии которых содержатся переданные слова"""
        query = """
        SELECT v.name as vacancy, c.name as company,
               CASE
                   WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL
                       THEN (v.salary_from + v.salary_to) / 2
                   WHEN v.salary_from IS NOT NULL THEN v.salary_from
                   WHEN v.salary_to IS NOT NULL THEN v.salary_to
                   ELSE NULL
               END as salary,
               v.url
        FROM vacancies v
        JOIN companies c ON v.company_id = c.id
        WHERE v.name ILIKE %s
        ORDER BY salary DESC NULLS LAST
        LIMIT 20
        """
        results = self.execute_query(query, ("%" + keyword + "%",))
        if not results:
            return f"Нет вакансий по ключевому слову '{keyword}'"

        output = [f"Результаты поиска по '{keyword}' (первые 20):"]
        for vacancy, company, salary, url in results:
            salary_info = (
                f"Зарплата: {int(salary)} руб." if salary else "Зарплата не указана"
            )
            output.append(f"{company} - {vacancy}\n{salary_info}\nСсылка: {url}\n")
        return "\n".join(output)
