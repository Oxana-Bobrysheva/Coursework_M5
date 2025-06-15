from src.vacancy_class import Vacancy


def test_get_vac_obj(get_vac_object_class):
    vac_obj_info = {
        "name": "Python Developer",
        "url": "<https://hh.ru/vacancy/123456>",
        "salary_from": "100 000",
        "salary_to": "150 000",
        "requirement": "Требования: опыт работы от 3 лет...",
        "id": "000000000",
    }
    assert vac_obj_info == get_vac_object_class.get_vacancy_info


def test_cast_to_object_list(get_vac_object_list):
    list_vacs = Vacancy.cast_to_object_list(get_vac_object_list)
    obj = list_vacs[0]
    assert obj.get_vacancy_info.get("salary_to") == 71800
