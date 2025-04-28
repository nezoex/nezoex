import numpy as np
import pandas as pd
import os
import patoolib
import requests
import sqlalchemy
import urllib
import re
import datetime
import pytz

engine = sqlalchemy.create_engine('####', echo = True)
con = engine.connect()
# Для годовых данных (Показатели СЭР)
path
df_dimension = pd.read_excel(path + r'\Показатели СЭР.xlsx', sheet_name = 'period_dimension_indicators', header = 0)
dimension_match = pd.read_excel(path + r'\Показатели СЭР.xlsx', sheet_name = 'dimension_match', header = 0)
df_dimension = df_dimension.fillna('1')

def dashboard_upload(indicator_id:str, years=15, dimension_match:pd.DataFrame=dimension_match, df_dimension:pd.DataFrame=df_dimension, token:str):
    
    df_dimension = df_dimension[['indicator_id', 'schema', 'table', 'value_column', 'math_transform', 'period_column', 'filter_1_column', 'filter_1_value',
                                                            'filter_2_column', 'filter_2_value', 'IndicatorType']]
    
    dimension_match = dimension_match[dimension_match['indicator_id'] == indicator_id]
    df_dimension = df_dimension[df_dimension['indicator_id'] == indicator_id]
    df_dimension = df_dimension.reset_index()
    period = df_dimension['period_column'][0]
    value_column = df_dimension['value_column'][0]
    math_transform = df_dimension['math_transform'][0]
    table = df_dimension['table'][0]
    schema = df_dimension['schema'][0]
    indicator_type = df_dimension['IndicatorType'][0]
    
    filter_1 = df_dimension['filter_1_column'][0]
    filter_1_value = "', '".join(df_dimension['filter_1_value'])
    filter_2 = df_dimension['filter_2_column'][0]
    filter_2_value = df_dimension['filter_2_value'][0]
    if indicator_type == 'Годовой':
        if filter_2 != '1':
            filter_query = f" AND [{filter_2}] = ('{filter_2_value}')"
        else:
            filter_query = f"" 
        if period != 'Год':
            date_method = f" AND MONTH([{period}]) = 12 AND "
            WORD = f"YEAR"
        else:
            date_method = f"AND "
            WORD = f""
        if filter_2 != '1':
            filter_query = f" AND [{filter_2}] = ('{filter_2_value}')"
        else:
            filter_query = f"" 
        df_sql= pd.read_sql_query(
            f"""
            SELECT [{period}], [{filter_1}], [{value_column}]/{math_transform}
            FROM [MAIN].[{schema}].[{table}]
            WHERE [{filter_1}] IN ('{filter_1_value}')
                {date_method}{WORD}([{period}]) >= (
                    SELECT MAX({WORD}([{period}]))-{years}
                    FROM [MAIN].[{schema}].[{table}]
                    WHERE [{filter_1}] IN ('{filter_1_value}')){filter_query}
            """,
            con=con
            )
    if indicator_type == 'Оперативный':
        if filter_2 != '1':
            filter_query = f" AND [{filter_2}] = ('{filter_2_value}')"
        else:
            filter_query = f"" 
        df_sql= pd.read_sql_query(
            f"""
        SELECT [{period}], [{filter_1}], [{value_column}]/{math_transform}
            FROM [MAIN].[{schema}].[{table}]
            WHERE [{filter_1}] IN ('{filter_1_value}')
                AND YEAR([{period}]) >= (
                    SELECT MAX(YEAR([{period}]))-1
                    FROM [MAIN].[{schema}].[{table}]
                    WHERE [{filter_1}] IN ('{filter_1_value}')){filter_query}
            """,
            con=con
            )
    if (period == 'Период' or "Дата") and indicator_type == 'Годовой':
        replace_method = df_sql[df_dimension['period_column'][0]] = df_sql[df_dimension['period_column'][0]].astype(str). \
            replace(r'-12-\d{2}', '', regex = True)
        df_sql[period] = pd.to_datetime("01.01." + df_sql[period].astype(str)).dt.date
    else:
        replace_method = ""
    replace_method
    if period == 'Год' and indicator_type == 'Годовой':
        df_sql[period] = pd.to_datetime("01.01." + df_sql[period].astype(str)).dt.date
    if indicator_id == 2779: # МСП Количество субъектов
        df_sql['Дата']  = pd.to_datetime(df_sql['Дата'].astype(str).replace(r'(\d{4}-\d{2})-10', r'\1-01', regex = True)).dt.date
    if indicator_id == 2788: # МСП Среднесписочная численность работников
        df_sql['Дата']  = pd.to_datetime(df_sql['Дата'].astype(str).replace(r'(\d{4}-\d{2})-31', r'\1-01', regex = True)).dt.date
        df_sql['Дата']  = pd.to_datetime(df_sql['Дата'].astype(str).replace(r'(\d{4}-\d{2})-29', r'\1-01', regex = True)).dt.date
        df_sql['Дата']  = pd.to_datetime(df_sql['Дата'].astype(str).replace(r'(\d{4}-\d{2})-28', r'\1-01', regex = True)).dt.date
        df_sql['Дата']  = pd.to_datetime(df_sql['Дата'].astype(str).replace(r'(\d{4}-\d{2})-30', r'\1-01', regex = True)).dt.date
    df_sql = df_sql.dropna()
    df_sql = df_sql.drop_duplicates()
    df_pivot = df_sql.pivot(columns = period, index=filter_1).sort_index(ascending=False).reset_index(col_level=1, names='region')
    df_pivot.insert(0, ('', 'chart_hex_color'), ['#C00000', '#7F7F7F'])
    df_pivot.columns = df_pivot.columns.droplevel(level=0)
    df_pivot = df_pivot.drop(columns = 'region')
    df_dimension_query = dimension_match.query(f"indicator_id == {indicator_id}")
    df_dimension_query['region'] = ['г. Москва', 'Российская Федерация']
    df_overall = df_dimension_query[['short_name', 'chart_hex_color', 'lvl', 'top_chart_disabled', 'bottom_chart_disabled', 'default_order', 'indicator_id', 'region', 'name']].merge(df_pivot, how = 'inner', on = 'chart_hex_color')
    df_overall = df_overall.drop(columns=['default_order', 'indicator_id', 'region'])
    df_overall['lvl'] = [1, 2]
    df_overall = df_overall.fillna('')
    if indicator_id == 2792: #ВРП
            df_overall= df_overall.drop(df_overall[df_overall['short_name'] == 'РФ'].index) 
            df_overall = df_overall.reset_index()
            df_overall = df_overall.drop(columns = 'index')
            df_overall['lvl'] = 1
    if indicator_id == 2710 or indicator_id == 2673: # Оборот розничной торговли
        df_overall.loc[df_overall['name']=='Москва', df_overall.columns[6:]]/=1000
    df_overall.to_excel('post_request.xlsx', index = False)
    with open(r"post_request.xlsx", "rb") as f:
        file = f.read()
    headers = {
        "Accept": "application/json",
    }

    response = requests.post(
        f"########",
        headers=headers,
        files={
            "file": (
                'post_request.xlsx',
                file,
                '#########',
                {}
            )
        },
        verify=False
    )
    
    os.remove('post_request.xlsx')
    assert response.json()['status'] == 'success', response.json()
    return df_overall
dashboard_upload(2705)
dashboard_upload(2706)
dashboard_upload(2792)
dashboard_upload(2796)
dashboard_upload(2780)
dashboard_upload(2709)
dashboard_upload(2789)
dashboard_upload(2798)
dashboard_upload(2718, 12)
dashboard_upload(2777)
dashboard_upload(2710)
dashboard_upload(2711)
dashboard_upload(2712)
dashboard_upload(2713)
dashboard_upload(2714)
dashboard_upload(2715)
dashboard_upload(2768)
dashboard_upload(2769)
dashboard_upload(2761)
dashboard_upload(2762)
dashboard_upload(2784)
dashboard_upload(2781)
dashboard_upload(2707)
dashboard_upload(2708)
dashboard_upload(2660)
dashboard_upload(2662)
dashboard_upload(2787)
dashboard_upload(2626)
dashboard_upload(2625)
dashboard_upload(2797)
dashboard_upload(2682)
dashboard_upload(2702)
dashboard_upload(2790)
dashboard_upload(2791)
dashboard_upload(2673)
dashboard_upload(2674)
dashboard_upload(2676)
dashboard_upload(2677)
dashboard_upload(2678)
dashboard_upload(2679)
dashboard_upload(2785)
dashboard_upload(2786)
dashboard_upload(2682)
dashboard_upload(2683)
dashboard_upload(2779)
dashboard_upload(2788)
dashboard_upload(2701)
dashboard_upload(2702)