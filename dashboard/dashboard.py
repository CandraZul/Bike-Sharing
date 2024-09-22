import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


sns.set(style='dark')


st.header('Bike Sharing Dashboard :bike:')


def create_daily_rentals_df(df):
    daily_rentals_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum"
    })
    daily_rentals_df = daily_rentals_df.reset_index()
    daily_rentals_df.rename(columns={
        "cnt": "rentals_count"
    }, inplace=True)
    return daily_rentals_df

def create_sum_season_df(df):
    sum_season_df = df.groupby("season").agg({"cnt": "sum"}).reset_index()
    sum_season_df.rename(columns={"cnt": "rentals_count"}, inplace=True)

    sum_season_df = sum_season_df.sort_values(by="rentals_count", ascending=False).reset_index(drop=True)

    sum_season_df['season'] = sum_season_df['season'].replace({
        1:'springer', 
        2:'summer', 
        3:'fall', 
        4:'winter'
    })
    return sum_season_df

def create_weathersit_df(df):
    weathersit_df = df.groupby("weathersit").agg({'cnt':'sum'}).reset_index()

    weathersit_df['weathersit'] = weathersit_df['weathersit'].replace({
        1: 'Clear',
        2: 'Misty',
        3: 'Light Precipitation',
        4: 'Heavy Precipitation',
    })
    return weathersit_df

def create_weather_factors_df(df):
    weather_factors_df = df[['dteday', 'temp', 'hum', 'windspeed']]
    weather_factors_df['temp'] = weather_factors_df['temp'] * 41
    weather_factors_df['hum'] = weather_factors_df['hum'] * 100
    weather_factors_df['windspeed'] = weather_factors_df['windspeed'] * 67
    return weather_factors_df

def create_user_df(df):
    user_df = pd.DataFrame()
    user_df['user_type'] = ['casual', 'registered']
    user_df['rentals_count'] = [df['casual'].sum(), df['registered'].sum()]
    user_df = user_df.sort_values(by="rentals_count", ascending=False)
    return user_df

bike_df = pd.read_csv("./dashboard/bike_data.csv")

datetime_columns = ["dteday"]
bike_df.sort_values(by="dteday", inplace=True)
bike_df.reset_index(inplace=True)
 

for column in datetime_columns:
    bike_df[column] = pd.to_datetime(bike_df[column])

min_date = bike_df["dteday"].min()

max_date = bike_df["dteday"].max()
 

with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>Bike Sharing</h2>", unsafe_allow_html=True)
    st.image("bike-logo.png")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = bike_df[(bike_df["dteday"] >= str(start_date)) & 

                (bike_df["dteday"] <= str(end_date))]

daily_rentals_df = create_daily_rentals_df(main_df)
sum_season_df = create_sum_season_df(main_df)
weathersit_df = create_weathersit_df(main_df)
weather_factors_df = create_weather_factors_df(main_df)
user_df = create_user_df(main_df)

# subheader rental
st.subheader('Daily Rentals')
total_rentals = daily_rentals_df.rentals_count.sum()
st.metric("Total rentals", value=total_rentals)

# rental graph
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_rentals_df["dteday"],
    daily_rentals_df["rentals_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.set_ylabel("Rentals Count", fontsize=20)
ax.set_xlabel("Date", fontsize=20)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

# season
st.subheader("Seasonal Bike Rental Performance")

fig, ax = plt.subplots(figsize=(10, 5))  
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    y="rentals_count", 
    x="season",
    data=sum_season_df,
    palette=colors,
    order=sum_season_df['season']
)
ax.set_title("Number of Rentals by Season", loc="center", fontsize=15)
ax.set_ylabel("Rentals Count")
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

# weathersit
st.subheader("Impact of Weather on Bike Rental Performance")

fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    y="cnt", 
    x="weathersit",
    data=weathersit_df,
    palette=colors,
    order = weathersit_df['weathersit']
)
ax.set_title("Number of Rentals by Weathersit", loc="center", fontsize=15)
ax.set_ylabel("Rentals Count")
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

# Weather Factors vs Rentals
with st.expander("Weather Factors and Rentals"):
    # temp
    fig, ax1 = plt.subplots(figsize=(16, 8))
    ax1.plot(
        daily_rentals_df["dteday"],
        daily_rentals_df["rentals_count"],
        marker='o', 
        linewidth=2,
        color="#90CAF9",
        label="Rentals Count"
    )
    ax1.set_ylabel("Rentals Count", fontsize=15, color="#90CAF9")
    ax1.tick_params(axis='y', labelsize=12, colors="#90CAF9")
    ax1.set_xlabel("Date", fontsize=15)

    # Creating second y-axis for temperature
    ax2 = ax1.twinx()
    ax2.plot(
        weather_factors_df["dteday"],
        weather_factors_df["temp"],  # Mengembalikan ke nilai asli
        marker='o', 
        linewidth=2,
        color="#FF5733",
        label="Temperature (°C)"
    )
    ax2.set_ylabel("Temperature (°C)", fontsize=15, color="#FF5733")
    ax2.tick_params(axis='y', labelsize=12, colors="#FF5733")

    plt.title("Temperature and Rentals", fontsize=20)
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    st.pyplot(fig)


    # humidity
    fig, ax1 = plt.subplots(figsize=(16, 8))
    ax1.plot(
        daily_rentals_df["dteday"],
        daily_rentals_df["rentals_count"],
        marker='o', 
        linewidth=2,
        color="#90CAF9",
        label="Rentals Count"
    )
    ax1.set_ylabel("Rentals Count", fontsize=15, color="#90CAF9")
    ax1.tick_params(axis='y', labelsize=12, colors="#90CAF9")
    ax1.set_xlabel("Date", fontsize=15)

    ax2 = ax1.twinx()
    ax2.plot(
        weather_factors_df["dteday"],
        weather_factors_df["hum"],  # Mengembalikan ke nilai asli
        marker='o', 
        linewidth=2,
        color="#FF5733",
        label="Humidity (%)"
    )
    ax2.set_ylabel("Humidity (%)", fontsize=15, color="#FF5733")
    ax2.tick_params(axis='y', labelsize=12, colors="#FF5733")

    plt.title("Humidity and Rentals", fontsize=20)
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    st.pyplot(fig)

    # Windspeed
    fig, ax1 = plt.subplots(figsize=(16, 8))
    ax1.plot(
        daily_rentals_df["dteday"],
        daily_rentals_df["rentals_count"],
        marker='o', 
        linewidth=2,
        color="#90CAF9",
        label="Rentals Count"
    )
    ax1.set_ylabel("Rentals Count", fontsize=15, color="#90CAF9")
    ax1.tick_params(axis='y', labelsize=12, colors="#90CAF9")
    ax1.set_xlabel("Date", fontsize=15)

    ax2 = ax1.twinx()
    ax2.plot(
        weather_factors_df["dteday"],
        weather_factors_df["windspeed"],  # Mengembalikan ke nilai asli
        marker='o', 
        linewidth=2,
        color="#FF5733",
        label="Windspeed (km/h)"
    )
    ax2.set_ylabel("Windspeed (km/h)", fontsize=15, color="#FF5733")
    ax2.tick_params(axis='y', labelsize=12, colors="#FF5733")

    plt.title("Windspeed and Rentals", fontsize=20)
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    st.pyplot(fig)

# Casual User vs Registered User
st.subheader("Casual vs Registered Users")
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(y=user_df["rentals_count"], x=user_df["user_type"], palette="Blues")
ax.set_ylabel("Rentals Count")
ax.set_xlabel("User Type")
ax.set_title("Number of Rentals by User Type")
st.pyplot(fig)

