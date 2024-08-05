import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

# Veri yolları ve yükleme
directory = Path(__file__).parent
nocs = pd.read_csv(directory / "clean-data" / "noc_regions.csv")

nocs['region'] = nocs['region'].astype(str)
country_dict = dict(zip(nocs['region'], nocs['NOC']))
countries = sorted(nocs['region'].unique().tolist())

# Yardımcı fonksiyonlar
@st.cache_data
def load_bios():
    return pd.read_csv(directory / "clean-data" / "bios_locs.csv")

@st.cache_data
def load_results():
    return pd.read_csv(directory / "clean-data" / "results.csv")

def filter_bios(bios, country):
    bios = bios[bios['born_country'] == country_dict[country]]
    return bios[bios['lat'].notna() & bios['long'].notna()]

def filter_results(df, country, include_winter, only_medalists):
    df = df[df['noc'] == country_dict[country]]
    if not include_winter:
        df = df[df['type'] == 'Summer']
    if only_medalists:
        df = df[df['medal'].notna()]
    return df

def get_medals(results, country):
    medals = results[(results['medal'].notna()) & (~results['event'].str.endswith('(YOG)'))]
    medals_filtered = medals.drop_duplicates(['year','type','discipline','noc','event','medal'])
    models_by_year = medals_filtered.groupby(['noc','year'])['medal'].count().loc[country_dict[country]]
    return models_by_year.reset_index()

# Streamlit UI
st.title("Olympic Data Analysis")

# Sidebar
country = st.sidebar.selectbox("Select a country", countries, index=countries.index("Turkey"))
include_winter = st.sidebar.checkbox("Include winter months", value=True)
only_medalists = st.sidebar.checkbox("Only include medalists", value=False)

# Load data
bios = load_bios()
results = load_results()

# Filter data
filtered_bios = filter_bios(bios, country)
filtered_results = filter_results(results, country, include_winter, only_medalists)
medals_data = get_medals(filtered_results, country)

# Medals plot
st.header("Medals")
fig, ax = plt.subplots()
ax.plot(medals_data['year'], medals_data['medal'])
ax.set_xlabel('Year')
ax.set_ylabel('Medal Count')
ax.set_title('Medals by Year')
st.pyplot(fig)

# Heatmap
st.header("Heatmap of athletes")
m = folium.Map(location=[filtered_bios['lat'].mean(), filtered_bios['long'].mean()], zoom_start=2)
heat_data = [[row['lat'], row['long']] for index, row in filtered_bios.iterrows()]
HeatMap(heat_data).add_to(m)
folium_static(m)

# Results table
st.header("Results")
st.dataframe(filtered_results)