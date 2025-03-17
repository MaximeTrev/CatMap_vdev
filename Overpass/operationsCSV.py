import streamlit as st
import pandas as pd
import json
import time
import unidecode as u
import os

from requetes import Requetes as R
from requetes import *



def __suppr__(chain, Liste) : #sous-fonction
    ch = chain.upper()
    occ, i = Liste[0], 1
    lengthListe = len(Liste)
    while occ not in ch and i<lengthListe:
        occ = Liste[i]
        i+=1
    if i==lengthListe :
        return chain
    ch = ch.replace(occ, "")
    return ch.capitalize()

ListeLabel = [" SE", " SARL", " EI", " EURL", " SASU", " SAS", " SA", " SNC", " SCS", " SCA"]

def fromJSONtoDataFrame(Fichiers) : #Fichiers une liste de fichiers (JSON)
    Name = []
    Flag = []
    Lat = []
    Lon = []
    Source = []
    Amenity, Place, Shop, Power, Highway = [],[],[],[],[]
    for i in range(len(Fichiers)) :
        
        booleen = True
        
        if ".json" not in Fichiers[i] :
            booleen = False
        else:
            try:
                with open("json/"+Fichiers[i], "r") as JSON:
                    j = 1
                    dico = json.load(JSON)
                    for occ in dico :
                        dic = dico["iteration "+str(j)]
                        
                        try: Amenity.append(dic["amenity"]) 
                        #si amenity n'est pas renseigné cela renvoie une exception / erreur
                        #on va donc l' "attraper" avec Except et lui définir une valeur pré-choisie
                        except: Amenity.append("X")
                        
                        try: Source.append(dic["source"])
                        except: Source.append("X")
                        
                        try: Place.append(dic["place"])
                        except: Place.append("X")
                        
                        try: Shop.append(dic["shop"])
                        except: Shop.append("X")
                        
                        try: Power.append(dic["power"])
                        except: Power.append("X")
                        
                        try: Highway.append(dic["highway"])
                        except: Highway.append("X")
                        
                        Name.append(dic["name"])
                        Coordonnees = dic["coord"].split("/")
                        Lat.append(Coordonnees[0])
                        Lon.append(Coordonnees[1])
                        Flag.append(dic["flag"])
                        j+=1
                        booleen = True
            except:
                print(Fichiers[i], "fichier vide.")
                    
    if booleen :
        data = {"Source": Source, "Name": Name, "Amenity": Amenity, "Place": Place, "Shop": Shop, "Power": Power, "Highway": Highway, "Lat": Lat, "Long": Lon, "Flag": Flag}
        df = pd.DataFrame(data)
   
        print("\n",booleen, ": File saved.")
        return df
    else:
        print("\n",booleen, ": aucun fichier JSON trouvé.")

def __var_name__(name, booleen = False): #sous-fonction
    out = [] # 0 --> nom initial et on boucle direct dessus ?
    out.append((name.upper()))
    out.append((name.lower()))
    out.append((name.capitalize()))
    tests = [" ", "-","_"]
    test_esp = False
    for test in tests:
        #BLoc pour vérifier si 2 mots (ou plus) dans la chaîne
        #marche pas si plusieurs "sépérateurs" pour une chaîne
        if test in name:
            #bloc pour le test "mots composés"
            test_esp = test
            #ICI bloc pour le test "classique"
            #espace = test
            tests.remove(test)
            break
        
    for espace in tests:
        if test_esp :
            newName = name.replace(test_esp, espace)
            out.append((newName.upper()))
            out.append((newName.lower()))
            out.append((newName.capitalize()))
    
    liste = []
    
    i = 1
    for val in out :
        val = (val, i)
        liste.append(val)
        i += 1
    return liste # --> set avec toutes les variations de noms

##########################################################################################################################

def fromCSVtoJSON(option, progress_container, NomEntreprise="", FichierCSV="", i=1, max_length = None) :
    
    """
    - Paramètres
    --------------------------------------------------------------
    fichierCSV : TYPE
        Fichier CSV
        Format fichier CSV :
            - Nom de l'entreprise
            - Nom de l'entreprise à concaténer au nom du fichier en sortie
            - Requête (Overpass turbo)
            - délimiteur : | (sans espaces)
    
    - Tâche
    --------------------------------------------------------------
    Crée un fichier JSON pour 
    chaque entreprise.
    """
    
    print("Options :s \n 1 - Générer un fichier CSV depuis un autre fichier CSV. \n 2 - Générer un fichier CSV depuis une seule entreprise. \n")
    
    entreprises = []
        
    if FichierCSV != "":

        FichierCSV.seek(0)  # Revenir au début du fichier

        # Lire le fichier en ignorant le BOM UTF-8
        file_content = FichierCSV.getvalue().decode("utf-8-sig")
    
        # Lire le CSV en tant que DataFrame pandas
        try:
            df_entreprises = pd.read_csv(pd.io.common.StringIO(file_content), sep="|")
        except Exception as e:
            st.error(f"Erreur de lecture du fichier CSV : {e}")
            return None, []

        liste_entreprises = df_entreprises.iloc[:, 0].tolist()
        fName, varName, varName_ = [], [], []
        #IndNomInitial, nomInitial, _ = [], [], []
        i = 0
        for entreprise in liste_entreprises:
            fName.append(__suppr__(entreprise, ListeLabel))
            #print("Name :", fName[i])
            varName.append(__var_name__(fName[i])) #avec accents
            fName_ = u.unidecode(fName[i])
            if fName_ != fName[i] :
                varName_.append(__var_name__(fName_, True)) #True -> pas d'accent, donc le nom initial n'est pas présent
            i += 1
      
        temps = 0.0
        
        max_length=len(varName)+len(varName_)

        df_entreprises = pd.DataFrame(liste_entreprises, columns=["Nom"])

        #listeFichiers = []
        all_results = []  # Stocke tous les résultats pour concaténation
        

        for idx, row in df_entreprises.iterrows():
            entreprise = row.iloc[0]  # Nom de l'entreprise
            print(f"Traitement de l'entreprise : {entreprise}")
            df_result, _ = fromCSVtoJSON(option, progress_container, NomEntreprise=entreprise, max_length = max_length)
            if df_result is not None:
                all_results.append(df_result)

        # Concaténer tous les résultats en un seul DataFrame
        if all_results:
            df_final = pd.concat(all_results, ignore_index=True)
            print("Données combinées pour toutes les entreprises du fichier.")
        else:
            df_final = pd.DataFrame()
            print("Aucune donnée extraite.")

        return df_final, df_entreprises.iloc[:, 0].tolist()
    
    elif NomEntreprise != "" :
        #listeFichiers = []
        
        #pas opti on fait ce bloque 2 fois dans ce cas, une fois dans fichiercsv puis fois dans NomEntreprise a chaque itération du for
        #On s'assure de pas refaire 2 fois, car max_length uniquement en entrée de la fonction si fichier csv
        if max_length is None:
            max_length=len(varName)+len(varName_)
            fname = __suppr__(NomEntreprise, ListeLabel) 
            print("Name :", fname)
            fName = fname
            temps = 0.0
            varName, varName_ = [], []
            varName = __var_name__(fName) #avec accents
            #print("varName :", varName)
            fName_ = u.unidecode(fName)
            if fName_ != fName :
                varName_ = __var_name__(fName_, True) #True -> pas d'accent, donc le nom initial n'est pas présent

        if max_length is not None:
            max_length=len(varName)+len(varName_)
            
        j=0
        for (var, flag) in varName :
            j+=1         
            osm_data = get_overpass_data(var)
            if j <= 1:
                if osm_data:
                    df = process_osm_data(osm_data)
                    df["flag"] = flag   
                else:
                    print("No data")
            if j > 1:
                if osm_data:
                    df_trans = process_osm_data(osm_data)
                    df_trans["flag"] = flag   
                    df = pd.concat([df, df_trans], ignore_index=True)
                else:
                    print("No data")

            progress=j/max_length*100
            progress=round(progress)
            progress_container.markdown(
                f"""<div class="progress-bar" style="width: {progress}%;">
                {progress}%
            </div>""",
                unsafe_allow_html=True
            )

        time.sleep(1)
        
        for (var, flag) in varName_ :
            j+=1         
            #pas sur, a virer ?
            osm_data = get_overpass_data(var)
            if j <= 1:
                if osm_data:
                    df = process_osm_data(osm_data)
                    df["flag"] = flag   
                else:
                    print("No data")
            if j > 1:
                if osm_data:
                    df_trans = process_osm_data(osm_data)
                    df_trans["flag"] = flag   
                    df = pd.concat([df, df_trans], ignore_index=True)
                else:
                    print("No data")
            
            progress=j/max_length*100
            progress=round(progress)
            progress_container.markdown(
                f"""<div class="progress-bar" style="width: {progress}%;">
                {progress}%
            </div>""",
                unsafe_allow_html=True
            )
        
        print("Temps de génération fichier/s :", str(round(temps-2))+" secondes.\n") #-2 car on a fait time.sleep(1)*2
        print("Building(s): ", len(df))
        print(df)
        return df, []
