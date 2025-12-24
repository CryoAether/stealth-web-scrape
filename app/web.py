from flask import Flask, render_template, request
import pandas as pd
import re
import geonamescache

app = Flask(__name__)

gc = geonamescache.GeonamesCache()
cities = gc.get_cities()
us_states = gc.get_us_states() # Maps 'CA' -> 'California'

city_to_state = {}

for city_id, data in cities.items():
    if data['countrycode'] == 'US':
        city_name = data['name'].lower()
        state_code = data['admin1code'] # e.g., 'NC' or 'CA'
        
        if state_code in us_states:
            full_state_name = us_states[state_code]['name']
            city_to_state[city_name] = full_state_name


def detect_state(location_text):
    if not isinstance(location_text, str):
        return "Other"
        
    text = location_text.lower()

    for word in text.replace(',', '').split():
        if word in city_to_state:
            return city_to_state[word]
            

    for state_name in set(city_to_state.values()):
        if state_name.lower() in text:
            return state_name
            
    return "Other"

def extract_year(title):
    title = str(title).lower()
    four_digit = re.search(r'\b(19|20)\d{2}\b', title)
    if four_digit:
        return int(four_digit.group(0))
    two_digit = re.search(r"\b'?(\d{2})\b", title)
    if two_digit:
        val = int(two_digit.group(1))
        return 2000 + val if val <= 26 else 1900 + val
    return 0 

def detect_brand(title):
    title = str(title).lower()
    brands = {
        'harley': 'Harley Davidson', 'davidson': 'Harley Davidson',
        'kawasaki': 'Kawasaki', 'honda': 'Honda',
        'bmw': 'BMW', 'triumph': 'Triumph'
    }
    for key, clean_name in brands.items():
        if key in title:
            return clean_name
    return "Other"

def clean_price(price_str):
    try:
        return float(re.sub(r'[^\d.]', '', str(price_str)))
    except:
        return 0.0

@app.route('/')
def home():
    try:
        df = pd.read_csv("listings.csv")
    except FileNotFoundError:
        return "listings.csv not found. Please run the scraper first."

    df['CleanYear'] = df['Listing'].apply(extract_year)
    df['DetectedBrand'] = df['Listing'].apply(detect_brand)
    df['CleanPrice'] = df['Price'].apply(clean_price)

    #detect state
    df['DetectedState'] = df['Location'].apply(detect_state)
    available_states = sorted(df['DetectedState'].unique())

    search_query = request.args.get('search', '').lower()
    brand_filter = request.args.get('brand', '')
    location_filter = request.args.get('location', '')
    sort_option = request.args.get('sort', '')

    if search_query:
        df = df[df['Listing'].str.lower().str.contains(search_query, na=False)]
    if brand_filter:
        df = df[df['DetectedBrand'] == brand_filter]

    if location_filter:
        df = df[df['DetectedState'] == location_filter]

    if sort_option == 'price_low':
        df = df.sort_values(by='CleanPrice', ascending=True)
    elif sort_option == 'price_high':
        df = df.sort_values(by='CleanPrice', ascending=False)
    elif sort_option == 'year_new':
        df = df.sort_values(by='CleanYear', ascending=False)
    elif sort_option == 'year_old':
        df = df.sort_values(by='CleanYear', ascending=True)

    if "Other" in available_states: 
        available_states.remove("Other") 
    items = df.to_dict(orient='records')
    
    return render_template('base.html', items=items, 
                           current_search=request.args.get('search', ''),
                           current_brand=request.args.get('brand', ''),
                           current_location=request.args.get('location', ''),
                           current_sort=request.args.get('sort', ''),
                           available_states=available_states,
                           )

if __name__ == '__main__':
    app.run(debug=True)