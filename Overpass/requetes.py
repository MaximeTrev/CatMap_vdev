import overpy, time
from extractionDonnees import loadDatas
import pandas as pd

def get_overpass_data(company_name):
    """
    Interroge l'API Overpass avec overpy pour récupérer les données OSM d'une entreprise.
    """
    api = overpy.Overpass()
    query = f"""[out:json][timeout:180];(node["name"="{company_name}"];way["name"="{company_name}"];relation["name"="{company_name}"];);out center;"""
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
    - Le centre des ways et relations
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

    #Probleme ici car les relations ont parfois pas de coord directement. Possibilité :
    #Si la relation contient des nœuds ou d'autres objets associés ayant des coordonnées, il te faut parcourir ces membres et extraire les coordonnées.
    #Récupérer les coordonnées des nœuds : En supposant que chaque membre de la relation soit un nœud, tu peux récupérer les coordonnées de ce nœud.
    #--> on risque cependant d'avoir les coord de chaque noeuds de la relation, entrainant de nombreux "duplicatats"
    """
    # Traitement des relations (utilisation du "center" si dispo)
    for relation in result.relations:
        print(relation.tags)
        if hasattr(relation, "center_lat") and hasattr(relation, "center_lon"):
            # Vérifier si les valeurs des attributs ne sont pas None
            if relation.center_lat is not None and relation.center_lon is not None:
                results.append({
                    "name": relation.tags.get("name", "Unknown"),
                    "type": "relation",
                    "lat": float(relation.center_lat),
                    "long": float(relation.center_lon),
                    **extract_tags(relation)  # Ajout des tags
                })
            else:
                # Si les coordonnées sont None, récupérer les coordonnées d'un nœud
                node = relation.members[0]  # Supposons que le premier membre est un nœud
                lat = node.lat
                lon = node.lon
                results.append({
                    "name": relation.tags.get("name", "Unknown"),
                    "type": "relation",
                    "lat": float(lat),
                    "long": float(lon),
                    **extract_tags(relation)  # Ajout des tags
                })"""

    return pd.DataFrame(results)

def extract_tags(element):
    """ Récupère les tags spécifiques d'un élément OSM """
    tags_list = ["source", "amenity", "place", "shop", "power", "highway"]
    return {tag: element.tags.get(tag, "N/A") for tag in tags_list}


