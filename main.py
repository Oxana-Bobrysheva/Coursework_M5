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
    params = config()
    db_connect = DBConnection(params)

    # Сначала создаем базу данных
    db_connect.create_db()

    # Затем создаем таблицы
    db_connect.create_tables()

    # Получаем список компаний
    employer_word = input("Введите ключевое слово для поиска компаний (например, 'яндекс'):\n") or None
    employers_count = int(input("Введите количество компаний для поиска (до 50):\n"))

    employer_obj = FindEmployerFromHHApi()
    employers = employer_obj.get_employer_info(employers_count, keyword=employer_word)

    if not employers:
        print("Не найдено компаний по вашему запросу")
        return

    # # Выводим список найденных компаний
    # print("\nНайденные компании:")
    # for i, emp in enumerate(employers, 1):
    #     print(f"{i}. {emp.get('name')} (ID: {emp.get('id')})")
    #
    # # Заполняем таблицу companies
    # db_connect.db_filling_companies(employers)
    # print("\nДанные о компаниях добавлены в базу данных")
    #
    # # Заполняем таблицу vacancies для всех компаний
    # for emp in employers:
    #     emp_id = emp.get("id")
    #     print(f"\nОбработка компании {emp.get('name')} (ID: {emp_id})")
    #     vacancy_list = FindVacancyFromHHApi().get_vacancies_by_employer_id(emp_id)
    #     print(f"Найдено вакансий: {len(vacancy_list)}")
    #     if vacancy_list:
    #         db_connect.db_filling_vacancies(vacancy_list)

    # Работа с менеджером базы данных
    query_manager = DBManager(params)

    while True:
        print("\nВыберите действие:")
        print("1. Получить список всех компаний и количество вакансий")
        print("2. Получить список всех вакансий")
        print("3. Получить среднюю зарплату по вакансиям")
        print("4. Получить вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("Ваш выбор: ")

        if choice == "1":
            print(query_manager.get_companies_and_vacancies_count())
        elif choice == "2":
            print(query_manager.get_all_vacancies())
        elif choice == "3":
            print(query_manager.get_avg_salary())
        elif choice == "4":
            print(query_manager.get_vacancies_with_higher_salary())
        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска: ")
            print(query_manager.get_vacancies_with_keyword(keyword))
        elif choice == "0":
            break
        else:
            print("Неверный ввод, попробуйте еще раз")


if __name__ == "__main__":
    user_interaction_with_db()
