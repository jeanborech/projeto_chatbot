import requests
import streamlit as st

class APIService:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get(self, endpoint):
        try:
            r = requests.get(f"{self.base_url}/{endpoint}")
            r.raise_for_status()
            return r.json()
        except Exception as e:
            st.error(f"Erro ao buscar dados de {endpoint}: {e}")
            return []