"""
Tento modul slouží k načtení různých zdrojů dat. V tuto chvíli umožňuje načíst \
data o projektech a uchazečích/příjemcích ze "zdroje pravdy", IS VaVaI a STARFOS.
"""

import gspread
import pandas as pd

import requests
from bs4 import BeautifulSoup

import string

from tqdm import tqdm

from typing import Union


class Projects:
    """ Třída, která načítá a reprezentuje tabulku projektů.

    Funguje pouze v rámci Google Colab prostředí.

    :param projects: DataFrame načtených dat ze zdroje nebo z nově vytvořené (vyfiltrované) instance
    :type projects: DataFrame
    :param summary: DataFrame s agregovanými údaji na úrovni veřejných soutěží
    :type summary: DataFrame
    """

    def __init__(self, creds_or_df: object):
        """ Kontstruktor, který načte data do DataFrame, očistí finanční hodnoty a vytvoří agregovanou tabulku.

        :param creds_or_df: údaje, které slouží k authenizaci v rámci Google Colab nebo přímo DataFrame projektu
        """
        self.projects = None
        if isinstance(creds_or_df, pd.DataFrame):
            self.projects = creds_or_df
        else:
            self.projects = self._get_projects(creds_or_df)
            self._finance_cleaning('Náklady celkem')
            self._finance_cleaning('Podpora celkem')
            self._finance_cleaning('Ostatní celkem')
        self.summary = self.create_summary()

    def _get_projects(self, creds_or_df: object) -> pd.DataFrame:
        """ Načte data o projektech ze "zdroje pravdy" z googlesheets uloženého na Google disku.

        Lze použít pouze v rámci Google Colab prostředí.

        :param creds_or_df: údaje, které slouží k authenizaci v rámci Google Colab
        :return: DataFrame načtených dat ze zdroje
        """
        file_id = "1Ax1OYkdg3IA1YZki0fePizgQR6zOuzq7VGhFgeMorDQ"

        gc = gspread.authorize(creds_or_df)
        sht = gc.open_by_key(file_id)
        worksheet = sht.get_worksheet(0)

        rows = worksheet.get_all_values()

        df = pd.DataFrame.from_records(rows[1:], columns=rows[0])

        return df

    def _finance_cleaning(self, column_name: str):
        """ Interní funkce, která očistí finanční data.

        :param column_name: název sloupce, ve kterém se mají finanční data očistit
        """

        self.projects[column_name].fillna(0, inplace=True)
        self.projects[column_name] = self.projects[column_name].str.replace(',', '.')
        self.projects[column_name] = self.projects[column_name].replace('', '0')
        self.projects[column_name] = self.projects[column_name].astype(float)

    def create_summary(self, level: str = 'cfp') -> pd.DataFrame:
        """ Vytvoří agregovaný souhrn buď na úrovni veřejných soutěží (defaultní) nebo na úrovni programů.

        :param level: určuje, na jaké úrovni se provede agregace

                      * 'cfp' (defaultní) - na úrovni veřejných soutěží
                      * 'prog' - na úrovni programů
        :return: agregovaný DataFrame, který obsahuje:

                * Počet podaných projektů
                * Počet podpořených projektů
                * Náklady podpořených projektů
                * Podpora podpořených projektů
        """
        if level not in ['cfp', 'prog']:
            raise ValueError('Neexistující forma agregace.')

        temp_df = self.projects.copy()
        temp_df['Podpořené'] = temp_df.apply(
            lambda x: 'Ano' if x['Fáze projektu'] in ['Realizace', 'Implementace', 'Ukončené'] else 'Ne', axis=1)
        submitted = temp_df.groupby(['Kód programu', 'Kód VS']).agg(
            {'Kód projektu': 'count', 'Náklady celkem': 'sum', 'Podpora celkem': 'sum'}).reset_index()
        funded = temp_df[temp_df['Podpořené'] == 'Ano'].groupby(['Kód programu', 'Kód VS']).agg(
            {'Kód projektu': 'count', 'Náklady celkem': 'sum', 'Podpora celkem': 'sum'}).reset_index()

        summary_df = pd.merge(submitted[['Kód programu', 'Kód VS', 'Kód projektu']], funded, how='inner',
                              on=['Kód programu', 'Kód VS'])
        summary_df.columns = ['Kód programu', 'Kód VS', 'Podané', 'Podpořené', 'Náklady', 'Podpora']

        if level == 'cfp':
            pass
        elif level == 'prog':
            summary_df = summary_df.groupby('Kód programu').agg('sum', numeric_only=True).reset_index()

        return summary_df

    def select_programme(self, *args: str) -> 'Projects':
        """ Vyfiltruje tabulku tak, aby obsahovala pouze projekty vybraných programů.

        :param args: kódy programů, které se mají vyfiltrovat
        :return: nová instance třídy Projects s vyfiltrovanými údaji
        :raise: ValueError
        """

        existing_programmes = self.projects['Kód programu'].unique()

        missing_programmes = [prog for prog in args if prog not in existing_programmes]

        if missing_programmes:
            raise ValueError(f'Programy {missing_programmes} neexistují.')

        else:
            programme_list = [prog for prog in args]
            select_df = self.projects[self.projects['Kód programu'].isin(programme_list)].reset_index(drop=True)
            return Projects(select_df)  # todo maybe another class Programms?

    def select_cfp(self, *args: str) -> 'Projects':
        """ Vyfiltruje tabulku tak, aby obsahovala pouze projekty vybraných veřejných soutěží.

        :param args: kódy veřejných soutěží, které se mají vyfiltrovat
        :return: nová instance třídy Projects s vyfiltrovanými údaji
        :raise: ValueError
        """
        existing_cfp = self.projects['Kód VS'].unique()

        missing_cfp = [cfp for cfp in args if cfp not in existing_cfp]

        if missing_cfp:
            raise ValueError(f'Veřejné soutěže {missing_cfp} neexistují.')

        else:
            cfp_list = [cfp for cfp in args]
            select_df = self.projects[self.projects['Kód VS'].isin(cfp_list)].reset_index(drop=True)
            return Projects(select_df)

    def select_funded(self) -> 'Projects':
        """ Vyfiltruje tabulku tak, aby obsahovala pouze podpořené projekty.

        :return: nová instance třídy Projects s vyfiltrovanými údaji
        """
        funded_states = ['Realizace', 'Implementace', 'Ukončené']
        select_df = self.projects[self.projects['Fáze projektu'].isin(funded_states)].reset_index(drop=True)
        return Projects(select_df)


def projects_finance(creds_or_df: object) -> pd.DataFrame:
    """ Načte data o financích projektů ze "zdroje pravdy" z googlesheets uloženého na Google disku.

    Finance jsou v rozdělení po jednotlivých letech.
    Lze použít pouze v rámci Google Colab prostředí.

    :param creds_or_df: údaje, které slouží k authenizaci v rámci Google Colab
    :return: DataFrame načtených dat ze zdroje
    """
    file_id = "1Ax1OYkdg3IA1YZki0fePizgQR6zOuzq7VGhFgeMorDQ"

    gc = gspread.authorize(creds_or_df)
    sht = gc.open_by_key(file_id)
    worksheet = sht.get_worksheet(1)

    rows = worksheet.get_all_values()

    df = pd.DataFrame.from_records(rows[1:], columns=rows[0])
    return df


def organizations(creds_or_df: object) -> pd.DataFrame:
    """ Načte data o uchazečích/příjemcích ze "zdroje pravdy" z googlesheets uloženého na Google disku.

    Lze použít pouze v rámci Google Colab prostředí.

    :param creds_or_df: údaje, které slouží k authenizaci v rámci Google Colab
    :return: DataFrame načtených dat ze zdroje
    """
    file_id = "1h7HpPn-G0_XY2gb_sExAQDkzR1TswGUH_2FuHCWhbRg"

    gc = gspread.authorize(creds_or_df)
    sht = gc.open_by_key(file_id)
    worksheet = sht.get_worksheet(0)

    rows = worksheet.get_all_values()

    df = pd.DataFrame.from_records(rows[1:], columns=rows[0])
    return df


def organizations_finance(creds_or_df: object) -> pd.DataFrame:
    """ Načte data o financích uchazečů/příjemců ze "zdroje pravdy" z googlesheets uloženého na Google disku.

    Finance jsou v rozdělení po jednotlivých letech.
    Lze použít pouze v rámci Google Colab prostředí.

    :param creds_or_df: údaje, které slouží k authenizaci v rámci Google Colab
    :return: DataFrame načtených dat ze zdroje
    """
    file_id = "1h7HpPn-G0_XY2gb_sExAQDkzR1TswGUH_2FuHCWhbRg"

    gc = gspread.authorize(creds_or_df)
    sht = gc.open_by_key(file_id)
    worksheet = sht.get_worksheet(1)

    rows = worksheet.get_all_values()

    df = pd.DataFrame.from_records(rows[1:], columns=rows[0])
    return df


def isvav_projects() -> pd.DataFrame:
    """ Načte data o příjemcích z otevřených dat IS VaVaI.

    Data jsou aktualizovaná cca jednou za čtvrt roku.

    :return: DataFrame načtených dat ze zdroje
    """
    df = pd.read_csv("https://www.isvavai.cz/dokumenty/opendata/CEP-projekty.csv")
    return df


def isvav_organizations() -> pd.DataFrame:
    """ Načte data o projektech z otevřených dat IS VaVaI.

    Data jsou aktualizovaná cca jednou za čtvrt roku.

    :return: DataFrame načtených dat ze zdroje
    """
    df = pd.read_csv("https://www.isvavai.cz/dokumenty/opendata/CEP-ucastnici.csv")
    return df


def results(creds_or_df: object) -> pd.DataFrame:
    """ Načte data o výsledcích ze "zdroje pravdy" z googlesheets uloženého na Google disku.

    Lze použít pouze v rámci Google Colab prostředí.

    :param creds_or_df: údaje, které slouží k authenizaci v rámci Google Colab
    :return: DataFrame načtených dat ze zdroje
    """
    file_id = "1eSE6gB8bwuP6OVwVVhQojQLS6aPi_q8t7gK6VhPyiRw"

    gc = gspread.authorize(creds_or_df)
    sht = gc.open_by_key(file_id)
    worksheet = sht.get_worksheet(0)

    rows = worksheet.get_all_values()

    df = pd.DataFrame.from_records(rows[1:], columns=rows[0])
    return df


def cfp(creds_or_df: object) -> pd.DataFrame:
    """ Načte data o veřejných soutěží z googlesheets uloženého na Google disku.

    Lze použít pouze v rámci Google Colab prostředí.

    :param creds_or_df: údaje, které slouží k authenizaci v rámci Google Colab
    :return: DataFrame načtených dat ze zdroje
    """
    file_id = "1FaVienG6ceJGdqSTyD5tpsUsRGxgPii6BWOL73Vk2_s"

    gc = gspread.authorize(creds_or_df)
    sht = gc.open_by_key(file_id)
    worksheet = sht.get_worksheet(1)

    rows = worksheet.get_all_values()

    df = pd.DataFrame.from_records(rows[1:], columns=rows[0]).iloc[:, 0:15]
    return df


def get_providers() -> list:
    """ Stáhne seznam kódu všech poskytovatelů v IS VaVaI.

    Data jsou získána pomocí web scrapingu z webu IS VaVaI.

    :return: seznam kódu poskytovatelů
    """

    base_url = 'https://www.isvavai.cz/cea?s=poskytovatele&n='

    provider_list = []

    for page in range(0, 2):
        url = base_url + str(page)
        html = requests.get(url).content
        parsed_html = BeautifulSoup(html, 'html.parser')

        for i in parsed_html.findAll('b', attrs={'class': 'abbr'}):
            provider_list.append(i.find('a').text)

    # nejsou v seznamu aktivních poskytovatelů, jedná se o historická ministerstva
    # ministerstvo hospodářství a ministesrtvo informatiky
    provider_list.extend(['MH0', 'MI0'])

    return provider_list


def starfos_projects(prog_select: Union[str, list] = None
                     , prov_select: Union[str, list] = None) -> Union[pd.DataFrame, dict[str]]:
    """ Stáhne ze STARFOS projekty buď podle kódů programů nebo kódů poskytovatelů

    Volá API endpoint, který slouží pro vytváření exportů. Výstup exportu převede na DataFrame.

    :param prog_select: seznam programů
    :param prov_select: seznam poskytovatelů
    :return: projekty ze STARFOS
    """

    url = 'https://old.starfos.tacr.cz/api/starfos/export'
    headers = {'content-type': 'application/json'}

    common_query_template = {
        "collection": "isvav_project",
        "language_ui": "cs",
        "format": "xlsx",
        "limit": 0,
        "columns": ["code", "name", "anot", "name_en", "anot_en", "x_solve_begin_year", "x_solve_end_year"],
        "filters": {}
    }

    if prog_select:
        programme_filter = {
            "programme__code": {
                "option_codes": prog_select
            }
        }
        common_query_template['filters'].update(programme_filter)

    if prov_select:
        provider_filter = {
            "programme__funder__code": {
                "option_codes": prov_select
            }
        }
        common_query_template['filters'].update(provider_filter)

    try:
        r = requests.post(url, headers=headers, json=common_query_template, stream=True)
        r.raise_for_status()
        df = pd.read_excel(r.content)
        return df
    except requests.exceptions.RequestException as e:
        if not prog_select or prov_select:
            return {'error': str(e),
                    'additional_info': 'You need to enter at least one programme (prog_select) or provider (prov_select).'}
        else:
            return {'error': str(e), 'additional_info': 'Unknown error.'}


def starfos_projects_all() -> pd.DataFrame:
    """ Stáhne ze STARFOS všechny projekty.

    Postupně volá API endpoint, který slouží pro vytváření exportu, za jednotlivé poskytovatele. Výjimku tvoří GA ČR,
    který přesahuje maximální limit 20 000 záznamů, proto se volá po jednotlivých programech. Výstupy se skládají do
    jednoho DataFrame.

    :return: projekty ze STARFOS
    """

    url = 'https://old.starfos.tacr.cz/api/starfos/export'
    headers = {'content-type': 'application/json'}

    df_list = []

    provider_list = get_providers()

    common_query_template = {
        "collection": "isvav_project",
        "language_ui": "cs",
        "format": "xlsx",
        "limit": 0,
        "columns": ["code", "name", "anot", "name_en", "anot_en", "x_solve_begin_year", "x_solve_end_year"],
        "filters": {}
    }

    for prov in tqdm(provider_list):
        query_template = common_query_template.copy()

        if prov == 'GA0':
            programme_list = ['G' + i for i in string.ascii_uppercase]
            for prog in programme_list:
                query_template['filters'] = {
                    "programme__code": {
                        "option_codes": [prog]
                    }
                }
                r = requests.post(url, headers=headers, json=query_template, stream=True)
                df = pd.read_excel(r.content)
                df_list.append(df)
        else:
            query_template['filters'] = {
                "programme__funder__code": {
                    "option_codes": [prov]
                }
            }

            r = requests.post(url, headers=headers, json=query_template, stream=True)
            df = pd.read_excel(r.content)
            df_list.append(df)
    df_concat = pd.concat(df_list).reset_index(drop=True)
    return df_concat
