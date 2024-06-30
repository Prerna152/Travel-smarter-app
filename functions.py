import requests
import json
import pandas as pd
import os
import deepl
import datetime
import dotenv
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv
load_dotenv()
import time
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
import pathlib
from os.path import join
import warnings
warnings.filterwarnings('ignore')
from write_read_data_to_file import *




##Function for forecast API:
def get_weather_forecast(arrival_city_name):
    url = "https://api.weatherbit.io/v2.0/forecast/daily"
    params = {
        'city': arrival_city_name,
        'key': os.getenv('weather_bit')  
    }

    weather = requests.get(url, params=params)
    weather = weather.json()['data']

    forecasts_data = []

    for forecast in weather:
        try:
            date = forecast['datetime']
        except KeyError:
            date = ''
        try:
            max_temp = forecast['max_temp']
        except KeyError:
            max_temp = ''
        try:
            min_temp = forecast['min_temp']
        except KeyError:
            min_temp = ''
        try:
            description = forecast['weather']['description']
        except KeyError:
            description = ''

        forecast_data = {
            'Date': date,
            'Max Temp': max_temp,
            'Min Temp': min_temp,
            'Weather': description,
        }

    # Append the dictionary to the list
        forecasts_data.append(forecast_data)

    return forecasts_data

#weather_forecast = get_weather_forecast(arrival_city_name)


##Function build weather graph:
def get_weather_plot(data):
    #print(weather_df)
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])

    # Set the aesthetic style of the plots
    sns.set(style="white")

    # Create a figure and a set of subplots
    fig, ax1 = plt.subplots(figsize=(17, 7))
    ax1.grid(False)

    # Plot MaxTemp and MinTemp
    sns.lineplot(x='Date', y='Max Temp', data=df, marker='o', ax=ax1, label='Max Temperature', color='r')
    sns.lineplot(x='Date', y='Min Temp', data=df, marker='o', ax=ax1, label='Min Temperature', color='b')

    # Rotate date labels for better readability
    plt.xticks(rotation=45)

    # Set the labels and title
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Temperature (°C)')
    ax1.set_title('Temperature and Weather Conditions Over Time' )

    # Rotate date labels for better readability and show all dates
    ax1.set_xticks(df['Date'])
    ax1.set_xticklabels(df['Date'].dt.strftime('%Y-%m-%d'), rotation=45, ha='right')

    # Create a secondary y-axis to plot weather conditions
    ax2 = ax1.twinx()

    # Define color palette for weather conditions
    weather_colors={
    'Few clouds': 'gray',
    'Clear Sky': 'blue',
    'Scattered clouds': 'green',
    'Moderate rain': 'yellow',
    'Broken clouds': 'orange',
    'Heavy rain': 'red',
    'Overcast clouds': 'darkgray'
}

    # Plot Weather as scatter plot
    sns.scatterplot(x='Date', y='Max Temp', data=df, hue='Weather', palette=weather_colors, s=100, ax=ax2, legend=True, zorder=5)

    # Set y-axis label for weather conditions
    ax2.set_ylabel('Weather Conditions')

    # Move the legend outside the plot
    #handles, labels = ax1.get_legend_handles_labels()
    #ax1.legend(handles=handles[1:], labels=labels[1:], loc='right', bbox_to_anchor=(1.05, 0.5), title='Weather')

    # Show the plot
    #plt.savefig("temperature_weather_plot.png", bbox_inches='tight')
    
    return plt.show()

#plot = get_weather_plot(weather_forecast)



##Function get tocken for API:

def get_tocken():
    # API_key = os.getenv("Amadeus_key")
    # API_seccret_key = os.getenv("Amadeus_secret_key")

    headers = { 'Content-Type' : 'application/x-www-form-urlencoded' }
    data = { 'grant_type' : 'client_credentials', 'client_id' : os.getenv("Amadeus_key"), 'client_secret' : os.getenv("Amadeus_secret_key") }
    response = requests.post("https://test.api.amadeus.com/v1/security/oauth2/token", headers=headers, data=data)

    response = response.json()
    
    return response['access_token']



##Function for getting all city names and codes:
def get_city_iata(city):
    cities_iata = read_data_from_file('cities_iata.json')
    city_code_iata = cities_iata.get(city)

    if not city_code_iata:

        headers = {
                'accept': 'application/vnd.amadeus+json',
                'Authorization': 'Bearer ' + get_tocken(),
            }
        
        params = {
            'keyword': city,
            'max': '1',
        }
        response = requests.get('https://test.api.amadeus.com/v1/reference-data/locations/cities', params=params, headers=headers)

        data = response.json()
        city_code = data['data'][0]

        city_code_iata = {
            city : { 'iata' : city_code['iataCode'],
                     'countryCode' : city_code['address']['countryCode']
                    }
                                }
    
        write_data_to_file('cities_iata.json', city_code_iata)
    
    # print(city_code_iata)
    return(city_code_iata)


## Function Flight Offers Search:
def get_flights_offers(iata_code_dep,iata_code_arrival,departure_date,return_date, adults): 

    headers = {
        'accept': 'application/vnd.amadeus+json',
        'Authorization': 'Bearer ' + get_tocken(),
    }

    params = {
        'originLocationCode': iata_code_dep ,
        'destinationLocationCode': iata_code_arrival,
        'departureDate': departure_date,
        'returnDate': return_date,
        'adults': adults,
        'nonStop': 'true',
        'max': '250',
    }

    flight_offers = requests.get('https://test.api.amadeus.com/v2/shopping/flight-offers', params=params, headers=headers)

    flights = flight_offers.json()

    flights_list = []

    if not flights.get('data'):
         flights_list = {}
         return flights_list
    
       
    for flight in flights['data']:
        
            from_code = flight['itineraries'][0]['segments'][0]['departure']['iataCode']
            to_code = flight['itineraries'][0]['segments'][0]['arrival']['iataCode']
            price = flight['price']['total']
            departure_datetime = flight['itineraries'][0]['segments'][0]['departure']['at']
            arrival_datetime = flight['itineraries'][0]['segments'][0]['arrival']['at']

            back_from_code = flight['itineraries'][1]['segments'][0]['departure']['iataCode']
            back_to_code = flight['itineraries'][1]['segments'][0]['arrival']['iataCode']
            back_departure_datetime = flight['itineraries'][1]['segments'][0]['departure']['at']
            back_arrival_datetime = flight['itineraries'][1]['segments'][0]['arrival']['at']


            # Convert datetime strings to date strings
            departure_date = datetime.datetime.fromisoformat(departure_datetime).date().isoformat()
            departure_time = datetime.datetime.fromisoformat(departure_datetime).time().isoformat()
            arrival_date = datetime.datetime.fromisoformat(arrival_datetime).date().isoformat()
            arrival_time = datetime.datetime.fromisoformat(arrival_datetime).time().isoformat()
            back_departure_date = datetime.datetime.fromisoformat(back_departure_datetime).date().isoformat()
            back_departure_time = datetime.datetime.fromisoformat(back_departure_datetime).time().isoformat()
            back_arrival_date = datetime.datetime.fromisoformat(back_arrival_datetime).date().isoformat()
            back_arrival_time = datetime.datetime.fromisoformat(back_arrival_datetime).time().isoformat()


            # Create a dictionary for the flight data
            flight_data = { 
                'To':{
                    'From': from_code,
                    'To': to_code,
                    'Departure date': departure_date,
                    'Departure time': departure_time,
                    'Arrival date': arrival_date,
                    'Arrival time': arrival_time
                             },

                'From' :{
                    'From': back_from_code,
                    'To': back_to_code,
                    'Departure date': back_departure_date,
                    'Departure time': back_departure_time,
                    'Arrival date': back_arrival_date,
                    'Arrival time': back_arrival_time   
                            },
                'price': price,
            }


            flights_list.append(flight_data)
    return flights_list

#flights_data = get_flights_offers(iata_code_dep,iata_code_arrival,"2024-06-14","2024-06-16", adults)



## Function Hotel list:
def get_hotels_catalog(iata_code):
    no_data = False
    
    with open('hotels_catalog.json', 'r') as openfile: 
            hotel_catalog = json.load(openfile)

    if hotel_catalog:
        try:
                hotel_catalog[iata_code]
        except KeyError:
                no_data = True

    if not hotel_catalog or no_data == True:                
        headers = {
            'accept': 'application/vnd.amadeus+json',
            'Authorization': 'Bearer ' + get_tocken(),
                    }

        params = {
            'cityCode': iata_code,
            'radius': '5',
            'radiusUnit': 'KM',
            'hotelSource': 'ALL',
            'ratings': '4',
                    }
        hotel_list= requests.get("https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city",params =params,  headers = headers)

        # hotel_catalog[iata_code] = hotel_list.json().get('data')[0:100]
        hotel_catalog[iata_code] = hotel_list.json().get('data')[0:20]

        with open("hotels_catalog.json", "w") as outfile:
                json.dump(hotel_catalog, outfile)

      
    hotel_catalog_list = []
   
    for hotel in hotel_catalog[iata_code]:
        iata_code = hotel.get('iataCode')
        hotel_id = hotel.get('hotelId')
        name = hotel.get('name')
        country = hotel.get('address',{}).get('countryCode')
        lon = hotel.get('geoCode',{}).get('longitude')
        lat = hotel.get('geoCode',{}).get('latitude')
        distance = hotel.get('distance',{}).get('value')
        unit = hotel.get('distance',{}).get('unit')
        
   
        hotel_catalog_data = {
                    'City iata code': iata_code,
                    'Hotel Id': hotel_id,
                    'Hotel': name,
                    'Country code': country,
                    'Longitude': lon,
                    'latitude': lat,
                    'Distance': distance,
                    'Unit': unit,
                    'Price': hotel.get('price', 0),
                    'Currency': '',
                    'Language': '',
                                }

        hotel_catalog_list.append(hotel_catalog_data)
            
    return hotel_catalog_list
    
# hotel_catalog_list = get_hotels_catalog('PAR')


##Hotel price:
def get_hotel_prices(hotel_catalog_list, adults, checkInDate):
    hotel_ids = []

    for hotel in hotel_catalog_list:
        hotel_ids.append(hotel['Hotel Id'])

    headers = {
        'accept': 'application/vnd.amadeus+json',
        'Authorization': 'Bearer ' + get_tocken(),
    }
    params = {
        'hotelIds': hotel_ids,               
        'adults':adults,
        'checkInDate': checkInDate,
        'includeClosed' : 'true',
        'bestRateOnly' : 'true',
        'paymentPolicy': 'NONE',
        'roomQuantity': '1',
    }
    hotels_prices= requests.get("https://test.api.amadeus.com/v3/shopping/hotel-offers",params = params, headers = headers)
    hotels_prices_json = hotels_prices.json().get('data',[])
    
    hotels_prices_lists = []
   
    for hotel in hotels_prices_json:
            
        city_code = hotel['hotel'].get('cityCode')
        hotel_id = hotel['hotel'].get('hotelId')
        hotel_name = hotel['hotel'].get('name')
        type = hotel['hotel'].get('type')
        check_in_date = hotel['offers'][0].get('checkInDate')
        room_category= hotel['offers'][0]['room']['typeEstimated'].get('category')
        bed_type = hotel['offers'][0]['room']['typeEstimated'].get('bedType')
        price = hotel['offers'][0]['price'].get('total')
        price_currency = hotel['offers'][0]['price'].get('currency')
        language = hotel['offers'][0]['room']['description'].get('lang')
        # Create a dictionary for the hotel data
        hotel_prices_data = {
            'City': city_code,
            'Hotel id': hotel_id,
            'Hotel': hotel_name,
            'Type': type,
            'Check In':  check_in_date,
            'room_category': room_category,
            'Bed type': bed_type,
            'Price': price,
            'Currency': price_currency,
            'Language' : language,
            }
        # Append the hotel data to the list
        hotels_prices_lists.append(hotel_prices_data)

    return  hotels_prices_lists

# hotel_prices_lists = get_hotel_prices(hotel_catalog_list, '1', '2025-02-22')


#Function for phrase-book:
def get_phrase_book(language_code):
    eng_phrases = ['Hello!','My name is...','Please','Thank you','Yes','No','Help me please','Do you speak English?', 'How much does it cost?', 'Where is...?','Good Bye!']
    translations = []
    
    # Translate each English phrase to the target language
    for word in eng_phrases:
        auth_key = os.getenv("Deepl_key")  # Assuming you have your Deepl API key stored in an environment variable
        translator = deepl.Translator(auth_key)
        result = translator.translate_text(word, target_lang=language_code)
        translations.append({'Phrase': word, 'Translation': result.text})
        
    return translations
#translations = get_phrase_book('DE')



##Function for web_csrapping. We used Selenium just for study case, in other case  it will be better and fast to use Wikipedia API :
def get_info_wiki(city):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
    chrome_options.add_argument('--no-sandbox')  # Required for running as root user
    chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems


    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Navigate to Wikipedia homepage
        driver.get("https://www.wikipedia.org/")

        # Find the search input element
        search_input = driver.find_element(By.ID, "searchInput")

        # Enter "Berlin" into the search input
        search_input.send_keys(city)

        # Submit the search form
        search_input.send_keys(Keys.RETURN)

        # Wait for the results to load (you may need to adjust the sleep time)
        time.sleep(2)

            # Locate the infobox element using XPath
        infobox_element = driver.find_element(By.CLASS_NAME, 'infobox')

        # Find all label and data elements within the infobox
        labels = infobox_element.find_elements(By.CLASS_NAME, 'infobox-label')
        data_elements = infobox_element.find_elements(By.CLASS_NAME, 'infobox-data')

        # Initialize lists to store label and data values
        labels_list = [label.text.replace('•', '').strip() for label in labels]
        data_list = [data.text for data in data_elements]

        # Ensure the lengths are equal
        if len(labels_list) != len(data_list):
            print("Error: Lengths of labels and data do not match.")
            driver.quit()
            exit()

        # Create a DataFrame
        df = pd.DataFrame({'Info:': labels_list, 'Result:': data_list})

    finally:
        # Close the WebDriver
        driver.quit()

    return df
#get_info_wiki('Berlin')


#Function get_name country:

def get_country_name_from_df(city):
    cities_info = read_data_from_file('cities_iata.json')
    city_info = cities_info.get(city)
    country_name = city_info.get('country')

    if not country_name:
        df = get_info_wiki(city)
        country_name = df['Result:'].iloc[0]
        city_info['country'] = country_name
        cities_info[city].update(city_info)
        write_data_to_file('cities_iata.json', cities_info)

    return country_name

#print(get_country_name_from_df('Berlin'))

#Function to offer local cuisine:

def get_local_cuisine_country(country):
    dishes_info = read_data_from_file('country-by-national-dish.json')
    for dish_info in dishes_info:
        dishes_country = dish_info.get('country')
        if dishes_country == country:
            return dish_info.get("dish")
        
# print(get_local_cuisine_country("France"))



##Function converter currency:
def get_currency_rate(cur_country):

    url = "https://currency-conversion-and-exchange-rates.p.rapidapi.com/latest"

    querystring = {"from":"EUR","to":cur_country, "amount":"1"}

    headers = {
        "x-rapidapi-key": os.getenv("Currency_key"),
        "x-rapidapi-host": "currency-conversion-and-exchange-rates.p.rapidapi.com",
    }

    currency_rate = requests.get(url, headers=headers, params=querystring)
  
    currency_result = currency_rate.json()

    currency_catalog_data = {
            'Date': currency_result['date'],
            'Base Currency rate': "1",
            'Base Currency': currency_result['base'],
            'Local Currency rate': currency_result['rates'][cur_country],
            'Local Currency': cur_country
            }
    
    return currency_catalog_data

#print(get_currency_rate("USD"))



