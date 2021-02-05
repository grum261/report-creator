# Обернуть все декораторами и распихать красиво по классам

import requests
import locale
import re

from time import time
from typing import Dict, List, Union, Tuple
from docxtpl import DocxTemplate
from datetime import datetime
from .models import CompanyReport
from django.core.files import File

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

BASE_URL = 'https://focus-api.kontur.ru/api3/'

# Первод числа в формат 123 321 123
def money_sum_repr(money_sum: str) -> str:
  return f"{round(float(money_sum), 2):,}".replace(',', ' ')

# Полные адрес
def full_address(response: Dict, type_of_UL: str) -> str:
  address = []
  if type_of_UL == 'UL':
    for topo in response[type_of_UL]['legalAddress']['parsedAddressRF'].values():
      if len(topo) == 6:
        address.append(topo)
      elif type(topo) is dict:
        address.append(' '.join([topo[param] for param in ['topoFullName', 'topoValue']]))
  else:
    for topo in response[type_of_UL]['shortenedAddress'].values():
      if len(topo) == 6:
        address.append(topo)
      elif type(topo) is dict:
        address.append(' '.join([topo[param] for param in ['topoFullName', 'topoValue']]))

  return ', '.join(address)

# Дата образования
def registration_date(response: Dict, type_of_UL:str) -> str:
  return datetime.strptime(response[type_of_UL]['registrationDate'], '%Y-%m-%d').strftime('%d %B %Y г.')

# Главы и их должности
def heads(response: Dict, type_of_UL: str) -> str:
  heads = []
  for head in response[type_of_UL]['heads']:
    try:
      heads.append(f"{head['position']}: {head['fio']}, ИНН {head['innfl']}")
    except KeyError:
      heads.append(f"{head['position']}: {head['fio']}")

  return heads

# Учредители
def founders(response: Dict, type_of_UL: str) -> List[str]:
  founders = []
  for key in ['foundersUL', 'foundersForeign', 'foundersFL']:
    try:
      founders.append([
        # добавить логику для иностранных учредителей
        f"{founder['fullName']}, ИНН {founder['inn']}, " + \
        f"вклад - {money_sum_repr(founder['share']['sum'])} руб. " + \
        f"({founder['share']['percentagePlain']} %)" \
        for founder in response[type_of_UL][key]
      ])
    except KeyError:
      continue

  return founders

# ОКВЭД
def activity(response: Dict, type_of_UL: str) -> str:
  activity_repr = f"{response[type_of_UL]['activities']['principalActivity']['text']} " + \
                  f"({response[type_of_UL]['activities']['principalActivity']['code']})"
  
  return activity_repr

# Склонение существительного после числительного
# Сделать декоратором
def verbose_number(number: int, words: list = ['дело', 'дела', 'дел']) -> str:
  remainder = number % 100
  if remainder >= 11 and number <= 19:
    return f"{number} {words[2]}"
  else:
    if remainder % 10 == 1:
      return f"{number} {words[0]}"
    elif remainder % 10 == 2:
      return f"{number} {words[1]}"
    elif remainder % 10 == 3:
      return f"{number} {words[1]}"
    elif remainder % 10 == 4:
      return f"{number} {words[1]}"
    else:
      return f"{number} {words[2]}"

# Для отображения в шаблоне
# Сделать декоратором
def template_representation(response: Dict, defendant_or_claimant: int, category: int, words: list = ['дело', 'дела', 'дел']):
  try:
    return (verbose_number(response['analytics'][f'q20{defendant_or_claimant}{category}'], words), 
            money_sum_repr(response['analytics'][f's20{defendant_or_claimant}{category}']) + ' руб.')
  except KeyError:
    if verbose_number(response['analytics'][f'q20{defendant_or_claimant}{category}'], words):
      return verbose_number(response['analytics'][f'q20{defendant_or_claimant}{category}'], words)
    else:
      return None

# Количество дел в качестве ответчика, и их общая сумма
# Сделать с использованием декоратора и объединить с claimant_sum_count
def defendant_sum_and_count(response: Dict, sum_or_count: Union[list, str] = ['q', 's']) -> List:
  sum_count = []
  for category in range(1, 6):
    try:
      if category == 1:
        sum_count.append(
            f"{template_representation(response, 1, category)[0]} проиграно," + \
            f" на сумму {template_representation(response, 1, category)[1]}, "
        )
      elif category == 2:
        sum_count.append(
            f"{template_representation(response, 1, category)[0]} частично проиграно," + \
            f" на сумму {template_representation(response, 1, category)[1]}, "
        )
      elif category == 3:
        sum_count.append(
            f"{template_representation(response, 1, category)[0]} не проиграно," + \
            f" на сумму {template_representation(response, 1, category)[1]}, "
        )
      elif category == 4:
        sum_count.append(
            f"{template_representation(response, 1, category)[0]} на рассмотрении," + \
            f" на сумму {template_representation(response, 1, category)[1]}, "
        )
      else:
        sum_count.append(
            f"{template_representation(response, 1, category)[0]} с неопределенным исходом," + \
            f" на сумму {template_representation(response, 1, category)[1]}"
        )
    except KeyError:
      continue

  return sum_count

# Количество дел в качестве истца, и их общая сумма
# Сделать с использованием декоратора
def claimant_sum_and_count(response: Dict, sum_or_count: Union[list, str] = ['q', 's']) -> List:
  sum_count = []
  for category in range(1, 6):
    try:
      if category == 1:
        sum_count.append(
            f"{template_representation(response, 2, category)[0]} проиграно," + \
            f" на сумму {template_representation(response, 2, category)[1]}, "
        )
      elif category == 2:
        sum_count.append(
            f"{template_representation(response, 2, category)[0]} частично проиграно," + \
            f" на сумму {template_representation(response, 2, category)[1]}, "
        )
      elif category == 3:
        sum_count.append(
            f"{template_representation(response, 2, category)[0]} выиграно," + \
            f" на сумму {template_representation(response, 2, category)[1]}, "
        )
      elif category == 4:
        sum_count.append(
            f"{template_representation(response,2, category)[0]} на рассмотрении," + \
            f" на сумму {template_representation(response, 2, category)[1]}, "
        )
      else:
        sum_count.append(
            f"{template_representation(response, 2, category)[0]} с неопределенным исходом," + \
            f" на сумму {template_representation(response, 2, category)[1]}"
        )
    except KeyError:
      continue

  return sum_count

# Самые важные категории арбитражей в качестве ответчика
# Сделать с использованием декоратора
def most_valuable_arbitrations(response: Dict) -> str:
  valuable_arb = []
  for category in range(1, 6):
    try:
      if category == 1:
        valuable_arb.append(
            f"{template_representation(response, 3, category)[0]} связано с проведением процедуры банкротства, " + \
            f"на сумму {template_representation(response, 3, category)[1]}"
        )
      elif category == 2:
        valuable_arb.append(
            f"{template_representation(response, 3, category)[0]} связано с обязательствами по договорам займа, кредита, лизинга, " + \
            f"на сумму {template_representation(response, 3, category)[1]}"
        )
      elif category == 3:
        valuable_arb.append(
            f"{template_representation(response, 3, category)[0]} связано с налогами, " + \
            f"на сумму {template_representation(response, 3, category)[1]}"
        )
      elif category == 4:
        valuable_arb.append(
            f"{template_representation(response, 3, category)[0]} связано с оказанием услуг, " + \
            f"на сумму {template_representation(response, 3, category)[1]}"
        )
      else:
        valuable_arb.append(
            f"{template_representation(response, 3, category)[0]} с договорами поставки, " + \
            f"на сумму {template_representation(response, 3, category)[1]} "
        )
    except KeyError:
      continue

  if len(valuable_arb) > 1:
    return ', '.join(valuable_arb)
  else:
    return valuable_arb

# Для удобного отбражения
# Сделать из этого декоратор
def fssp_repr(topics: set, count: int, fssp_sum: float, flag: str = 'opened') -> str:
  if flag == 'opened':
    endings = (
      f'открытое исполнительное производство, на сумму {money_sum_repr(fssp_sum)} руб., предметом которого являлись: ',
      f'открытых исполнительных производства, на сумму {money_sum_repr(fssp_sum)} руб., предметом которых являлись: ',
      f'открытых исполнительных производств, на сумму {money_sum_repr(fssp_sum)} руб., предметом которых являлись: ' 
    )
    return (f"Имеется {verbose_number(count, endings)}{', '.join(topics)}")
  else:
    endings = (
      f'закрытое исполнительное производство, на сумму {money_sum_repr(fssp_sum)} руб., предметом которого являлись: ',
      f'закрытых исполнительных производства, на сумму {money_sum_repr(fssp_sum)} руб., предметом которых являлись: ',
      f'закрытых исполнительных производств, на сумму {money_sum_repr(fssp_sum)} руб., предметом которых являлись: '
    )
    return (f"Имеется {verbose_number(count, endings)}{', '.join(topics)}.")

# Открытые и закрытые исполнительные производства
def fssp_sum_and_count(response: Dict) -> str:
  count_open, count_close = 0, 0
  opened_sum, closed_sum = 0, 0
  opened_fssp, closed_fssp = set(), set()
  for executory in response['fssp']:
    try:
      executory['cancelDate']
      count_close += 1
      closed_sum += executory['sum']
      if executory['topic']:
        if executory['topic'].startswith('Иные взыскания'):
          closed_fssp.add('иные взыскания')
        else:
          closed_fssp.add(executory['topic'][0].lower() + executory['topic'][1:])
    except KeyError:
      count_open += 1
      try:
        opened_sum += executory['sum']
        if executory['topic']:
          if executory['topic'].startswith('Иные взыскания'):
            opened_fssp.add('иные взыскания')
          else:
            opened_fssp.add(executory['topic'][0].lower() + executory['topic'][1:])
      except KeyError:
        continue
      
  if closed_fssp and opened_fssp:
    closed = fssp_repr(closed_fssp, count_close, closed_sum, 'closed')
    opened = fssp_repr(opened_fssp, count_open, opened_sum, 'opened')

    return opened, closed
  elif closed_fssp:
    return fssp_repr(closed_fssp, count_close, closed_sum, 'closed')
  elif opened_fssp:
    return fssp_repr(opened_fssp, count_open, opened_sum, 'opened')
  else:
    return 'Информация отсутствует.'

def finance_code(response: Dict) -> str:
  try:
    return response['analytics']['e6014']
  except KeyError:
    return ''

# Гос. контракты в качестве участника и в качестве заказчика
def contracts_participant_and_customer(response: Dict) -> str:
  participant_customer = []
  endings = ('гос. контракте', 'гос. контрактах', 'гос. контрактах')
  for category in [3, 5]:
    try:
      if category == 3:
        participant_customer.append(
          f"{verbose_number(response['analytics'][f'q400{category}'], endings)} в качестве участника, " + \
          f"на сумму {money_sum_repr(response['analytics'][f's400{category}'])} руб."
        )
      else:
        participant_customer.append(
          f"{verbose_number(response['analytics'][f'q400{category}'], endings)} в качестве заказчика, " + \
          f"на сумму {money_sum_repr(response['analytics'][f's400{category}'])} руб."
        )
    except KeyError:
      participant_customer.append(None)
      continue

  return participant_customer

# Преобразовывает ответ сервера в словарь python
"""def response_to_dict(method: str) -> dict:
    try:
        res = requests.get(BASE_URL + method, params=payload)
        res.raise_for_status()

        return res.json()[0]
    except requests.HTTPError:
        return None  """ 

class ReportCreateMiddleware:
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        response = self._get_response(request)
        if request.method == 'POST':
            print(request.POST['inn'])
            inn_list = list(request.POST['inn'].split(', '))
            start = time()

            for inn in inn_list:
                payload = {'inn': inn, 'key': '3208d29d15c507395db770d0e65f3711e40374df'}

                responses = []
                for method in ['req', 'egrDetails', 'analytics', 'sites','contacts', 'fssp', 'buh']:
                    try:
                        res = requests.get(BASE_URL + method, params=payload)
                        res.raise_for_status()
                        responses.append(res.json()[0])
                    except requests.HTTPError:
                        responses.append(None)

                req, egr, analytics, sites, contacts, fssp, buh = responses
                
                # Здесь ужас, не смотрите
                try:
                    defendant_all_count = [
                    verbose_number(analytics['analytics']['q2002'], ('делу', 'делам', 'делам')),
                    verbose_number(analytics['analytics']['q2002'])
                    ]
                except KeyError:
                    defendant_all_count = None

                try:
                    defendant_all_sum = money_sum_repr(analytics['analytics']['s2002']) + ' руб.'
                except KeyError:
                    defendant_all_sum = None

                try:
                    claimant_all_count = [
                    verbose_number(analytics['analytics']['q2004'], ('делу', 'делам', 'делам')),
                    verbose_number(analytics['analytics']['q2004'])
                    ]
                except KeyError:
                    claimant_all_count = None

                try:
                    claimant_all_sum = money_sum_repr(analytics['analytics']['s2004']) + ' руб.'
                except KeyError:
                    claimant_all_sum = None

                try:
                    sites = ', '.join(sites['sites'][:2])
                except KeyError:
                    sites = None

                if len(inn) == 12:
                    type_of_UL = 'IP'

                    try:
                        dissolution_date = req[type_of_UL]['dissolutionDate']
                        status_text = req[type_of_UL]['status']['statusString']
                    except KeyError:
                        dissolution_date = status_text = None
                    
                    context = {
                        # Шапка
                        'name': f"ИП {req[type_of_UL]['fio']}",
                        'inn': inn,
                        'address': full_address(egr, type_of_UL),
                        'registration_date': registration_date(req, type_of_UL),
                        'dissolution_date': datetime.strptime(dissolution_date, '%Y-%m-%d').strftime('%d %B %Y г.') if dissolution_date else None,
                        'status_text': status_text,
                        'sites': sites,
                        'phones': ', '.join(contacts['contactPhones']['phones'][:2]) if contacts and contacts['contactPhones']['phones'] else None,
                        'activity': activity(egr),
                        # Арбитражи
                        'defendant_all_count': defendant_all_count, # Общее количество арбитражей в качестве ответчика
                        'defendant_all_sum': defendant_all_sum, # Общая сумма арбитражей в качестве ответчика
                        # 2011 проигранные, 2012 частично проигранные, 2013 не проигранные, 2014 на рассмотрении, 2015 неопределенный исход
                        'defendant_representation': defendant_sum_and_count(analytics),
                        'most_valuable_arbitrations': most_valuable_arbitrations(analytics),
                        # Арбитражи: истец
                        'claimant_all_count': claimant_all_count,
                        'claimant_all_sum': claimant_all_sum,
                        'claimant_representation': claimant_sum_and_count(analytics),
                        # ФССП
                        'fssp_count_and_sum': fssp_sum_and_count(fssp),
                        # Фин. анализ
                        'finance_analysis_code': finance_code(analytics),
                        # Гос. контракты
                        'participant': contracts_participant_and_customer(analytics)[0],
                        'customer': contracts_participant_and_customer(analytics)[1],
                    } # Контекст рендера для ИП
                else:
                    type_of_UL = 'UL'
                    try:
                        stated_capital = money_sum_repr(egr[type_of_UL]['statedCapital']['sum'])
                    except KeyError:
                        stated_capital = None

                    context = {
                        # Шапка
                        'name': req[type_of_UL]['legalName']['readable'],
                        'inn': inn,
                        'address': full_address(req, type_of_UL),
                        'registration_date': registration_date(req, type_of_UL),
                        'heads': heads(req, type_of_UL),
                        'founders': founders(egr, type_of_UL),
                        'sites': sites,
                        'phones': ', '.join(contacts['contactPhones']['phones'][:2]) if contacts and contacts['contactPhones']['phones'] else None,
                        'stated_capital': stated_capital,
                        'activity': activity(egr, type_of_UL),
                        # Арбитражи: ответчик
                        'defendant_all_count': defendant_all_count, # Общее количество арбитражей в качестве ответчика
                        'defendant_all_sum': defendant_all_sum, # Общая сумма арбитражей в качестве ответчика
                        # 2011 проигранные, 2012 частично проигранные, 2013 не проигранные, 2014 на рассмотрении, 2015 неопределенный исход
                        'defendant_representation': defendant_sum_and_count(analytics),
                        'most_valuable_arbitrations': most_valuable_arbitrations(analytics),
                        # Арбитражи: истец
                        'claimant_all_count': claimant_all_count,
                        'claimant_all_sum': claimant_all_sum,
                        'claimant_representation': claimant_sum_and_count(analytics),
                        # ФССП
                        'fssp_count_and_sum': fssp_sum_and_count(fssp),
                        # Фин. анализ
                        'finance_analysis_code': finance_code(analytics),
                        # Гос. контракты
                        'participant': contracts_participant_and_customer(analytics)[0] if contracts_participant_and_customer(analytics) else None,
                        'customer': contracts_participant_and_customer(analytics)[1] if contracts_participant_and_customer(analytics) else None,
                    } # Контекст рендера для ЮЛ

                file_name = re.sub(r'[<>"\*:/|\?\\]', '', context['name'])

                template = DocxTemplate('/home/grum231/prog/python/reports/template.docx')
                template.render(context)
                template.save(f'/mnt/c/Users/grum231/Desktop/{file_name}.docx')

                end = time()
                print(f"Время выполнения: {round(end - start, 2)} секунд")
                print(context['name'])
                #print(Company.report.url)

        return response