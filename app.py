from functions import *
from Packing_List_Generator import *
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    flights = []
    hotels = []
    min_flight_price = max_flight_price = None
    min_hotel_price = max_hotel_price = None
    weather_forecast = []
    common_facts = None
    phrase_book = None
    currency_conversion = None
    local_cuisine = None
    pack_adviser = None
    
    if request.method == 'POST':
        departure_city = request.form.get('departure-city')
        destination_city = request.form.get('destination-city')
        departure_date = request.form.get('departure-date')
        return_date = request.form.get('return-date')
        number_of_people = request.form.get('number-of-people')
        aim_for_visit = request.form.get('aim-for-visit')

        departure_city_iata = get_city_iata(departure_city).get('iata')
        destination_city_iata = get_city_iata(destination_city).get('iata')

        # Get flight offers
        flights = get_flights_offers(departure_city_iata, destination_city_iata, departure_date, return_date, number_of_people)
        if flights:
            flight_prices = [flight['price'] for flight in flights]
            min_flight_price = min(flight_prices)
            max_flight_price = max(flight_prices)

        # Get hotels catalog
        hotels_catalog = get_hotels_catalog(destination_city_iata)
        hotels = hotels_catalog  
        
        # Calculate min and max hotel prices
        if hotels:
            hotel_prices = [hotel.get('Price', 0) for hotel in hotels]
            if hotel_prices:
                min_hotel_price = min(hotel_prices)
                max_hotel_price = max(hotel_prices)

        # weather_forecast = get_weather_forecast(destination_city)
        weather_forecast = [{}]

        #Get common facts about the destination
        common_facts_df = get_info_wiki(destination_city)
        common_facts = common_facts_df.to_dict(orient='records')

        # Get phrase book for the destination language
        city_data = get_city_iata(destination_city)
        destination_language_code = city_data.get('countryCode')
        phrase_book = get_phrase_book(destination_language_code)

       # Get currency rate
        currency_conversion = get_currency_rate('EUR')

        # Get local cuisine
        country = get_country_name_from_df(destination_city)
        local_cuisine = get_local_cuisine_country(country)
    
        # Generate packing list
        if aim_for_visit:
            duration = (datetime.strptime(return_date, '%Y-%m-%d') - datetime.strptime(departure_date, '%Y-%m-%d')).days
            pack_adviser = generate_packing_list(destination_city, duration, aim_for_visit)
 
    return render_template('index.html', flights=flights, hotels=hotels, weather_forecast=weather_forecast,
                           min_flight_price=min_flight_price, max_flight_price=max_flight_price,
                           min_hotel_price=min_hotel_price, max_hotel_price=max_hotel_price,
                           common_facts=common_facts, phrase_book=phrase_book, currency_conversion=currency_conversion,
                           local_cuisine=local_cuisine, pack_adviser=pack_adviser)

    
if __name__ == '__main__':
    app.run(debug=True)
