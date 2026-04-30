import pickle
import streamlit as st
import requests
import os
# from .env import API_KEY
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    
    try:
        response = requests.get(url, timeout=10)  
        
        if response.status_code != 200:
            return "https://via.placeholder.com/500x750?text=No+Image"
        
        data = response.json()
        poster_path = data.get('poster_path')
        
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750?text=Error"

from concurrent.futures import ThreadPoolExecutor

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    movie_ids = [movies.iloc[i[0]].movie_id for i in distances[1:6]]
    
    with ThreadPoolExecutor() as executor:
        posters = list(executor.map(fetch_poster, movie_ids))
    
    names = [movies.iloc[i[0]].title for i in distances[1:6]]
    
    return names, posters


st.header('Movie Recommender System')
movies = pickle.load(open('movie_list.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Recommend'):
    recommended_movie_names,recommended_movie_posters = recommend(selected_movie)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(recommended_movie_names[0])
        st.image(recommended_movie_posters[0])
    with col2:
        st.text(recommended_movie_names[1])
        st.image(recommended_movie_posters[1])

    with col3:
        st.text(recommended_movie_names[2])
        st.image(recommended_movie_posters[2])
    with col4:
        st.text(recommended_movie_names[3])
        st.image(recommended_movie_posters[3])
    with col5:
        st.text(recommended_movie_names[4])
        st.image(recommended_movie_posters[4])





