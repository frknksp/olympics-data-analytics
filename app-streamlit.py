import streamlit as st
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import pandas as pd

from utils import load_nocs, load_bios, load_results, filter_bios, filter_results, get_medals

def load_data():
    bios = load_bios()
    results = load_results()
    nocs = load_nocs()
    nocs['region'] = nocs['region'].astype(str)
    country_dict = dict(zip(nocs['region'], nocs['NOC']))
    countries = sorted(nocs['region'].unique().tolist())
    return bios, results, nocs, country_dict, countries

def create_sidebar(countries):
    st.sidebar.title("Filters")
    country = st.sidebar.selectbox("Select a country", countries, index=countries.index("Turkey"))
    include_winter = st.sidebar.checkbox("Include winter months", value=True)
    only_medalists = st.sidebar.checkbox("Only include medalists", value=False)
    return country, include_winter, only_medalists

def plot_medals(medals_data):
    if not medals_data.empty:
        fig, ax = plt.subplots()
        ax.plot(medals_data['year'], medals_data['medal'], marker='o')
        ax.set_xlabel('Year')
        ax.set_ylabel('Medal Count')
        ax.set_title('Medals by Year')
        st.pyplot(fig)
    else:
        st.write("No medal data available")

def create_heatmap(filtered_bios):
    if not filtered_bios.empty:
        m = folium.Map(location=[filtered_bios['lat'].mean(), filtered_bios['long'].mean()], zoom_start=2)
        heat_data = [[row['lat'], row['long']] for index, row in filtered_bios.iterrows()]
        HeatMap(heat_data).add_to(m)
        folium_static(m)
    else:
        st.write("No athlete birthplace data available")

def display_results(filtered_results):
    if not filtered_results.empty:
        filtered_results_reset = filtered_results.reset_index(drop=True)
        
        for col in filtered_results_reset.columns:
            if filtered_results_reset[col].dtype == 'object':
                try:
                    filtered_results_reset[col] = pd.to_numeric(filtered_results_reset[col])
                except ValueError:
                    pass
            elif filtered_results_reset[col].dtype == 'float64' and filtered_results_reset[col].apply(lambda x: x.is_integer()).all():
                filtered_results_reset[col] = filtered_results_reset[col].astype(int)

        #st.dataframe(filtered_results_reset)
        st.dataframe(
        filtered_results_reset,
        column_config={
            "year": st.column_config.NumberColumn(
                "Year",
                format="%d"
            ),
            "athlete_id": st.column_config.NumberColumn(
                "Athlete ID",
                format="%d" 
            )
        }
        )
    else:
        st.write("No results data available")

def calculate_medals(filtered_results, country, country_dict):
    if not filtered_results.empty:
        medals = filtered_results[(filtered_results['medal'].notna()) & (~filtered_results['event'].str.endswith('(YOG)'))]
        medals_filtered = medals.drop_duplicates(['year', 'type', 'discipline', 'noc', 'event', 'medal'])
        
        if country_dict[country] in medals_filtered['noc'].values:
            medals_count = medals_filtered.groupby(['noc'])['medal'].value_counts().loc[country_dict[country]]

            total_gold = medals_count.get('Gold', 0)
            total_silver = medals_count.get('Silver', 0)
            total_bronze = medals_count.get('Bronze', 0)

            st.write(f"Total Gold Medals: {total_gold}")
            st.write(f"Total Silver Medals: {total_silver}")
            st.write(f"Total Bronze Medals: {total_bronze}")
            st.write(f"Total Medals: {total_gold + total_silver + total_bronze}")
        else:
            st.write("No medals data available for this country")
    else:
        st.write("No results data available")

def main():
    st.set_page_config(page_title="Olympic Data Analysis", layout="centered")
    st.title("Olympic Data Analysis")
    #st.markdown("<h1 style='text-align: center;'>Olympic Data Analysis</h1>", unsafe_allow_html=True)

    bios, results, nocs, country_dict, countries = load_data()
    country, include_winter, only_medalists = create_sidebar(countries)

    if country in country_dict:
        filtered_bios = filter_bios(bios, country, country_dict)
        filtered_results = filter_results(results, country, country_dict, include_winter, only_medalists)
        medals_data = get_medals(filtered_results, country, country_dict)
    else:
        st.error(f"No data available for {country}")
        filtered_bios = pd.DataFrame(columns=bios.columns)
        filtered_results = pd.DataFrame(columns=results.columns)
        medals_data = pd.DataFrame(columns=['year', 'medal'])

    
    st.header("Medals")
    plot_medals(medals_data)

    st.header("Birthplaces of the athletes")
    create_heatmap(filtered_bios)

    st.header("Results Table")
    display_results(filtered_results)

    st.header("Medal Summary")
    calculate_medals(filtered_results, country, country_dict)

if __name__ == "__main__":
    main()