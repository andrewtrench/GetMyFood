import streamlit as st
import openai
import requests
import urllib.parse
from streamlit_embedcode import github_gist
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import os

os.environ['OPENAI_API_KEY'] = st.secret['OPENAI_API_KEY']
os.environ['SPOTIFY_CLIENT_ID'] = st.secret['SPOTIFY_CLIENT_ID']
os.environ['SPOTIFY_CLIENT_SECRET'] = st.secret['SPOTIFY_CLIENT_SECRET']

client_credentials_manager = SpotifyClientCredentials(client_id=os.environ['SPOTIFY_CLIENT_ID'], client_secret=os.environ['SPOTIFY_CLIENT_SECRET'])

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)



def get_recipe_and_wine(ingredients, dietary_requirement, cuisine):
    prompt = f"Create a {cuisine} recipe that includes {', '.join(ingredients)} and follows the {dietary_requirement} dietary " \
             f"requirement. Also, suggest a wine pairing and suggest a South African wine by brand specifically if " \
             f"possible, " \
             f"and complimentary spices and herbs. Show the estimated calories per portion. Also recommend a " \
             f"song to listen to while cooking this recipe. Use these subheadings it " \
             f"the results: 'Ingredients:', 'Instructions:', 'Wine pairing:','South African wine recommendation:', " \
             f"'Complimentary spices and herbs:', 'Estimated calories per portion:','Song recommendation:'. Give the " \
             f"recipe a name and use it as a title indicated by 'Title:'.Use centigrade for temperature and grams for weight. "

    recipe_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful chef and gourmand"},
                  {"role": "user", "content": f"{prompt}"}],
        temperature=0.2,
        max_tokens=500,
    )
    results = recipe_completion['choices'][0]['message']['content']
    print (results)
    return results

def search_spotify(song):
    results = sp.search(q=song, limit=1)
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


st.set_page_config(page_title="VineDine: Savor the Flavor", layout="wide")

# Include Bootstrap CDN
st.markdown("""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
""", unsafe_allow_html=True)

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Custom CSS
custom_css = """
<style>
    stMarkdownContainer[data-testid="stMarkdownContainer"] {
    background-color: #F0F0F0;
    color: #000;
    border: 2px solid #C0C0C0;
    border-radius: 5px;
    padding: 8px;
    font-size: 16px;
}
    
    h1 {
        font-family: 'Roboto', sans-serif;
        color: #25D366;
    }

    div[data-testid="stText"] input {
        font-family: 'Roboto', sans-serif;
    }

    div[data-testid="stSelectbox"] select {
        font-family: 'Roboto', sans-serif;
    }

    button {
        font-family: 'Roboto', sans-serif;
    }

    .btn {
        background-color: #25D366;
        color: white;
        font-family: 'Roboto', sans-serif;
        border: none;
        padding: 10px 20px;
        text-decoration: none;
        display: inline-block;
        cursor: pointer;
        border-radius: 25px
    }
</style>"""

st.markdown(custom_css, unsafe_allow_html=True)

# Create columns for layout
left_column, center_column, right_column = st.columns([1, 3, 1])

with center_column:
    st.title("VineDine: Savour the Flavour")
    ingredients = st.text_input("Enter ingredients (comma-separated):")
    cuisines = [
        'Italian', 'Chinese', 'Indian', 'Mexican', 'Japanese', 'Mediterranean',
        'Middle Eastern', 'Thai', 'American', 'Greek', 'French', 'Spanish'
    ]
    cuisine = st.selectbox("Select a cuisine:", cuisines)
    options = ['Vegetarian', 'Vegan', 'Anything goes', 'Low fat', 'Under 300 calories']
    dietary_requirement = st.selectbox("Select a dietary requirement:", options)

    if st.button("Find Recipe and Wine Pairing"):
        ingredients_list = [ingredient.strip() for ingredient in ingredients.split(',')]
        result = get_recipe_and_wine(ingredients_list, dietary_requirement, cuisine)
        formatted_result = format_subheadings(result)
        song,artist = extract_song_from_results(result)
        song_url = search_spotify(song)

        st.markdown(formatted_result, unsafe_allow_html=True)
        whatsapp_url = generate_whatsapp_url(result)
        st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="btn">Share by WhatsApp</a>',
                    unsafe_allow_html=True)
        st.markdown(f'<a href="{song_url}" target="_blank" class="btn">Listen to Song</a>',
                    unsafe_allow_html=True)
