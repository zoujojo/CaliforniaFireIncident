"""
Name: Yun Zou
CS602: Section 02
Data: California Fire Incidents, 2013 to 2019
URL:
Description:

This program creates a Streamlit app to show the data analysis
of California fire incidents during 2013 to 2019 about:
1.	what locations in California are under fire threat in a map, and
2.	how devastating they are.
"""

import numpy as np
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
plt.style.use('seaborn')

@st.cache

# A scatter plot to explore lat/lon data, not shown in streamlit app
def scatterData(data):
    plt.scatter(data.Longitude, data.Latitude)
    plt.grid()
    plt.xlabel("Latitude")
    plt.ylabel("Longitude")
    plt.title("California Fire Incidents for Year 2013 to 2019")
    plt.show()

# function to clean data for California map
def processMapData(data):
    # California Longitude: 114° 8' W to 124° 24' W Latitude: 32° 30' N to 42° N
    # Filter the unrealistic lon/lat data
    df_map = data[(data.Longitude < -114) & (data.Latitude > 30) & (data.Latitude < 44)]
    return df_map

# create a map by year
def mapByYear(data, year=2019):
    ZOOM_FACTOR = 5
    RADIUS_SCALE = 50

    df_map = processMapData(data)
    df = df_map[df_map.ArchiveYear == year]

    fire_map = folium.Map(location=[36, -120], zoom_start=ZOOM_FACTOR)

    for i in range(0, df.shape[0]):
        folium.Circle(radius=np.sqrt(df.iloc[i]['AcresBurned']) * RADIUS_SCALE,
                      location=[df.iloc[i]['Latitude'], df.iloc[i]['Longitude']],
                      popup="County: " + df.iloc[i]['Counties'] +
                            "\nAcresBurned: " + str(df.iloc[i]['AcresBurned']) +
                            "\nName: " + df.iloc[i]['Name'],
                      color='red', fill=True, fill_color='red').add_to(fire_map)
    return fire_map

# Bar charts to show top 10 acres burned counties for each year
def topAcresBurnedCounties(data, year, color='tab:blue'):
    df = data[data.ArchiveYear == year]
    df_counties = df.groupby(by='Counties')['AcresBurned'].sum()
    #print(df_counties)
    df_top10 = df_counties.sort_values(ascending=False)[:10]
    #print(df_top10)
    x = []
    y = []
    for i in range(len(df_top10)):
        x.append(df_top10.index[i])
        y.append(df_top10[i])
    plt.bar(x, y, color=color)
    plt.xlabel('County')
    plt.ylabel('Acres Burned')
    plt.xticks(x, rotation=45, ha='right')

    return plt


# bar chart to show yearly acres burned
def totalAcresBurnedByYear(data):
    table1 = pd.pivot_table(data, index=['ArchiveYear'], values=['AcresBurned'], aggfunc=np.sum)
    return table1

# line chart to show yearly major incidents count
def yearlyMajorIncidents(data):
    table2 = pd.pivot_table(data, index=['ArchiveYear'], values=['MajorIncident'], aggfunc=np.sum)
    return table2

# bar chart to show yearly average injuries for major incidents
def yearlyAverageInjuries(data):
    df = data[data.MajorIncident==True]
    table3 = pd.pivot_table(df, index=['ArchiveYear'], values=['Injuries'], aggfunc=np.mean)
    return table3

# bar charts to show yearly total structures damaged
def yearlyStructureDamagedMedian(data):
    df = data[data.MajorIncident==True]
    table4 = pd.pivot_table(df, index=['ArchiveYear'], values=['StructuresDamaged'], aggfunc=np.median)
    return table4


def main():
    df = pd.read_csv("California_Fire_Incidents.csv")
    print(df.info)
    print(df.columns)
    print(df.dtypes)


    # scatter plot lat/lon data for all years
    scatterData(df)

    # show map by year in Streamlit app
    st.title('California Fire Incidents\nYear 2013 to 2019')

    st.sidebar.header('Show Fire Maps and Top 10 Acres Burned Counties By Year')
    year = st.sidebar.slider("Select Year: ", min_value=2013, max_value=2019, step=1)

    st.header(f'Fire Map for Year {year}')
    st.write(f'The area of the red circle shows the acres burned in Year {year}.')
    df_map = processMapData(df)

    df1 = df_map[df_map.ArchiveYear == year]
    folium_static(mapByYear(df1, year))

    # charts show top 10 acres burned counties for each year with color radio button
    colors = {"tab:red":"r","tab:green":"g","tab:orange":"o","tab:blue":"b","tab:cyan":"c"}
    color_names = list(colors.keys())
    color = st.sidebar.radio('Select a color:', color_names)

    st.header(f'Top 10 Counties in Year {year}')
    st.write(f'Below is a bar plot of top 10 counties with most yearly total acres burned in {year}')
    st.pyplot(topAcresBurnedCounties(df, year, color))


    st.sidebar.header('Display Yearly Statistical Data Analysis Chart')
    type_names = ["Total Acres Burned", "Number of Major Incident", "Average Injuries of Major Incidents",
                  "Median Number of Structure Damaged of Major Incidents"]
    type = st.sidebar.radio("Select Analysis Type: ", type_names)

    st.header(f'Data Analysis: \n{type}')
    if type == type_names[0]:
        st.bar_chart(totalAcresBurnedByYear(df))
    elif type == type_names[1]:
        st.line_chart(yearlyMajorIncidents(df))
    elif type == type_names[2]:
        st.bar_chart(yearlyAverageInjuries(df))
    elif type == type_names[3]:
        st.bar_chart(yearlyStructureDamagedMedian(df))

main()


