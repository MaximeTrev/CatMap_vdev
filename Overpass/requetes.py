import overpy, time, unicodedata
from extractionDonnees import loadDatas
import pandas as pd
import streamlit as st

def normalize_char_variants(char):
    """Retourne une classe regex regroupant le caractère et ses variantes accentuées."""
    variants = {char.lower(), char.upper()}
    for form in ['NFD', 'NFKD']:
        decomposed = unicodedata.normalize(form, char)
        base = decomposed[0]
        if base.isalpha():
            variants.add(base.lower())
            variants.add(base.upper())
    accent_map = {
        'a': 'aàáâäãåā',
        'e': 'eèéêëēėę',
        'i': 'iìíîïīį',
        'o': 'oòóôõöøō',
        'u': 'uùúûüū',
        'c': 'cçćč',
        'n': 'nñń',
        'y': 'yÿý',}
    char_lc = char.lower()
    if char_lc in accent_map:
        for c in accent_map[char_lc]:
            variants.add(c)
            variants.add(c.upper())
    return '[' + ''.join(sorted(variants)) + ']'

def build_company_name_regex(company_name: str) -> str:
    """Construit une regex robuste pour rechercher le nom dans Overpass."""
    regex_parts = []
    for char in company_name:
        if char.isalpha():
            regex_parts.append(normalize_char_variants(char))
        elif char.isspace():
            regex_parts.append('[\\s\\-_]+')
        else:
            regex_parts.append(re.escape(char))
    core = ''.join(regex_parts)
    return f"(^|[\\s\\-_]){core}" # (^|[\\s\\-_]) permet de s'assurer que le mot est en 1ère position ou précédé d'un séparateur (espace, tiret..)

def get_overpass_data(company_name):
    """
    - Interroge l'API Overpass avec overpy à partir d'une requête REGEX pour récupérer les données OSM d'une entreprise.
    - Considère uniquement les nodes et les ways actuellement. 
    - Les relations ne sont pas prises en charges au regard du bruits qu'elles induisent
    
    """
    api = overpy.Overpass()
    regex = build_company_name_regex(company_name)
    # [!"XX"] sert a exclure les résultats avec le tag renseigné, \\b indique que le mot se termine ici
    regex_operator = '~' 
    query = f"""
    [out:json][timeout:180];
    (
      node["name"{regex_operator}"{regex}\\b",i][!"highway"][!"place"][!"junction"];
      way["name"{regex_operator}"{regex}\\b",i][!"highway"][!"place"][!"junction"];
    );
    out center;
    """ 
    # Ajout de "out center;" pour forcer le centre des ways et relations


    query = """
    [out:json][timeout:180];
    (
      node["name"~"Celio\\b",i][!"highway"][!"place"][!"junction"];
      way["name"~"Celio\\b",i][!"highway"][!"place"][!"junction"];
    );
    out center;"""
    

    print(query)
    st.code(query)
    try:
        result = api.query(query)
        st.write(result.nodes)
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
    !  Relations ajoute un bruitage similaire à son gain de volumétrie sur nos exemples (ajout d'arrêt de bus...)
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


