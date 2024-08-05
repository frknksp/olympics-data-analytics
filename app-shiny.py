import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from shiny.express import ui, input, render
from shiny import reactive
import folium
from folium.plugins import HeatMap

ui.page_opts()
directory = Path(__file__).parent
nocs = pd.read_csv(directory / "clean-data" / "noc_regions.csv")

nocs['region'] = nocs['region'].astype(str)
country_dict = dict(zip(nocs['region'], nocs['NOC']))
#print(country_dict)
countries = sorted(nocs['region'].unique().tolist())

with ui.layout_sidebar():
    with ui.sidebar(open='open'):
        ui.input_select("country", "Select a country", countries, selected="Turkey")
        ui.input_checkbox("winter","Include winter months", value=True)
        ui.input_checkbox("medalist","only include medalists", value=False)

    with ui.card():
        "Medals"

        @render.plot()
        def show_medals():
            df = get_medals()
            plt.plot(df['year'], df['medal'])
            plt.xlabel('Year')
            plt.ylabel('Medal Count')
            plt.title('Medals by Year')

    with ui.card():
        "Heatmap of athletes"
        @render.ui()
        def show_heatmap():
            df = bios_df()
            m = folium.Map(location=[df['lat'].mean(), df['long'].mean()], zoom_start=2)
            heat_data = [[row['lat'], row['long']] for index, row in df.iterrows()]
            HeatMap(heat_data).add_to(m)
            return m

    with ui.card():    
        @render.data_frame
        def results():
            return result_df()
    
@reactive.calc
def bios_df():
    bios = pd.read_csv(directory / "clean-data" / "bios_locs.csv")
    bios = bios[bios['born_country'] == country_dict[input.country()]]
    country_df = bios[bios['lat'].notna() & bios['long'].notna()]
    return country_df

@reactive.calc
def result_df():
    df = pd.read_csv(directory / "clean-data" / "results.csv")
    
    selected_noc = country_dict[input.country()]
    df = df[df['noc'] == selected_noc]

    if not input.winter():
        df = df[df['type'] == 'Summer']
    if input.medalist():
        df = df[df['medal'].notna()]

    return df
@reactive.calc
def get_medals():
    results = result_df()
    medals = results[(results['medal'].notna()) & (~results['event'].str.endswith('(YOG)'))]
    medals_filtered = medals.drop_duplicates(['year','type','discipline','noc','event','medal'])
    #print(medals_filtered)
    models_by_year = medals_filtered.groupby(['noc','year'])['medal'].count().loc[country_dict[input.country()]]
    #print(models_by_year.reset_index())
    return models_by_year.reset_index()