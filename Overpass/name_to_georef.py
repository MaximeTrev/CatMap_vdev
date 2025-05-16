import streamlit as st
import pandas as pd
import json
import time
import unidecode as u
import os
from requetes import *

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        # Récupérer les valeurs de NomEntreprise et FichierCSV
        FichierCSV = kwargs.get('FichierCSV', None)
        NomEntreprise = kwargs.get('NomEntreprise', None)

        if FichierCSV:  # Mode FichierCSV (avec appels récursifs)
            if "timing_start" not in st.session_state:  
                # Premier appel en mode FichierCSV => On démarre le chronomètre
                st.session_state.timing_start = time.time()
                st.session_state.is_first_call = True  # Marquer comme premier appel
            
            result = func(*args, **kwargs)  # Exécution de la fonction
            
            if st.session_state.is_first_call:
                # Afficher le temps total une seule fois (quand le premier appel termine)
                elapsed_time = time.time() - st.session_state.timing_start
                st.markdown(f'<p style="font-size:14px;margin-bottom: 2px;">Total Computing time: {round(elapsed_time, 2)} s</p>', unsafe_allow_html=True)
                
                # Réinitialiser pour la prochaine exécution
                del st.session_state["timing_start"]
                del st.session_state["is_first_call"]

            return result

        elif NomEntreprise and FichierCSV is None:  # Mode NomEntreprise (et FichierCSV n'est PAS renseigné)
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            st.markdown(f'<p style="font-size:14px;margin-bottom: 2px;">Computing time: {round(elapsed_time, 2)} s</p>', unsafe_allow_html=True)
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

def __var_name__(name): #sous-fonction
    """
    - Détermination des combinaisons potentielles des noms (xxx, Xxx, XXX) 
    - /!\ On considère uniquement les accents si dans le nom initial
    - Détermination si nom composé (" ", -, _) et réalisation des combinaisons potentielles
    - Check si caractère spéciaux (accents..), si oui prend également la version sans accents. Les flags ne tiennent pas compte de la présence ou non d'accents.
    - Attribution d'un flag normalisé à chaque type de nom pour contrôler la qualité des résultats
    - Flag : 
        - 0 (nom original, prioritaire sur le reste si doublon)
        - 1, 2, 3 (XXX, xxx, Xxx)
        - 4, 5, 5, 7 (XXX XXX, xxx xxx, Xxx xxx, Xxx Xxx) a adapter la norme change en fonction des espaces
        - 8, 9, 10, 11 (XXX-XXX, xxx-xxx, Xxx-xxx, Xxx-Xxx)
        - 12, 13, 14, 15 (XXX_XXX, xxx_xxx, Xxx_xxx, Xxx_Xxx)

        Pas sur que les espaces en - et _ soient utiles..
        A rajouter: vérifier si caractère spécial, si oui on le rend en ASCII et on chèque combi
    """
    
    variations = [] # 0 --> nom initial et on boucle direct dessus ?
    variations.append((name, 0)) #nom initial + rajouter drop duplicate
    
    separateurs = [" ", "-","_"] #test des séparateurs

    # Bloc pour vérifier la présence uniquement d'un type séparateur.
    detected_sep = None
    for sep in separateurs:
        if sep in name:
            detected_sep = sep
            break          
    if detected_sep:
        # Déterminer la base flag selon le séparateur détecté
        base_flag = 4  # Pour les noms avec espace
        variations.append((name.replace(detected_sep," ").upper(), base_flag))        
        variations.append((name.replace(detected_sep," ").lower(), base_flag + 1))     
        variations.append((name.replace(detected_sep," ").capitalize(), base_flag + 2))
        variations.append((name.replace(detected_sep," ").title(), base_flag + 3))    

        base_flag = 8  # Pour les noms avec tiret
        variations.append((name.replace(detected_sep,"-").upper(), base_flag))        
        variations.append((name.replace(detected_sep,"-").lower(), base_flag + 1))     
        variations.append((name.replace(detected_sep,"-").capitalize(), base_flag + 2))
        variations.append((name.replace(detected_sep,"-").title(), base_flag + 3))      

        base_flag = 12  # Pour les noms avec underscore
        variations.append((name.replace(detected_sep,"_").upper(), base_flag))        
        variations.append((name.replace(detected_sep,"_").lower(), base_flag + 1))     
        variations.append((name.replace(detected_sep,"_").capitalize(), base_flag + 2))
        variations.append((name.replace(detected_sep,"_").title(), base_flag + 3))

    else:
        variations.append((name.upper(), 1)) #XXX
        variations.append((name.lower(), 2)) #xxx
        variations.append((name.capitalize(), 3)) #Xxx

    #Suppression des doublons avec le Flag 0, et si doublon on garde le Flag 0
    var_noduplicata = [variations[0]] # Référence (flag 0)
    for name, flag in variations:
        if variations[0][0] != name :
            var_noduplicata.append((name, flag))
    return var_noduplicata # --> set avec toutes les variations de noms

#@timing_decorator
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
    if FichierCSV:
        FichierCSV.seek(0)  # Revenir au début du fichier
        # Lire le fichier en ignorant le BOM UTF-8
        #file_content = FichierCSV.getvalue().decode("utf-8-sig")
        file_content = FichierCSV.getvalue().decode("latin-1")
        # Lire le CSV en tant que DataFrame pandas
        try:
            df_entreprises = pd.read_csv(pd.io.common.StringIO(file_content), sep="|")
        except Exception as e:
            st.error(f"Erreur de lecture du fichier CSV : {e}")
            return None, []
        liste_entreprises = df_entreprises.iloc[:, 0].tolist()

        #Détermination des variations des noms d'entreprises + correction bruits (SE, SARL...)
        fName, varName, varName_ = [], [], []
        i = 0
        for entreprise in liste_entreprises:
            fName.append(__suppr__(entreprise))
            varName.append(__var_name__(fName[i]))
            fName_ = u.unidecode(fName[i])
            if fName_ != fName[i] :
                varName_.append(__var_name__(fName_)) #True -> pas d'accent, donc le nom initial n'est pas présent
            i += 1

        max_length = sum(len(name) for name in varName) + sum(len(name) for name in varName_)
        df_entreprises = pd.DataFrame(liste_entreprises, columns=["Nom"])

        all_results = []  # Stocke tous les résultats pour concaténation
        j = 0
        for idx, row in df_entreprises.iterrows():
            entreprise = row.iloc[0]  # Nom de l'entreprise
            print(f"Traitement de l'entreprise : {entreprise}")
            df_result, _, j = georef(option, progress_container, NomEntreprise=entreprise, max_length = max_length, j = j)
            if df_result is not None:
                all_results.append(df_result)

        # Concaténer tous les résultats en un seul DataFrame
        if all_results:
            df_final = pd.concat(all_results, ignore_index=True)
            print("Données combinées pour toutes les entreprises du fichier.")
        else:
            df_final = pd.DataFrame()
            print("Aucune donnée extraite.")
        return df_final, df_entreprises.iloc[:, 0].tolist(), j
    
    elif NomEntreprise :
        #pas opti on fait ce bloque 2 fois dans ce cas, une fois dans fichiercsv puis fois dans NomEntreprise a chaque itération du for
        #On s'assure de pas refaire 2 fois, car max_length uniquement en entrée de la fonction si fichier csv    
        fname = __suppr__(NomEntreprise) 
        print("Name :", fname)
        fName = fname
        varName, varName_ = [], []
        varName = __var_name__(fName) #avec accents
        fName_ = u.unidecode(fName) #on check caractère spéciaux
        if fName_ != fName :
            varName_ = __var_name__(fName_) #True -> pas d'accent, donc le nom initial n'est pas présent
        if max_length is None:
            max_length=len(varName)+len(varName_)
            
        first_iter = True
        for (var, flag) in varName :         
            osm_data = get_overpass_data(var)
            if first_iter:
                first_iter = False
                if osm_data:
                    df = process_osm_data(osm_data)
                    df["flag"] = flag   
                else:
                    print("No data")
            else:
                if osm_data:
                    df_trans = process_osm_data(osm_data)
                    df_trans["flag"] = flag   
                    df = pd.concat([df, df_trans], ignore_index=True)
                else:
                    print("No data")
            j+=1
            progress=j/max_length*100
            progress=round(progress)
            progress_container.markdown(
                f"""<div class="progress-bar" style="width: {progress}%;">
                {progress}%
            </div>""",
                unsafe_allow_html=True)
        time.sleep(1)
        
        first_iter = True
        for (var, flag) in varName_ :
            #pas sur, a virer ?
            osm_data = get_overpass_data(var)
            if first_iter:
                first_iter = False
                if osm_data:
                    df_ = process_osm_data(osm_data)
                    df_["flag"] = flag   
                else:
                    print("No data")
            else:
                if osm_data:
                    df_trans = process_osm_data(osm_data)
                    df_trans["flag"] = flag   
                    df_ = pd.concat([df_, df_trans], ignore_index=True)
                else:
                    print("No data")
            j+=1
            progress=j/max_length*100
            progress=round(progress)
            progress_container.markdown(
                f"""<div class="progress-bar" style="width: {progress}%;">
                {progress}%
            </div>""",
                unsafe_allow_html=True)
            df = pd.concat([df, df_], ignore_index=True)
        return df, [], j
