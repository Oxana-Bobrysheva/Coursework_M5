import psycopg2

from src.DB_creation import DBConnection
from config import config

class DBManager(DBConnection):
    """Класс для взаимодействия с базой данных"""

    def __init__(self):
        super().__init__()

    # def connect_to_db(self, query, params=None):
    #     try:
    #         with psycopg2.connect(
    #                 host=self._host,
    #                 database=self._database,
    #                 user=self._username,
    #                 port=self._port,
    #                 password=self._password,
    #         ) as conn:
    #             conn.autocommit = True
    #             with conn.cursor() as cur:
    #                 cur.execute(query, params)
    #                 result = cur.fetchall()
    #     except Exception as e:
    #         print(f"Ошибка при выполнении запроса: {e}")
    #         result = []
    #     return result

    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        conn = None
        try:
            conn = super().connect_to_db()  # Use parent's connection method
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
        """Метод для получения из базы данных названия компании и количества вакансий этой компании"""
        execute_message = """SELECT employers.company_name, COUNT(vacancies.employer_id)
        FROM employers JOIN vacancies USING (employer_id) GROUP BY employer_id"""
        results = self.execute_query(execute_message)
        return f'Компании и количество вакансий:{results}'

    def get_all_vacancies(self):
        """Метод для получения информации по вакансии и названию компании"""
        execute_message = """SELECT employers.company_name, vacancies.vacancy_name, 
        ((vacancies.salary_from + vacancies.salary_to) / 2), vacancies.url
        FROM vacancies JOIN employers USING(employer_id)"""
        results = self.execute_query(execute_message)
        return f'Список всех вакансий:\n{results[:10] if results else "Вакансий не найдено"} \n...'

    def get_avg_salary(self):
        """Метод для получения средней зарплаты по вакансиям"""
        execute_message = """SELECT AVG((vacancies.salary_from + vacancies.salary_to) / 2) FROM vacancies"""
        results = self.execute_query(execute_message)
        return f'Средняя зарплата по вакансиям:\n{results[0][0] if results else "Нет данных по зарплате"}'

    def get_vacancies_with_higher_salary(self):
        """Метод для получения вакансий с зарплатой выше среднего"""
        execute_message = """SELECT * FROM vacancies WHERE ((vacancies.salary_from + vacancies.salary_to) / 2) > 
        (SELECT (AVG((vacancies.salary_from + vacancies.salary_to) / 2)) FROM vacancies)"""
        results = self.execute_query(execute_message)
        return f'Вакансии с зарплатой выше среднего:\n{results[:10] if results else "Нет подходящих вакансий"}'

    def get_vacancies_with_keyword(self, keyword: str):
        """Метод для получения вакансий по ключевому слову"""
        execute_message = f"""SELECT * FROM vacancies WHERE vacancy_name ILIKE %s"""
        results = self.execute_query(execute_message, ('%' + keyword + '%',))
        return f'Вакансии по ключевому слову "keyword":\n{results[:10] if results else "Нет подходящих вакансий"}'
