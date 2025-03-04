from config import config
from src.API_work import FindEmployerFromHHApi, FindVacancyFromHHApi
from src.DB_creation import DBConnection
from src.utils import filter_vacancies, get_top_vacancies, get_vacancies_by_salary, sort_vacancies
from src.vacancies import Vacancy
from src.DB_operation import DBManager


def user_interaction():
    """Функция для взаимодействия с пользователем"""
    search_query = input("Введите поисковый запрос: ")
    hh_vacancies = FindVacancyFromHHApi().get_vacancies(
        search_query
    )  # Получение вакансий с hh.ru в формате JSON
    vacancies_list = Vacancy.cast_to_object_list(
        hh_vacancies
    )  # Преобразование набора данных из JSON в список объектов
    top_n = int(input("Введите количество вакансий для вывода N самых оплачиваемых: "))
    filter_words = list(
        input("Введите ключевые слова для фильтрации вакансий: ").split()
    )
    salary_range_from = input("Введите диапазон зарплат от: ")  # Пример: 100000
    salary_range_to = input("Введите диапазон зарплат до: ")  # Пример: 150000
    filtered_vacancies = filter_vacancies(vacancies_list, filter_words)
    ranged_vacancies = get_vacancies_by_salary(
        filtered_vacancies, salary_range_from, salary_range_to
    )
    sorted_vacancies = sort_vacancies(ranged_vacancies)
    top_vacancies = get_top_vacancies(sorted_vacancies, top_n)
    print(top_vacancies)


def user_interaction_with_db():
    """Функция для создания, заполнения и взаимодействия пользователя с базой данных вакансий"""
    employer_word = input("Введите слово по которому хотите найти работодателя или оставьте поле пустым:\n")
    employers_count = int(input("Введите топ N (число до 50) вакансий для просмотра:\n"))
    employer_obj = FindEmployerFromHHApi()
    employers = employer_obj.get_employer_info(employers_count, keyword=employer_word)
    params = config()
    db_connect = DBConnection(params)
    db_connect.create_db()

    db_connect.db_creating_employers()
    employers_id_list = list(input("Введите через запятую id не менее 10 компаний для отслеживания:\n").split(", "))
    db_connect.db_filling_columns_for_emps(employers_id_list, employers)

    db_connect.db_creating_vacancies()
    for emp_id in employers_id_list:
        vacancy_list = FindVacancyFromHHApi().get_vacancies_by_employer_id(emp_id)
        db_connect.db_filling_vacancies(vacancy_list)
    searching_keyword = input('Введите слово для поиска по имеющимся вакансиям ...')
    query_manager = DBManager()
    print(query_manager.get_companies_and_vacancies_count())
    print(query_manager.get_all_vacancies())
    print(query_manager.get_avg_salary())
    print(query_manager.get_vacancies_with_higher_salary())
    print(query_manager.get_vacancies_with_keyword(searching_keyword))


if __name__ == "__main__":
    user_interaction_with_db()