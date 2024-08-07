# utils.py
import pandas as pd
from pathlib import Path
import streamlit as st

directory = Path(__file__).parent / "clean-data"

@st.cache_data
def load_nocs():
    nocs = pd.read_csv(directory / "noc_regions.csv")
    # NOC'ları bölgelere göre gruplandır
    noc_groups = nocs.groupby('region')['NOC'].apply(list).reset_index()
    # Sözlük oluştur
    country_dict = dict(zip(noc_groups['region'], noc_groups['NOC']))
    return nocs, country_dict

@st.cache_data
def load_bios():
    return pd.read_csv(directory / "bios_locs.csv")

@st.cache_data
def load_results():
    return pd.read_csv(directory / "results.csv")

def filter_bios(bios, country, country_dict):
    if country not in country_dict:
        return pd.DataFrame(columns=bios.columns)
    filtered = bios[bios['born_country'].isin(country_dict[country])]
    return filtered[filtered['lat'].notna() & filtered['long'].notna()]

def filter_results(df, country, country_dict, include_winter, only_medalists):
    if country not in country_dict:
        return pd.DataFrame(columns=df.columns)
    df = df[df['noc'].isin(country_dict[country])]
    if not include_winter:
        df = df[df['type'] == 'Summer']
    if only_medalists:
        df = df[df['medal'].notna()]
    return df

def get_medals(results, country, country_dict):
    if country not in country_dict:
        return pd.DataFrame(columns=['year', 'medal'])
    medals = results[(results['medal'].notna()) & (~results['event'].str.endswith('(YOG)'))]
    medals_filtered = medals.drop_duplicates(['year', 'type', 'discipline', 'noc', 'event', 'medal'])
    medals_by_year = medals_filtered[medals_filtered['noc'].isin(country_dict[country])].groupby('year')['medal'].count()
    return medals_by_year.reset_index()