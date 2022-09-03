import streamlit as st  # type: ignore
import pandas as pd
import numpy as np
import pydeck as pdk # type: ignore
import plotly.express as px # type: ignore
data_url = "data.csv"

st.title("Motor Vehicle Collisions in NYC")
st.markdown("This a streamlit dashboard")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(data_url, nrows=nrows, parse_dates=[['CRASH DATE', 'CRASH TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x : str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'number of persons injured':'injured_persons'}, inplace=True)
    data.rename(columns={'crash date_crash time':'date/time'}, inplace=True)
    data.rename(columns={'number of pedestrians injured':'number_of_pedestrians_injured'}, inplace=True)
    data.rename(columns={'number of cyclist injured':'number_of_cyclist_injured'}, inplace=True)
    data.rename(columns={'number of motorist injured':'number_of_motorist_injured'}, inplace=True)
    data.rename(columns={'on street name':'on_street_name'}, inplace=True)
    return data

data = load_data(10**5)

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("No of persons injured in vehicle collisions", 0, 19)
if injured_people is None:
    injured_people = 0
st.map(data.query("injured_persons >= @injured_people")[['latitude', 'longitude']].dropna(how='any'))

st.header("How many collisions occur during a given time of day ?")
hour = st.slider("Hour to look at", 0, 23)
original_data = data
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour+1)%24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude" : midpoint[0],
        "longitude" : midpoint[1],
        "zoom" : 11,
        "pitch" : 50
    },
    layers = [
        pdk.Layer(
            "HexagonLayer",
            data = data[['date/time', 'latitude', 'longitude']],
            get_position = ['longitude', 'latitude'],
            radius = 100,
            extruded = True,
            pickable = True,
            elevation_scale = 4,
            elevation_range = [0,1000]
        )
    ]
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour+1)%24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))
]
hist = np.histogram(filtered['date/time'].dt.minute, range=(0, 60), bins=60)[0]
chart_data = pd.DataFrame({
    'minute': range(0, 60),
    'crashes' : hist
})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected types")
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query('number_of_pedestrians_injured >= 1')[['on_street_name', 'number_of_pedestrians_injured']].sort_values(by=['number_of_pedestrians_injured'], ascending=False).dropna(how='any')[:5])
elif select == 'Cyclists':
    st.write(original_data.query('number_of_cyclist_injured >= 1')[['on_street_name', 'number_of_cyclist_injured']].sort_values(by=['number_of_cyclist_injured'], ascending=False).dropna(how='any')[:5])
elif select == 'Motorists':
    st.write(original_data.query('number_of_motorist_injured >= 1')[['on_street_name', 'number_of_motorist_injured']].sort_values(by=['number_of_motorist_injured'], ascending=False).dropna(how='any')[:5])


if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)