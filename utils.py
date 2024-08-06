# utils.py
import pandas as pd
from pathlib import Path
import streamlit as st

directory = Path(__file__).parent / "clean-data"

@st.cache_data
def load_nocs():
    return pd.read_csv(directory / "noc_regions.csv")

@st.cache_data
def load_bios():
    return pd.read_csv(directory / "bios_locs.csv")

@st.cache_data
def load_results():
    return pd.read_csv(directory / "results.csv")

def filter_bios(bios, country, country_dict):
    if country not in country_dict:
        return pd.DataFrame(columns=bios.columns)  # Boş bir DataFrame döndür
    bios = bios[bios['born_country'] == country_dict[country]]
    return bios[bios['lat'].notna() & bios['long'].notna()]

def filter_results(df, country, country_dict, include_winter, only_medalists):
    if country not in country_dict:
        return pd.DataFrame(columns=df.columns)  # Boş bir DataFrame döndür
    df = df[df['noc'] == country_dict[country]]
    if not include_winter:
        df = df[df['type'] == 'Summer']
    if only_medalists:
        df = df[df['medal'].notna()]
    return df

def get_medals(results, country, country_dict):
    if country not in country_dict:
        return pd.DataFrame(columns=['year', 'medal'])  # Boş bir DataFrame döndür
    medals = results[(results['medal'].notna()) & (~results['event'].str.endswith('(YOG)'))]
    medals_filtered = medals.drop_duplicates(['year', 'type', 'discipline', 'noc', 'event', 'medal'])
    medals_by_year = medals_filtered.groupby(['noc', 'year'])['medal'].count()
    if country_dict[country] not in medals_by_year.index:
        return pd.DataFrame(columns=['year', 'medal'])  # Boş bir DataFrame döndür
    medals_by_year = medals_by_year.loc[country_dict[country]]
    return medals_by_year.reset_index()
