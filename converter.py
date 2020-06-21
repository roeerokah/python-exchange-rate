from xml.etree import ElementTree as ET
import requests
import uuid
from decimal import Decimal
import calendar

BASE_URL = 'https://sdw-wsrest.ecb.europa.eu/service/data'
GENERIC = '{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}'
MESSAGE = '{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message}'


def converter(from_currency_list, to_currency_list, from_date, to_date):
    base = 'EUR'
    headers = {
        "authorization": "Basic ZXV1c2VybmFtZTpwYXNzd29yZA=="
    }
    currencies = {}
    form_currency_string = '+'.join(from_currency_list)

    from_date = substract_time_if_needed(from_date)
    for to in to_currency_list:
        if to != base:
            form_currency_string += "+" + to

    url = BASE_URL+'/EXR/D.'+form_currency_string+'..SP00.A?detail=dataonly&startPeriod=' + from_date + '&endPeriod='\
          + to_date
    print(url)

    res = requests.get(url, headers=headers)
    if res.status_code == 404:
        raise Exception('the wanted Currencies was not found')
    if not res.text:
        raise Exception('no values in this dates')

    tree = ET.fromstring(res.text)

    data = tree.find(MESSAGE + 'DataSet')

    for series in data:
        from_currency = ''

        currency_metadata = series.find(GENERIC + 'SeriesKey')
        for key in currency_metadata:
            key_id = key.attrib.get('id')
            if 'CURRENCY' == key_id:
                from_currency = key.attrib.get('value')
                currencies[from_currency] = {}

        obslist = series.findall(GENERIC + 'Obs')
        for obs in obslist:

            rate_date = obs.find(GENERIC + 'ObsDimension')
            rate_value = obs.find(GENERIC + 'ObsValue')
            date = rate_date.attrib.get('value')

            value = rate_value.attrib.get('value')

            currencies[from_currency][date] = value

    print(currencies)

    build_xml_result(currencies, from_currency_list, to_currency_list)


def substract_time_if_needed(from_date):
    from datetime import timedelta, datetime
    from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
    result = from_datetime
    curr_day = calendar.day_name[from_datetime.weekday()]

    if 'Saturday' in curr_day:
        result = from_datetime - timedelta(days=1)
    elif 'Sunday' in curr_day:
        result = from_datetime - timedelta(days=2)

    return str(result.date())


def build_xml_result(currencies, from_currency_list, to_currency_list):
    from datetime import date
    result = ET.Element('data', attrib={'id': str(uuid.uuid4()), 'date': str(date.today())})

    for from_cur in from_currency_list:
        for to_cur in to_currency_list:
            if from_cur is to_cur:
                continue
            series_result = ET.SubElement(result, 'currency')
            series_result.set('from', from_cur)
            series_result.set('to', to_cur)
            if from_cur is 'EUR':
                for date in currencies[to_cur]:
                    val = str(currencies[to_cur][date])
                    day_result = ET.SubElement(series_result, 'day')
                    day_result.set('time', date)
                    day_result.set('value', val)
            elif to_cur is 'EUR':
                for date in currencies[from_cur]:
                    val = str(Decimal(1) / Decimal(currencies[from_cur][date]))
                    day_result = ET.SubElement(series_result, 'day')
                    day_result.set('time', date)
                    day_result.set('value', val)
            else:
                for date in currencies[from_cur]:
                    val = str(Decimal(1) / Decimal(currencies[from_cur][date]) * Decimal(currencies[to_cur][date]))
                    day_result = ET.SubElement(series_result, 'day')
                    day_result.set('time', date)
                    day_result.set('value', val)

    indent(result)
    result_tree = ET.ElementTree(result)

    result_tree.write("file.xml", xml_declaration=True, encoding='utf-8', method="xml")


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


converter(['ILS', 'USD'], ['JPY', 'EUR'], '2020-06-18', '2020-06-21')
