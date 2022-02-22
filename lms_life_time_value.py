from collections import defaultdict
from typing import List, Dict
from datetime import timedelta
from all_var import LAST_UPDATE_TIME, TABLE_ACCOUNT_MANAGER, TABLE_GR
from decorators import benchmark, try_except
from mysql_tables import table_advanced_payments, table_advanced_users
from spreadsheet import clear_insert_spreedsheet
from usual_func import last_months, group_by_field


def get_users_pays(users, id_lms_pays, ab_price) -> Dict[str, dict]:
    """Собираем нужные данные из клиентов и платежей.\n
        Получаем: \n
    users - список клиентов.\n
    id_lead_pays - словарь {id_lead : payments}.\n
    id_contact_pays - словарь {d_contact : payments}.\n
        Возвращаем:\n
    user_data - словарь {id: данные}
    """
    user_data = defaultdict(lambda: defaultdict(int))
    for user in users:
        pays = id_lms_pays.get(user['id_lms'], [])
        if not pays or user['last_regular_lesson'] is None:
            continue
        pays_income = [i['income'] for i in pays]
        if max(pays_income) < ab_price:
            continue
        user_data[user['id_lms']]['last_regular_lesson'] = user['last_regular_lesson']
        user_data[user['id_lms']]['live'] = user['is_study']
        user_data[user['id_lms']]['last_date_payment'] = user['last_date_payment']
        user_data[user['id_lms']]['pays'] = pays
    return user_data


def get_all_pays(payments: list, date_3_month):
    """Подсчитывает все суммы из списка.\n
        Получает:\n
    datas - список платежей, \n
    date_3_month - дату 3 месяца\n
        Возвращает:\n
    count_all_pays - все полученные суммы, \n
    count_all_pay_to_3_month - все полученные суммы не ранее 3 месяца.
    """
    count_all_pays = 0
    count_all_pay_to_3_month = 0
    for pay in payments:
        count_all_pays += pay['income']
        if pay['document_date'] < date_3_month:
            count_all_pay_to_3_month += pay['income']
    return count_all_pays, count_all_pay_to_3_month


def get_dict_datas_payments(user_pays: Dict[str, dict], period: list):
    """"Заполняет словарь данными по месячно.\n
        Получает:\n
    user_data - словарь {id: данные}.\n
    period - список дат месяцев за год.\n
        Возвращает:\n
    dict_datas_payments -словарь с данными по месяцам
    """
    dict_datas_payments = defaultdict(lambda: defaultdict(list))
    for id_lead, datas in user_pays.items():
        date_pays = sorted(datas['pays'], key=lambda x: x['document_date'])
        date_first_payments = date_pays[0]['document_date']
        date_last_regular_lesson = datas['last_regular_lesson']
        date_dict = date_first_payments - timedelta(days=date_first_payments.day - 1)
        count_all_pays, count_all_pay_to_3_month = get_all_pays(datas['pays'], period[2])
        dict_datas_payments[date_dict]['купило'].append(1)
        dict_datas_payments[date_dict]['принесли'].append(count_all_pays)
        dict_datas_payments[date_dict]['принесли_3'].append(count_all_pay_to_3_month)
        dict_datas_payments[date_dict]['кто пришел'].append(id_lead)
        if datas['live'] == 0:
            dict_datas_payments[date_dict]['отвалилось'].append(1)
            dict_datas_payments[date_dict]['кто отвалился'].append(id_lead)
            if date_last_regular_lesson is None:
                continue
            elif date_last_regular_lesson <= period[3]:
                dict_datas_payments[date_dict]['отвалилось_3'].append(1)
    return dict_datas_payments


def get_values(dict_datas_payments: dict):
    """Подготавливает данные к заполнению таблицы.\n
        Получает:\n
    dict_datas_payments -словарь с данными по месяцам\n
        Возвращает:\n
    values_base - данные для таблицы с клиентами и платежами, \n
    values_base_list - данные с номерами id клиентов.
    """
    dict_datas_payments = sorted(dict_datas_payments.items(), key=lambda d: d[0])
    values_base = []
    counter = 2
    for date, datas in dict_datas_payments:
        values = [None]
        values.append(date.strftime('%Y-%m-%d'))
        for name in ['купило', 'принесли', 'отвалилось', 'принесли_3', 'отвалилось_3']:
            values.append(sum(datas.get(name, [])))
        values.append(f'=E{counter}/C{counter}')
        values.append(f'=G{counter}/C{counter}')
        values.append(f'=D{counter}/C{counter}')
        values.append(f'=F{counter}/C{counter}')
        balance = list(set(datas.get('кто пришел', [])).difference(set(datas.get('кто отвалился', []))))
        values.append(str(datas.get('кто отвалился', [])))
        values.append(str(balance))
        values_base.append(values)
        counter += 1
    return values_base


@benchmark
@try_except
def get_life_time_value_base(payments: List[dict], users: List[dict], table, name_table, ab_price=5000):
    period = last_months(12, 'yes')
    id_lms_pays = group_by_field(payments, 'id_customer', 'many')
    user_pays = get_users_pays(users, id_lms_pays, ab_price)
    dict_datas_payments = get_dict_datas_payments(user_pays, period)
    values = get_values(dict_datas_payments)
    header = [LAST_UPDATE_TIME, 'Месяц', 'Сколько купило', 'Сколько принесли', 'Сколько отвалилось',
              'Сколько принесли (-3 мес)', 'Сколько отвалилось (-3 мес)', '%', '% (-3 мес)', 'LTV', 'LTV (-3 мес)',
              'Кто отвалился', 'Кто остался']
    values.insert(0, header)
    clear_insert_spreedsheet(table, name_table, values)


def get_life_time_value(payments, users):
    get_life_time_value_base(payments, users, TABLE_ACCOUNT_MANAGER, 'lms LTV!A:M')

    payments = [paument for paument in advanced_payments if paument.get('direction') == 'GR']
    get_life_time_value_base(payments, advanced_users, TABLE_GR, 'lms LTV-GR!A:M', 3400)


if __name__ == '__main__':
    advanced_payments = table_advanced_payments().get_data()
    advanced_users = table_advanced_users().get_data()
    get_life_time_value(advanced_payments, advanced_users)
