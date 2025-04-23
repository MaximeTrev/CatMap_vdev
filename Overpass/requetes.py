import overpy, time
from extractionDonnees import loadDatas
import pandas as pd
import streamlit as st


def get_overpass_data(company_name):
    """
    - Interroge l'API Overpass avec overpy pour récupérer les données OSM d'une entreprise.
    - Considère uniquement les nodes et les ways actuellement. 
    - Les relations ne sont pas prises en charges au regard du bruits qu'elles induisent
    
    """
    api = overpy.Overpass()
    query = f"""[out:json][timeout:180];(node["name"="{company_name}"];way["name"="{company_name}"];);out center;"""
    # Ajout de "out center;" pour forcer le centre des ways et relations
    try:
        result = api.query(query)
        return result
    except Exception as e:
        print(f"Erreur lors de la requête Overpass : {e}")
        return None

def process_osm_data(result):
    """
    Traite les données OSM pour extraire :
    - Les nodes avec leurs coordonnées
    - Le centre des ways
    - Si volonté d'extraire les relations --> pas de centre / coordonnées directement, il faut parcouris les membres la composant, donc: 
        - soit extraire ses noeuds et en faire la moyenne arithmétique,
        - soit extraire ses ways et extraire son centre
    --> il faut également adapter la query
    /!\ Relations ajoute un bruitage similaire à son gain de volumétrie sur nos exemples (ajout d'arrêt de bus...)
    """
    results = []

    # Traitement des nœuds
    for node in result.nodes:
        results.append({
            "name": node.tags.get("name", "Unknown"),
            "type": "node",
            "lat": float(node.lat),
            "long": float(node.lon),
            **extract_tags(node)  # Ajout des tags
        })

    # Traitement des ways (utilisation du "center" directement)
    for way in result.ways:
        if hasattr(way, "center_lat") and hasattr(way, "center_lon"):
            results.append({
                "name": way.tags.get("name", "Unknown"),
                "type": "way",
                "lat": float(way.center_lat),
                "long": float(way.center_lon),
                **extract_tags(way)  # Ajout des tags
                #**extract_tags(node)  # Ajout des tags
            })
    return pd.DataFrame(results)

def extract_tags(element):
    """ Récupère les tags spécifiques d'un élément OSM """
    tags_list = ["source", "amenity", "place", "shop", "power", "highway"]
    return {tag: element.tags.get(tag, "N/A") for tag in tags_list}


