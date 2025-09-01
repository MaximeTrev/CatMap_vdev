import streamlit as st
import pandas as pd
import json
import time
import unidecode as u
import os
from requetes import *
import datetime

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        # Récupérer les valeurs de NomEntreprise et FichierCSV
        FichierCSV = kwargs.get('FichierCSV', None)
        NomEntreprise = kwargs.get('NomEntreprise', None)

        # Initialisation du chronomètre cumulé
        if "timing_total" not in st.session_state:
            st.session_state.timing_total = 0

        if FichierCSV:  # Mode FichierCSV (avec appels récursifs)
            if "timing_start" not in st.session_state:  
                # Premier appel en mode FichierCSV => On démarre le chronomètre
                st.session_state.timing_start = time.time()
                st.session_state.is_first_call = True  # Marquer comme premier appel
            
            result = func(*args, **kwargs)  # Exécution de la fonction
            
            if st.session_state.is_first_call:
                # Afficher le temps total une seule fois (quand le premier appel termine)
                elapsed_time = time.time() - st.session_state.timing_start
                st.session_state.timing_total += elapsed_time
                timing_total_datetime = str(datetime.timedelta(seconds=int(elapsed_time)))
                print(f"Computing time: {round(elapsed_time, 0)} s (Total: {timing_total_datetime})", flush = True)
                
                # Réinitialiser pour la prochaine exécution
                del st.session_state["timing_start"]
                del st.session_state["is_first_call"]

            return result

        elif NomEntreprise and FichierCSV is None:  # Mode NomEntreprise (et FichierCSV n'est PAS renseigné)
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            st.session_state.timing_total += elapsed_time
            timing_total_datetime = str(datetime.timedelta(seconds=int(elapsed_time)))
            print(f"Computing time: {round(elapsed_time, 0)} s (Total: {timing_total_datetime})", flush = True)
            return result

        else:
            return func(*args, **kwargs)  # Cas où ni NomEntreprise ni FichierCSV ne sont fournis

    return wrapper

def __suppr__(chain) : 
    """
    Haute sensibilité à la casse de la méthode : Total != TOTAL != total ...
    Fonction ayant pour objectif de supprimer les bruits potentiels au sein du/des nom(s) en input, commes les appelations juridiques (Fr)
    """
    #Liste des éléments à supprimer des noms
    ListeLabel = [" SE", " SARL", " EI", " EURL", " SASU", " SAS", " SA", " SNC", " SCS", " SCA"]
    
    ch = chain.upper()
    occ, i = ListeLabel[0], 1
    lengthListe = len(ListeLabel)
    while occ not in ch and i<lengthListe:
        occ = ListeLabel[i]
        i+=1
    if i==lengthListe :
        return chain
    ch = ch.replace(occ, "")
    #On retourne un nom normalisé
    return ch.capitalize()
    
@timing_decorator
def georef(option, progress_container, NomEntreprise=None, FichierCSV=None, i=1, max_length = None, j = 0) :
    """
    Fonction pour convertir un fichier CSV en JSON en générant des variations de noms d'entreprises
    et en récupérant des données via Overpass Turbo.
    Récursivité si FichierCSV: on boucle sur le mode NomEntreprise sur chaque nom du fichier
    
    Paramètres :
    --------------------------------------------------------------
    - option : Sélection du mode "by name" (NomEntreprise) ou "by csv file" (FichierCSV)
    - progress_container : Composant Streamlit pour afficher la progression.
    - NomEntreprise : Nom d'une entreprise spécifique (si aucun fichier CSV n'est fourni).
    - FichierCSV : Fichier CSV contenant une liste d'entreprises.
    - i : Indice de boucle initial (défaut = 1).
    - max_length : Nombre total de variations de noms (calculé si non fourni).
    - j : Compteur de progression.

    Return :
    --------------------------------------------------------------
    - Un DataFrame contenant les résultats de requêtes Overpass Turbo.
    - Une liste des entreprises traitées.
    - La valeur mise à jour de j (progression).
    """
    
    entreprises = []     
    j = 1
    if FichierCSV:
        FichierCSV.seek(0)  # Revenir au début du fichier
        # Lire le fichier en ignorant le BOM UTF-8
        file_content = FichierCSV.getvalue().decode("utf-8-sig")
        #file_content = FichierCSV.getvalue().decode("latin-1")
        # Lire le CSV en tant que DataFrame pandas
        try:
            df_entreprises = pd.read_csv(pd.io.common.StringIO(file_content), sep="|")
        except Exception as e:
            st.error(f"Erreur de lecture du fichier CSV : {e}")
            return None, []
        liste_entreprises = df_entreprises.iloc[:, 0].tolist()

        fName = []
        for entreprise in liste_entreprises:
            fName.append(__suppr__(entreprise))
        max_length = len(liste_entreprises)
        df_entreprises = pd.DataFrame(fName, columns=["Nom"])

        all_results = []  # Stocke tous les résultats pour concaténation
        j = 0
        for idx, row in df_entreprises.iterrows():
            entreprise = row.iloc[0]  # Nom de l'entreprise
            print(f"Traitement de l'entreprise : {entreprise}", flush = True)
            df_result, _, j = georef(option, progress_container, NomEntreprise=entreprise, max_length = max_length, j = j)
            if df_result is not None:
                all_results.append(df_result)
            j += 1
        # Concaténer tous les résultats en un seul DataFrame
        if all_results:
            df_final = pd.concat(all_results, ignore_index=True)
            print("Données combinées pour toutes les entreprises du fichier.", flush = True)
        else:
            df_final = pd.DataFrame()
            print("Aucune donnée extraite.", flush = True)
        return df_final, df_entreprises.iloc[:, 0].tolist(), j
    
    elif NomEntreprise :
        #pas opti on fait ce bloque 2 fois dans ce cas, une fois dans fichiercsv puis fois dans NomEntreprise a chaque itération du for
        #On s'assure de pas refaire 2 fois, car max_length uniquement en entrée de la fonction si fichier csv    
        fname = __suppr__(NomEntreprise) 
        osm_data = get_overpass_data(fname)
        if osm_data:
            df = process_osm_data(osm_data)
        else:
            print("No data", flush = True)
            df = pd.DataFrame()  # dataframe vide par défaut
        return df, [], j
