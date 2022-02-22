import datetime

import pytest

from lms_life_time_value import get_users_pays, get_all_pays, get_dict_datas_payments
from usual_func import group_by_field

users = [{'id_lms': 100, 'last_regular_lesson': datetime.date(2021, 11, 21), 'is_study': 1,
          'last_date_payment': datetime.date(2021, 11, 5)},
         {'id_lms': 101, 'last_regular_lesson': datetime.date(2021, 10, 21), 'is_study': 1,
          'last_date_payment': datetime.date(2021, 10, 5)},
         {'id_lms': 102, 'last_regular_lesson': datetime.date(2021, 9, 21), 'is_study': 0,
          'last_date_payment': datetime.date(2021, 9, 5)},
         {'id_lms': 103, 'last_regular_lesson': None, 'is_study': 0,
          'last_date_payment': None},
         {'id_lms': 104, 'last_regular_lesson': None, 'is_study': 1,
          'last_date_payment': datetime.date(2021, 11, 5)}
         ]

payments = [{'id': 108318, 'document_date': datetime.date(2021, 11, 5), 'income': 21000,
             'id_customer': 100, 'direction': 'GR'},
            {'id': 108318, 'document_date': datetime.date(2021, 10, 3), 'income': 1200,
             'id_customer': 100, 'direction': 'GR'},
            {'id': 108318, 'document_date': datetime.date(2021, 10, 5), 'income': 21000,
             'id_customer': 101, 'direction': None},
            {'id': 108318, 'document_date': datetime.date(2021, 9, 3), 'income': 1200,
             'id_customer': 101, 'direction': None},
            {'id': 108318, 'document_date': datetime.date(2021, 9, 5), 'income': 21000,
             'id_customer': 102, 'direction': None},
            {'id': 108318, 'document_date': datetime.date(2021, 8, 3), 'income': 1200,
             'id_customer': 102, 'direction': None},
            {'id': 108318, 'document_date': datetime.date(2021, 11, 5), 'income': 1200,
             'id_customer': 104, 'direction': None},
            ]

user_pays = {
    100: {'last_regular_lesson': datetime.date(2021, 11, 21), 'live': 1,
          'last_date_payment': datetime.date(2021, 11, 5), 'pays': [
            {'id': 108318, 'document_date': datetime.date(2021, 11, 5), 'income': 21000, 'id_customer': 100,
             'direction': 'GR'},
            {'id': 108318, 'document_date': datetime.date(2021, 10, 3), 'income': 1200, 'id_customer': 100,
             'direction': 'GR'}]},
    101: {'last_regular_lesson': datetime.date(2021, 10, 21), 'live': 1,
          'last_date_payment': datetime.date(2021, 10, 5), 'pays': [
            {'id': 108318, 'document_date': datetime.date(2021, 10, 5), 'income': 21000, 'id_customer': 101,
             'direction': None},
            {'id': 108318, 'document_date': datetime.date(2021, 9, 3), 'income': 1200, 'id_customer': 101,
             'direction': None}]},
    102: {'last_regular_lesson': datetime.date(2021, 9, 21), 'live': 0, 'last_date_payment': datetime.date(2021, 9, 5),
          'pays': [
              {'id': 108318, 'document_date': datetime.date(2021, 9, 5), 'income': 21000, 'id_customer': 102,
               'direction': None},
              {'id': 108318, 'document_date': datetime.date(2021, 8, 3), 'income': 1200, 'id_customer': 102,
               'direction': None}]}}

period = [datetime.date(2021, 12, 1), datetime.date(2021, 11, 1), datetime.date(2021, 10, 1), datetime.date(2021, 9, 1),
          datetime.date(2021, 8, 1), datetime.date(2021, 7, 1), datetime.date(2021, 6, 1), datetime.date(2021, 5, 1),
          datetime.date(2021, 4, 1), datetime.date(2021, 3, 1), datetime.date(2021, 2, 1), datetime.date(2021, 1, 1),
          datetime.date(2020, 12, 1)]

dict_datas_payments = {
    datetime.date(2021, 10, 1): {'купило': [1], 'принесли': [22200], 'принесли_3': [0], 'кто пришел': [100]},
    datetime.date(2021, 9, 1): {'купило': [1], 'принесли': [22200], 'принесли_3': [1200], 'кто пришел': [101]},
    datetime.date(2021, 8, 1): {'купило': [1], 'принесли': [22200], 'принесли_3': [22200], 'кто пришел': [102],
                                'отвалилось': [1], 'кто отвалился': [102]}}

ab_price = 5000


def test_get_users_pays_correct_data():
    """Тест get_users_pays на правильные данные."""
    id_lms_pays = group_by_field(payments, 'id_customer', 'many')
    actual_result = get_users_pays(users, id_lms_pays, ab_price)
    exspect_result = user_pays
    assert actual_result == exspect_result
    assert len(actual_result) == 3
    assert list(user_pays) == [100, 101, 102]


@pytest.mark.parametrize('id_lms, exspect_result', [(100, [100]), (10, [])])
def test_get_users_pays_id_lms(id_lms, exspect_result):
    """Тест get_users_pays на id_lms."""
    id_lms_pays = group_by_field(payments, 'id_customer', 'many')
    users = [{'id_lms': id_lms, 'last_regular_lesson': datetime.date(2021, 11, 21), 'is_study': 1,
              'last_date_payment': datetime.date(2021, 11, 5)}]
    actual_result = get_users_pays(users, id_lms_pays, ab_price)
    actual_result = list(actual_result.keys())
    assert actual_result == exspect_result


@pytest.mark.parametrize('last_regular_lesson, exspect_result', [(datetime.date(2021, 11, 21), [100]), (None, [])])
def test_get_users_pays_last_regular_lesson(last_regular_lesson, exspect_result):
    """Тест get_users_pays на last_regular_lesson."""
    id_lms_pays = group_by_field(payments, 'id_customer', 'many')
    users = [{'id_lms': 100, 'last_regular_lesson': last_regular_lesson, 'is_study': 1,
              'last_date_payment': datetime.date(2021, 11, 5)}]
    actual_result = get_users_pays(users, id_lms_pays, ab_price)
    actual_result = list(actual_result.keys())
    assert actual_result == exspect_result


@pytest.mark.parametrize('income, exspect_result', [(5000, [100]), (4999, [])])
def test_get_users_pays_income(income, exspect_result):
    """Тест get_users_pays на income."""
    id_lms_pays = {100: [
        {'id': 108318, 'document_date': datetime.date(2021, 11, 5), 'income': income, 'id_customer': 100,
         'direction': 'GR'}]}
    actual_result = get_users_pays(users, id_lms_pays, ab_price)
    actual_result = list(actual_result.keys())
    assert actual_result == exspect_result


@pytest.mark.parametrize('payments, exspect_result', [(payments, [100,101,102]), ([], [])])
def test_get_users_pays_pays(payments, exspect_result):
    """Тест get_users_pays на pays."""
    id_lms_pays = group_by_field(payments, 'id_customer', 'many')
    actual_result = get_users_pays(users, id_lms_pays, ab_price)
    actual_result = list(actual_result.keys())
    assert actual_result == exspect_result


def test_get_all_pays():
    """Тест get_all_pays на правильные данные."""
    datas = user_pays[102]
    a, b = get_all_pays(datas['pays'], period[2])
    assert a, b == (22200, 22000)

    
def test_get_dict_datas_payments_correct_data():
    """Тест get_dict_datas_payments на правильные данные."""
    actual_result = get_dict_datas_payments(user_pays, period)
    exspect_result = dict_datas_payments
    assert exspect_result == actual_result
