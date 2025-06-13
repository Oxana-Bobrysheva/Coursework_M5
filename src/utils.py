import re


def filter_vacancies(vacs_obj_list: list, filter_words) -> list:
    filtered_vacancies = []
    for vacancy in vacs_obj_list:
        for word in filter_words:
            match = re.search(word, vacancy.get_vacancy_info.get("requirement"))
            if match:
                filtered_vacancies.append(vacancy)
                break
    return filtered_vacancies


def get_top_vacancies(srtd_vacancies, top_n) -> str:
    top_n_vacancies = srtd_vacancies[:top_n]
    result = ""
    for vacancy in top_n_vacancies:
        result += f"""Вакансия: {vacancy.get('name')}
        Зарплата от {vacancy.get('salary_from')} до {vacancy.get('salary_to')}
        Требования: {vacancy.get('requirement')}
        Ссылка: {vacancy.get('url')}
        \n"""
    return result


def sort_vacancies(ranged_by_salary_vacs_list) -> list:
    vacs_list = [vacancy.get_vacancy_info for vacancy in ranged_by_salary_vacs_list]
    sorted_vacs_list = sorted(
        vacs_list,
        key=lambda vac: vac.get("salary_from", 0) + vac.get("salary_to", 0),
        reverse=True,
    )
    return sorted_vacs_list


def get_vacancies_by_salary(fltrd_list, salary_from, salary_to) -> list:
    ranged_vacancies = []
    for vacancy in fltrd_list:
        sal_from = int(vacancy.get_vacancy_info.get("salary_from"))
        sal_to = int(vacancy.get_vacancy_info.get("salary_to"))
        avg_salary = (sal_from + sal_to) / len([sal_from, sal_to])
        if int(salary_from) < int(avg_salary) < int(salary_to):
            ranged_vacancies.append(vacancy)
    return ranged_vacancies
