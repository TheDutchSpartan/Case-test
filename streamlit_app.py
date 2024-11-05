import time
start_time = time.perf_counter()
import folium
import json
from folium.plugins import MarkerCluster
import streamlit as st 
import requests 
import pandas as pd 
import matplotlib 
import matplotlib.pyplot as plt 
import plotly 
import plotly.graph_objects as go 
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# ======================================================================================================================================== #
# Title and introduction sectie voor de Streamlit app
st.title("""*COVID-19 Data* van 08 en 09 Maart 2023 voor EU-Landen""")

st.write("""Tijdens de pandemie is het bijhouden van data cruciaal geweest om inzicht te krijgen in de verspreiding en impact van COVID-19 in verschillende regio’s. In dit project hebben we een interactieve data-visualisatie ontwikkeld met behulp van Python en de Streamlit-bibliotheek. Ons doel was om gebruikers de mogelijkheid te geven om de COVID-19-gevallen en sterfgevallen in verschillende Europese landen en hun provincies te verkennen.""")
st.write("""Hiervoor hebben we als eerst een grafiek gecreëerd die het aantal gediagnosticeerde gevallen en sterfgevallen per land en provincie toont. Gebruikers kunnen zelf kiezen welke data ze willen bekijken, zowel de gediagnosticeerde gevallen als de sterfgevallen, of slechts één van beide datasets. Op deze manier kunnen gebruikers eenvoudig de verspreiding van COVID-19 binnen specifieke regio's analyseren.""")

st.title('Interactief COVID-19 Dashboard voor EU-landen')

st.subheader('Introductie')

st.write("""
Dit dashboard biedt een overzicht van de verspreiding van COVID-19 in verschillende Europese landen en hun provincies. Het doel van dit dashboard is om gebruikers te voorzien van actuele inzichten over het aantal bevestigde gevallen, sterfgevallen en de procentuele toename van COVID-19 in verschillende regio's.

### Functies van het dashboard:
1. **COVID-19 Gevallen en Sterfgevallen per Provincie**: Visualiseer het aantal bevestigde gevallen en sterfgevallen voor elke provincie in geselecteerde Europese landen. U kunt eenvoudig wisselen tussen landen om de data voor specifieke regio's te bekijken.
2. **Procentuele Toename per Dag**: Analyseer de procentuele toename van bevestigde gevallen, actieve gevallen en sterfgevallen tussen twee datums. Dit biedt inzicht in de snelheid waarmee het virus zich verspreidt in verschillende provincies.
3. **Gediagnosticeerde Gevallen vs. Sterfgevallen**: Vergelijk het aantal bevestigde gevallen met sterfgevallen in elke provincie. Deze visualisatie maakt het mogelijk om te zien welke regio’s harder zijn getroffen door de pandemie.
   
### Hoe het dashboard te gebruiken:
- Selecteer een **land** en **provincie** in de dropdown-menu’s om de data voor een specifieke regio te bekijken.
- Gebruik de **slider** om data voor verschillende datums te vergelijken.
- Vink opties aan of uit met de **checkboxes** om specifieke datapunten te tonen of te verbergen.

Het dashboard is ontworpen om overheden, gezondheidsautoriteiten en burgers te helpen bij het beter begrijpen van de impact van COVID-19 in Europa. Door data te visualiseren, kunnen trends gemakkelijker worden geïdentificeerd, wat leidt tot beter geïnformeerde beslissingen.
""")

# ======================================================================================================================================== #
# Load the CSV file
covid_df_EU = pd.read_csv("Case2vb_preprocessed.csv")
df = covid_df_EU.copy() 
# Check if `region` column needs parsing
def parse_region(region_str):
    try:
        # Convert JSON string to dictionary if needed
        if isinstance(region_str, str):
            return json.loads(region_str.replace("'", "\""))  # Handle single quotes if present
        return region_str  # If already a dictionary, return as is
    except json.JSONDecodeError:
        return {}  # Return an empty dictionary if parsing fails

# # Apply parsing to the `region` column
# covid_df_EU['region'] = covid_df_EU['region'].apply(parse_region)

# # Extract `province` from the parsed `region` dictionaries
# covid_df_EU['province'] = covid_df_EU['region'].apply(lambda x: x.get('province', 'Unknown'))

# # Filter out rows where province is 'Unknown'
# covid_df_EU = covid_df_EU[covid_df_EU['province'] != 'Unknown']

# Zoekt naar missende data
missing_data = covid_df_EU.isnull().sum()
missing_data_count = missing_data.sum()

# Toont missende data
st.subheader('Missende Data Overzicht')
#Boolean statement voor weergave betreft missende waardes
if missing_data_count == 0:
    st.write('Geen missende data gevonden. Alle onderdelen zijn compleet.')
else:
    st.write(' een overzicht van de missende data in de dataset:')
    st.dataframe(missing_data)
# # Extract province data en haalt de entries weg waar province is 'Unknown'
# covid_df_EU['province'] = covid_df_EU['region'].apply(lambda x: x.get('province'))
# covid_df_EU = covid_df_EU[covid_df_EU['province'] != 'Unknown']
# # Groepeer de data bij province en calculate de som van confirmed cases en deaths
# province_data_EU = covid_df_EU.groupby(['province', 'country_name']).agg({'confirmed': 'sum', 'deaths': 'sum', 'fatality_rate': 'mean'}).reset_index()
# province_data_EU = province_data_EU.reindex(columns=['country_name', 'province', 'confirmed', 'deaths', 'fatality_rate'])
# province_data_EU = province_data_EU.sort_values(by='country_name', ascending=True)
# #Plotly figure
# fig = go.Figure()
# Toevoegen van Bar traces voor de comfirmed cases en deaths for elke land
for country in covid_df_EU['country_name'].unique():
    fig.add_trace(go.Bar(x=covid_df_EU['province'],
                        y=covid_df_EU['confirmed'],
                        name=f'{country} gediagnosticeerde',
                        visible=False,
                        marker_color='blue'))
    fig.add_trace(go.Bar(x=covid_df_EU['province'],
                        y=covid_df_EU['deaths'],
                        name=f'{country} sterfgevallen',
                        visible=False,
                        marker_color='red'))
#Dit maakt het eerste land zijn data visible by defeault
fig.data[0].visible=True
fig.data[1].visible=True
# Dropdown menu voor kiezen van verschillende landen
dropdown_buttons = []

for country in covid_df_EU['country_name'].unique():
    dropdown_buttons.append({
        'label':country,
        'method':'update',
        'args':[{'visible': [name.startswith(country) for name in [trace.name for trace in fig.data]]},
        {'title':f'COVID-19 Gegevens voor {country}'}]
    })
# Update layout voor het plotly figuur, met een dropdown en titles
fig.update_layout(
    title = 'COVID-19 Gediagnosticeerde en Sterfgevallen per Provincie',
    xaxis_title = 'Provincie',
    yaxis_title = 'Aantal',
    barmode = 'group',
    updatemenus = [{'buttons':dropdown_buttons,
                    'showactive':True,
                    'direction':'down'}]
)
#weergeven van plot in streamlit
st.plotly_chart(fig)

# =================================================================================================================================== #
#Doormiddel van streamlit schrijven we headers en een stuk tekst
st.header("""Procentuele Toename van COVID-19 Gevallen en Sterfgevallen in de EU""")
st.write("""De verspreiding van COVID-19 blijft een belangrijke zorg in Europa, waarbij overheden en gezondheidsautoriteiten nauwlettend de dagelijkse stijgingen in besmettingen en sterfgevallen volgen. De onderstaande grafiek biedt een inzichtelijke vergelijking van de procentuele toename van actieve COVID-19-gevallen, bevestigde besmettingen, en sterfgevallen per provincie, tussen 8 en 9 maart 2023.""")
st.write("""Door deze gegevens te analyseren, krijgen we een duidelijker beeld van welke provincies in verschillende landen het hardst worden getroffen door de pandemie. Dit kan beleidsmakers helpen om beter geïnformeerde beslissingen te nemen over interventies en middelen.""")
st.write("""Kies hieronder een land en een provincie om de specifieke stijgingspercentages te bekijken. De kleuren in de grafiek geven de stijgingen weer: blauw voor actieve gevallen, oranje voor bevestigde besmettingen, en rood voor sterfgevallen.""")

# =================================================================================================================================== #
# # Berekend verhoogde percentage voor confirmed cases, deaths, en active cases
# covid_df_EU_con_diff = covid_df_EU[['province', 'country_name', 'confirmed', 'confirmed_diff']].copy()
# covid_df_EU_con_diff['2023-03-08'] = covid_df_EU_con_diff['confirmed'] - covid_df_EU_con_diff['confirmed_diff']
# covid_df_EU_con_diff['confirmed_increase_%'] = (((covid_df_EU_con_diff['confirmed'] - covid_df_EU_con_diff['2023-03-08']) / covid_df_EU_con_diff['2023-03-08']) * 100)
# covid_df_EU_con_diff.rename(columns={'confirmed':'2023-03-09'}, inplace=True)
# covid_df_EU_con_diff = covid_df_EU_con_diff.reindex(columns=['country_name', 'province', 'confirmed_diff','confirmed_increase_%', '2023-03-08', '2023-03-09',])
# #herhalen van soortgelijke berekeningen voor de deaths en active cases
# covid_df_EU_dea_diff = covid_df_EU[['province', 'country_name', 'deaths', 'deaths_diff']].copy()
# covid_df_EU_dea_diff['2023-03-08'] = covid_df_EU_dea_diff['deaths'] - covid_df_EU_dea_diff['deaths_diff']
# covid_df_EU_dea_diff['deaths_increase_%'] = (((covid_df_EU_dea_diff['deaths'] - covid_df_EU_dea_diff['2023-03-08']) / covid_df_EU_dea_diff['2023-03-08']) * 100)
# covid_df_EU_dea_diff.rename(columns={'deaths':'2023-03-09'}, inplace=True)
# covid_df_EU_dea_diff = covid_df_EU_dea_diff.reindex(columns=['country_name', 'province', 'deaths_diff', 'deaths_increase_%', '2023-03-08', '2023-03-09'])
# covid_df_EU_dea_diff['deaths_increase_%'] = covid_df_EU_dea_diff['deaths_increase_%'].fillna(0)

# covid_df_EU_act_diff = covid_df_EU[['province', 'country_name', 'active', 'active_diff']].copy()
# covid_df_EU_act_diff['2023-03-08'] = covid_df_EU_act_diff['active'] - covid_df_EU_act_diff['active_diff']
# covid_df_EU_act_diff['active_increase_%'] = (((covid_df_EU_act_diff['active'] - covid_df_EU_act_diff['2023-03-08']) / covid_df_EU_act_diff['2023-03-08']) * 100)
# covid_df_EU_act_diff.rename(columns={'active':'2023-03-09'}, inplace=True)
# covid_df_EU_act_diff = covid_df_EU_act_diff.reindex(columns=['country_name', 'province', 'active_diff', 'active_increase_%', '2023-03-08', '2023-03-09'])
# covid_df_EU_act_diff['active_increase_%'] = covid_df_EU_act_diff['active_increase_%'].fillna(0)
#Samenvoegen van de data in een dataframe voor toename percentage
# covid_df_EU_increase_pct = covid_df_EU_act_diff[['province', 'country_name', 'active_increase_%']].merge(
#     covid_df_EU_con_diff[['province', 'country_name', 'confirmed_increase_%']],
#     on=['province', 'country_name'],
#     how='inner').merge(
#         covid_df_EU_dea_diff[['province', 'country_name', 'deaths_increase_%']],
#         on=['province', 'country_name'],
#         how='inner'
#     )
# # Herschikken van de kolommen in de dataset
# covid_df_EU_increase_pct = covid_df_EU_increase_pct.reindex(
#     columns=['country_name', 'province', 'active_increase_%', 'confirmed_increase_%', 'deaths_increase_%'])
# Titel voor het dashboard
st.header('COVID-19 Toename Percentage Dashboard')
# Dropdown voor het selecteren van een land

# Aanmaken van een staafdiagram met plotly
selected_countries = st.multiselect('Selecteer landen om te vergelijken', covid_df_EU_increase_pct['country_name'].unique())
fig = go.Figure()

for country in selected_countries:
    country_data = covid_df_EU_increase_pct[covid_df_EU_increase_pct['country_name'] == country]
    values = country_data[['active_increase_%', 'confirmed_increase_%', 'deaths_increase_%']].mean()
    labels = ['Actieve Toename (%)', 'Gediagnosticeerde Toename (%)', 'Sterfgevallen Toename (%)']

    fig.add_trace(go.Bar(
        x=labels,
        y=values,
        name=country,
    ))

# Layout and styling of the plot
fig.update_layout(
    title="Vergelijking van Toename in Percentage voor Geselecteerde Landen",
    xaxis_title="Meting",
    yaxis_title="Percentage",
    barmode='group'
)

# Display the plot in Streamlit
if selected_countries:
    st.plotly_chart(fig)
else:
    st.write("Selecteer ten minste één land om een vergelijking te maken.")


# =================================================================================================================================== #
# Titel en text voor de tweede sectie van de analyse doormiddel van streamlit
st.header("""Analyse van COVID-19: Gediagnosticeerde Gevallen versus Sterfgevallen""")
st.write("""Het verloop van de COVID-19-pandemie verschilt aanzienlijk per regio en wordt beïnvloed door factoren zoals bevolkingsdichtheid, zorgcapaciteit en genomen overheidsmaatregelen. Voor beleidsmakers en gezondheidsautoriteiten is het cruciaal om inzicht te krijgen in deze regionale variaties.""")
st.write("""De onderstaande grafiek toont het aantal gediagnosticeerde gevallen in verhouding tot het aantal sterfgevallen in verschillende Europese provincies, gebaseerd op data van 8 maart 2023. Met behulp van de slider kunt u het bereik van het aantal besmettingen instellen om specifieke clusters te bekijken. Elke marker vertegenwoordigt een provincie en toont bij hover zowel het land als de provincie. Dit geeft een direct inzicht in hoe provincies zich tot elkaar verhouden.""")
st.write("""Door deze visualisatie worden trends duidelijk zichtbaar, zoals provincies met relatief hogere sterfgevallen in verhouding tot het aantal gediagnosticeerde gevallen. Ook wordt het mogelijk om patronen te identificeren die wijzen op provincies waar het aantal sterfgevallen relatief hoger ligt ten opzichte van besmettingen. Dit type analyse kan beleidsmakers helpen bij het ontwikkelen van gerichte interventies en het toewijzen van middelen om de impact van COVID-19 te beperken.""")

# Dataset voor scatter plot per datum
covid_df_EU['confirmed_08'] = covid_df_EU['confirmed'] - covid_df_EU['confirmed_diff']
covid_df_EU['deaths_08'] = covid_df_EU['deaths'] - covid_df_EU['deaths_diff']

# Data voor 8 maart 2023 gebruiken voor scatter en regressie
scatter_data = covid_df_EU[['country_name', 'province', 'confirmed_08', 'deaths_08']].dropna()

# Slider toevoegen voor het filteren op aantal besmettingen, met bereik van 0 tot 9M
confirmed_range = st.slider("Selecteer bereik voor aantal gediagnosticeerde gevallen", 
                            0, 9000000, (0, 9000000))

# Filter de data op basis van het geselecteerde bereik van aantal besmettingen
filtered_data = scatter_data[(scatter_data['confirmed_08'] >= confirmed_range[0]) & 
                             (scatter_data['confirmed_08'] <= confirmed_range[1])]

# Bereken dynamisch de maximale waarde voor de y-as op basis van gefilterde data
max_y_value = filtered_data['deaths_08'].max() if not filtered_data.empty else 80000  # Standaardwaarde als de data leeg is

# Regressie berekenen op de volledige dataset (niet gefilterd)
x_full = scatter_data['confirmed_08'].values.reshape(-1, 1)
y_full = scatter_data['deaths_08'].values
model = LinearRegression()
model.fit(x_full, y_full)
y_pred_full = model.predict(x_full)
r2_full = r2_score(y_full, y_pred_full)

# Scatter plot maken met volledige regressielijn en gefilterde gegevens
fig_scat = go.Figure()

# Hover-informatie uitbreiden met zowel land als provincie
hover_text = filtered_data.apply(lambda row: f"{row['country_name']}, {row['']}", axis=1)

# Originele data punten binnen het bereik, met kleuren per land en hover-informatie
fig_scat.add_trace(go.Scatter(
    x=filtered_data['confirmed_08'],
    y=filtered_data['deaths_08'],
    mode='markers',
    marker=dict(
        color=filtered_data['country_name'].astype('category').cat.codes, 
        colorscale='Turbo',  # Alternatieve kleuren
        size=8,  # Iets grotere markers
        opacity=0.8  # Minder transparant
    ),
    text=hover_text,  # Land en provincie in de hover-informatie
    name='Gediagnosticeerde vs Sterfgevallen'
))

# Regressielijn toevoegen op basis van volledige dataset (blijf altijd zichtbaar)
fig_scat.add_trace(go.Scatter(
    x=scatter_data['confirmed_08'],
    y=y_pred_full,
    mode='lines',
    name='Regressielijn (volledig)',
    line=dict(color='red', dash='dash', width=3)  # Dikkere lijn
))

# Layout en stijl van de plot met dynamische x-as afhankelijk van slider en maximale limiet van 9M
fig_scat.update_layout(
    title='Aantal gediagnosticeerde uitgezet tegen het aantal sterfgevallen (met regressie)',
    xaxis=dict(
        title='Aantal gediagnosticeerde',
        tickvals=[0, 1e6, 2e6, 3e6, 4e6, 5e6, 6e6, 7e6, 8e6, 9e6],  # Stappen tot 9M
        range=[confirmed_range[0], confirmed_range[1]]
    ),
    yaxis=dict(
        title='Aantal sterfgevallen',
        range=[0, max_y_value]  # Dynamisch bereik van de y-as
    ),
    template='plotly_dark'
)

# Weergeven van de scatter plot en R² waarde
st.plotly_chart(fig_scat)
st.write(f"R²-waarde voor de volledige regressie: {r2_full:.4f}")


# Tekst omtrent data kwaliteit
st.subheader('Discussie over Data Kwaliteit')
st.write("""
De dataset die in deze analyse is gebruikt, bevat geen ontbrekende waarden, wat betekent dat alle statistieken volledig zijn vertegenwoordigd. Dit vormt een solide basis voor een nauwkeurige analyse van COVID-19 gevallen en sterfgevallen.

Daarnaast zijn mogelijke uitschieters gemarkeerd tijdens de verkenning, wat kan duiden op provincies met ongewoon hoge of lage aantallen gevallen. Deze uitschieters zijn opgenomen in de analyse, maar worden gemarkeerd voor verdere beoordeling.

Door de volledigheid en betrouwbaarheid van de data te waarborgen, zullen de inzichten die uit dit dashboard worden getrokken waarschijnlijk de ware COVID-19 trends in de Europese regio’s weerspiegelen.
""")
#Disclaimer

st.subheader('Disclaimer')
st.write("""Ook al bevat de dataset geen ontbrekenden waarden, zijn de provincies niet altijd accuraat. Zo zijn er EU-landen die wel provincies/regio's bevatten, maar dat niet is aangegeven in de dataset. Zo lijkt het dus alsof sommige landen geen provincies hebben terwijl dit wel het geval is.""")

# ======================================================================================================================================== #
# Function to parse the 'region' column
def parse_region(region_str):
    try:
        if isinstance(region_str, str):
            return json.loads(region_str.replace("'", "\""))  # Handle single quotes if present
        return region_str  # If already a dictionary, return as is
    except json.JSONDecodeError:
        return {}  # Return an empty dictionary if parsing fails

# # Apply parsing to the 'region' column
# df['region'] = df['region'].apply(parse_region)

# # Extract 'lat' and 'long' from the parsed 'region' dictionaries
# df['Lat'] = df['region'].apply(lambda x: x.get('lat'))
# df['Lon'] = df['region'].apply(lambda x: x.get('long'))
# df['province'] = df['region'].apply(lambda x: x.get('province'))
# df['name'] = df['region'].apply(lambda x: x.get('name'))

# # Convert 'Lat' and 'Lon' to numeric, coercing errors to NaN
# df['Lat'] = pd.to_numeric(df['Lat'], errors='coerce')
# df['Lon'] = pd.to_numeric(df['Lon'], errors='coerce')

# # Filter data to avoid clutter (e.g., show only locations with confirmed cases > 0)
# df_filtered = df[df['confirmed'] > 0]

# Create a Folium map
m = folium.Map(location=[35, 0], tiles="OpenStreetMap", zoom_start=4)

# Add a legend with colored boxes
legend_html = '''
<div style="position: fixed; 
         top: 10px; right: 10px; width: 200px; height: auto; 
         z-index:9999; font-size:14px; 
         background-color: white; opacity: .8;
         padding: 10px;">
&emsp;<b>Legend</b><br>
&emsp;<i style="background: green; width: 20px; height: 20px; display: inline-block;"></i>&emsp;0-100 Cases<br>
&emsp;<i style="background: yellow; width: 20px; height: 20px; display: inline-block;"></i>&emsp;101-1000 Cases<br>
&emsp;<i style="background: orange; width: 20px; height: 20px; display: inline-block;"></i>&emsp;1001-5000 Cases<br>
&emsp;<i style="background: crimson; width: 20px; height: 20px; display: inline-block;"></i>&emsp;5001+ Cases<br>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Create a marker cluster for better performance
marker_cluster = MarkerCluster().add_to(m)

# Define a function to get color based on the number of confirmed cases
def get_color(cases):
    if cases <= 100:
        return 'green'
    elif cases <= 1000:
        return 'yellow'
    elif cases <= 5000:
        return 'orange'
    else:
        return 'crimson'

# Iterate over the filtered DataFrame to add markers to the map
for city in df_filtered.itertuples():
    if pd.notna(city.Lat) and pd.notna(city.Lon):  # Ensure coordinates are valid
        folium.CircleMarker(
            location=[city.Lat, city.Lon],
            popup=(f'Country name: {city.name}<br>'
                   f'Country ABV: {city.country}<br>'
                   f'Province: {city.province}<br>'
                   f'Confirmed: {city.confirmed}<br>'
                   f'Deaths: {city.deaths}'),
            radius=float(city.confirmed) * 0.00001,  # Adjust the size based on confirmed cases
            color=get_color(city.confirmed),
            fill=True,
            fill_color=get_color(city.confirmed),
            fill_opacity=0.6
        ).add_to(marker_cluster)

# Render the map as HTML
map_html = m._repr_html_()

# Streamlit Application Layout
st.title("COVID-19 Cases Map")
st.write("Deze kaart visualiseert bevestigde COVID-19-gevallen per regio. Gebruik de legenda om de kleuren te interpreteren en details te bekijken door op de markeringen te klikken")

# Embed the map HTML in Streamlit
st.components.v1.html(map_html, width=800, height=600)

end_time = time.perf_counter()
st.write(f"Total execution time: {end_time - start_time} seconds")
