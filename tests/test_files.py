from unittest.mock import MagicMock, patch

from src.files_class_module import JSONSaver


@patch("builtins.open")
@patch("json.load")
def test_delete_vacancy(mock_load, mock_open, get_vac_object_class):
    mock_response = MagicMock()
    mock_opening = MagicMock()
    mock_open.return_value = mock_opening
    mock_response.json.return_value = {
        "id": "107449290",
        "premium": False,
        "name": 'Стажёр по направлению "Нагрузочное тестирование"',
    }
    mock_load.return_value = mock_response
    assert JSONSaver().delete_vacancy(get_vac_object_class) == "Vacancy is not in data"
