import os
import re
import urllib.parse
import openai
import spotipy
import streamlit as st
from spotipy.oauth2 import SpotifyClientCredentials
import base64
from PIL import Image
from io import BytesIO


os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
os.environ['SPOTIFY_CLIENT_ID'] = st.secrets['SPOTIFY_CLIENT_ID']
os.environ['SPOTIFY_CLIENT_SECRET'] = st.secrets['SPOTIFY_CLIENT_SECRET']

openai.api_key = os.environ['OPENAI_API_KEY']
client_credentials_manager = SpotifyClientCredentials(client_id=os.environ['SPOTIFY_CLIENT_ID'], client_secret=os.environ['SPOTIFY_CLIENT_SECRET'])

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)



def get_recipe_and_wine(ingredients, dietary_requirement, cuisine):
    prompt = f"Create a {cuisine} recipe that includes {', '.join(ingredients)} and follows the {dietary_requirement} dietary " \
             f"requirement. Also, suggest a wine pairing and suggest a South African wine by brand specifically if " \
             f"possible, " \
             f"and complimentary spices and herbs. Show the estimated calories per portion. Also recommend a " \
             f"song to listen to while cooking this recipe but select from a wide range of artists who match the " \
             f"culture of the cuisine. Use these subheadings it " \
             f"the results: 'Ingredients:', 'Instructions:', 'Wine pairing:','South African wine recommendation:', " \
             f"'Complimentary spices and herbs:', 'Estimated calories per portion:','Song recommendation:'. Give the " \
             f"recipe a name and use it as a title indicated by 'Title:'.Use centigrade for temperature and grams for weight. "

    recipe_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful chef and gourmand"},
                  {"role": "user", "content": f"{prompt}"}],
        temperature=0.5,
        max_tokens=500,
    )
    results = recipe_completion['choices'][0]['message']['content']
    print (results)
    return results

def search_spotify(artist_name, song_name):
    query = f'artist:{artist_name} track:{song_name}'
    results = sp.search(q=query, limit=1)
    song_url = results['tracks']['items'][0]['external_urls']['spotify']
    #print (song_url)
    return song_url


def generate_whatsapp_url(text):
    base_url = "https://wa.me/?text="
    encoded_text = urllib.parse.quote(text)
    return f"{base_url}{encoded_text}"


def extract_song_from_results(result_text):
    pattern = r'"(.+?)" by (.+?)[\s\.]'
    match = re.search(pattern, result_text)
    if match:
        song_name = match.group(1)
        artist_name = match.group(2)
        #print(f"Song: {song_name}\nArtist: {artist_name}")
        return song_name, artist_name
    else:
        print("No match found")

def format_subheadings(result_text):
    subheadings = [
        "Title:",
        "Ingredients:",
        "Instructions:",
        "Wine pairing:",
        "South African wine recommendation:",
        "Complimentary spices and herbs:",
        "Estimated calories per portion:",
        "Song recommendation:",
    ]

    lines = result_text.split("\n")
    for i, line in enumerate(lines):
        for subheading in subheadings:
            if subheading in line:
                if subheading == "Title:":
                    line = line.replace(subheading, "")
                    lines[i] = f"<h3>{line.strip()}</h3>"
                else:
                    lines[i] = line.replace(subheading, f"<b>{subheading}</b>")
                break

    return "\n".join(lines)

def image_to_base64(image_path):
    with Image.open(image_path) as img:
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/jpeg;base64,{img_base64}"

st.set_page_config(page_title="VineDine: Savor the Flavor", layout="wide")

# Include Bootstrap CDN
st.markdown("""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
""", unsafe_allow_html=True)

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

background_image = "veggies.jpg"
background_image_base64 = image_to_base64(background_image)

# Custom CSS
custom_css = f"""
<style>body {{
        background-image: url({background_image_base64});
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }}
    
    h1 {{
        font-family: 'Roboto', sans-serif;
        color: #25D366;
    }}

    button {{
        font-family: 'Roboto', sans-serif;
    }}

    .btn {{
        background-color: #25D366;
        color: white;
        font-family: 'Roboto', sans-serif;
        border: none;
        padding: 10px 20px;
        text-decoration: none;
        display: inline-block;
        cursor: pointer;
        border-radius: 25px
    }}
</style>"""

st.markdown(custom_css, unsafe_allow_html=True)

# Create columns for layout
left_column, center_column, right_column = st.columns([1, 3, 1])

with center_column:
    st.title("VineDine: Savour the Flavour")
    ingredients = st.text_input("Enter ingredients (comma-separated):")
    cuisines = [
        'Italian', 'Chinese', 'Indian', 'Mexican', 'Japanese', 'Mediterranean',
        'Middle Eastern', 'Thai', 'American', 'Greek', 'French', 'Spanish',"South African"
    ]
    cuisine = st.selectbox("Select a cuisine:", cuisines)
    options = ['Anything goes', 'Keto','Low fat', 'Under 300 calories','Vegetarian', 'Vegan', 'Gluten-free']
    dietary_requirement = st.selectbox("Select a dietary requirement:", options)

    if st.button("Find Recipe and Wine Pairing"):
        ingredients_list = [ingredient.strip() for ingredient in ingredients.split(',')]
        result = get_recipe_and_wine(ingredients_list, dietary_requirement, cuisine)
        formatted_result = format_subheadings(result)
        song,artist = extract_song_from_results(result)
        song_url = search_spotify(artist, song)

        st.markdown(formatted_result, unsafe_allow_html=True)
        whatsapp_url = generate_whatsapp_url(result)
        st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="btn">Share by WhatsApp</a>',
                    unsafe_allow_html=True)
        st.markdown(f'<a href="{song_url}" target="_blank" class="btn">Listen to Song</a>',
                    unsafe_allow_html=True)
