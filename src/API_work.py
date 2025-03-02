from abc import ABC, abstractmethod

import requests


class ApiHH(ABC):

    @abstractmethod
    def __init__(self):
        pass


class FindVacancyFromHHApi(ApiHH):
    """
    Класс для получения данных по вакансиям из API HeadHunter
    """

    def __init__(self):
        self.__url = "https://api.hh.ru/vacancies"
        self.__headers = {"User-Agent": "HH-User-Agent"}
        self.__params = {"text": "", "page": 0, "per_page": 100}
        self.__vacancies = []

    def __get_vacancies(self, keyword: str):
        """Приватный метод получения списка вакансий"""
        self.__params["text"] = keyword
        try:
            while self.__params.get("page") != 20:
                if (
                    requests.get(
                        self.__url, headers=self.__headers, params=self.__params
                    ).status_code
                    == 200
                ):
                    response = requests.get(
                        self.__url, headers=self.__headers, params=self.__params
                    )
                    vacancies = response.json()["items"]
                    self.__vacancies.extend(vacancies)
                    self.__params["page"] += 1
        except Exception as e:
            print(f"Что-то не так с подключением, ошибка: {e}")

    def __get_vacancies_by_employer_id(self, employer_id: str):
        """Приватный метод для получения вакансий по идентификационному номеру работодателя"""
        try:
            self.__params["employer_id"] = employer_id
            while self.__params.get("page") != 10:
                response = requests.get(
                    self.__url, headers=self.__headers, params=self.__params
                )
                response_data = response.json()

                if "items" in response_data:
                    vacancies = response_data["items"]
                    self.__vacancies.extend(vacancies)
                else:
                    print(f"Нет вакансий для работодателя с ID: {employer_id}")
                    break  # Выход из цикла, если нет вакансий

                self.__params["page"] += 1
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def get_vacancies(self, keyword: str) -> list:
        """Получаем список вакансий в формате json из одноименного приватного метода"""
        self.__get_vacancies(keyword)
        return self.__vacancies

    def get_vacancies_by_employer_id(self, employer_id: str):
        self.__get_vacancies_by_employer_id(employer_id)
        return self.__vacancies


class FindEmployerFromHHApi(ApiHH):
    """
    Класс для получения данных по вакансиям из API HeadHunter
    """

    def __init__(self):
        self.__url = "https://api.hh.ru/employers"
        self.__headers = {"User-Agent": "HH-User-Agent"}
        self.__params = {
            "text": "",
            "page": 0,
            "per_page": 100,
            "sort_by": "by_vacancies_open",
        }
        self.__employers = []

    def __get_employer_info(self, keyword=""):
        """Приватный метод получения информации из АПИ HH по работодателям"""
        try:
            self.__params["text"] = keyword
            while self.__params.get("page") != 20:
                response = requests.get(
                    self.__url, headers=self.__headers, params=self.__params
                )
                employers = response.json()
                self.__employers.extend(employers["items"])
                self.__params["page"] += 1
        except Exception as e:
            print(f"Что-то не так с подключением, ошибка: {e}")

    def get_employer_info(self, employers_count, keyword=""):
        self.__get_employer_info(keyword)
        for employer in self.__employers[:employers_count]:
            print(f"{employer.get('name')}, id: {employer.get('id')}")
        print("...")
        return self.__employers