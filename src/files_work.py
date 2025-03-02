import json
import os
from abc import ABC, abstractmethod

from src.vacancy_class import Vacancy


class SaverABC(ABC):

    @abstractmethod
    def save_to_json_file(self, vac_obj_list):
        pass

    @abstractmethod
    def add_vacancy(self, vacancy_object):
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy_object):
        pass


class JSONSaver(SaverABC):
    """Класс для сохранения списка объектов в файл, добавления и удаления объектов"""

    def __init__(self):
        self.path = os.path.join(os.getcwd(), "data/vacancies.json")

    def save_to_json_file(self, vac_obj_list):
        """Метод получает список объектов, записывает их в json-формате в json-файл"""
        vac_dicts_list = [vacancy.get_vacancy_info for vacancy in vac_obj_list]
        with open(self.path, mode="w") as json_file:
            json.dump(vac_dicts_list, json_file, indent=4, ensure_ascii=False)

    def add_vacancy(self, vacancy_object: Vacancy):
        """Метод получает экземпляр класса Vacancy, загружает данные из json-файла,
        затем преобразовывет с помощью геттера экземпляр класса Vacancy в словарь, добавляем  вакансию,
        если ее нет в файле и перезаписываем результат в json-файл"""
        vac_to_add = vacancy_object.get_vacancy_info
        with open(self.path, mode="r+") as json_file:
            py_file = json.load(json_file)
            if not vac_to_add.get("id") in [vacancy.get("id") for vacancy in py_file]:
                py_file.append(vac_to_add)
                json_file.seek(0)
                json_file.truncate()
                json.dump(py_file, json_file, indent=4, ensure_ascii=False)
            else:
                return "Vacancy already in data"

    def delete_vacancy(self, vacancy_object: Vacancy):
        """Метод удаления вакансии из json-файла"""
        vac_to_del = vacancy_object.get_vacancy_info
        with open(self.path, mode="r+") as json_file:
            py_file = json.load(json_file)
            for vacancy in py_file:
                if vac_to_del.get("id") == vacancy.get("id"):
                    py_file.remove(vacancy)
                    json_file.seek(0)
                    json_file.truncate()
                    json.dump(py_file, json_file, indent=4, ensure_ascii=False)
                    return "Vacancy deleted successfully"
        return "Vacancy is not in data"