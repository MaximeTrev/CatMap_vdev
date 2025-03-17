# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 09:39:21 2025

@author: jerome.hertzog_squar
"""

from selenium import webdriver
import pandas as pd
import os

def testCoordonnees(fichierCSV, fichierOut) :
    
    """
    Paramètres
    ----------
    fichierCSV : TYPE
        Fichier CSV
    fichierOut : TYPE
        Fichier CSV

    Créer un fichier CSV contenant des informations pour chaque adresse, ainsi que
    le degré de précision
    Returns
    -------
    None.
    """
    
    driver_maps= webdriver.Chrome()
    driver_nominatim= webdriver.Chrome()

    driver_maps.get("https://www.google.com/maps") 
    driver_nominatim.get("https://nominatim.openstreetmap.org/ui")
    with open(fichierCSV, newline='', encoding='utf-8') as csvfile:
        df = pd.read_csv(csvfile, delimiter=';')
        
        

        # Extraire 500 lignes aléatoires sans rendre les résultats reproductibles
        spamreader = df.sample(n=500)
        
        # Afficher le résultat
        print(spamreader.iterrows())
        i=0
        
        NomEntreprise = []
        Coeff = []
        Coordonnees = []
        Commentaires = []
        dictOut = {}
        
        Place = []
        Highway = []
        Power = []
        Shop = []
        Source = []
        Amenity = []
        
            
        for occ, row in spamreader.iterrows():
            if i<500 :
                i+=1
                print(row)
                Lat = row.iloc[7]
                Long = row.iloc[8]
                source = row.iloc[0]
                amenity = row.iloc[2]
                place = row.iloc[3]
                highway = row.iloc[6]
                power = row.iloc[5]
                shop = [4]
                coordonnees_api = str(Lat)+","+str(Long)
                
                maps_url = f"https://www.google.com/maps/place/{Lat},{Long}/@{Lat},{Long},15z"
                nominatim = f"https://nominatim.openstreetmap.org/ui/search.html?q={coordonnees_api}"
                driver_maps.get(maps_url)
                driver_nominatim.get(nominatim)
                print(row.iloc[1], ":", i , "Bonne précision (1) : laisser vide, mauvaise : 0, peut-être : 2 ; Sortir : exit")
                out = input()
                coeff = 1
                commentaire = ""
                
                if out == "exit" :
                    bDictVide = (NomEntreprise == [] 
                                  and Coeff == []
                                  and Coordonnees == []
                                  and Commentaires == []
                                  and Place == []
                                  and Highway == []
                                  and Power == []
                                  and Shop == []
                                  and Source == []
                                  and Amenity == [])
                    bFileExists = os.path.isfile(fichierOut) #: comme son nom l'indique
                    
                    if not bDictVide :
                        dictOut = {"Nom" : NomEntreprise, 
                                   "Precision" : Coeff, 
                                   "Coordonnees" : Coordonnees, 
                                   "Commentaires" : Commentaires,
                                   "Source" : Source,
                                   "Amenity" : Amenity,
                                   "Place" : Place,
                                   "Shop" : Shop,
                                   "Power" : Power,
                                   "Highway" : Highway}
                        df = pd.DataFrame(dictOut)

                        #df_file.to_csv(fichierOut, sep=";", header=False, index=False)
                        if bFileExists:
                            df.to_csv(fichierOut, mode='a', sep=";", header=False, index=False)
                        else:
                            df.to_csv(fichierOut, sep=";", header=True, index=False)
                            
                        df_file = pd.read_csv(fichierOut, sep=";", encoding='latin1')
                        doublons = df_file.duplicated(keep=False).sum()
                        
                        if doublons>0 :
                            df_file = df_file.drop_duplicates(keep='first')
                            df_file.to_csv(fichierOut, sep=";", header=False, index=False)
                            print("doublons trouvés")
                        else:
                            print("aucun doublon trouvé")
                    break
                   
                #oui : coefficient de précision 1 (valeur par défaut)
                #non : coefficient de précision 0
                elif out == "0" :
                    coeff = 0
                
                elif out == "2" :
                    coeff = 2
                #peut-être : coefficient de précision 2
                print("Commentaire :", end="")
                commentaire = input()
                NomEntreprise.append(row.iloc[1])
                Coeff.append(coeff)
                Coordonnees.append(str(Lat)+", "+str(Long))
                Commentaires.append(commentaire)
                Source.append(source)
                Place.append(place)
                Highway.append(highway)
                Power.append(power)
                Shop.append(shop)
                Amenity.append(amenity)
            else :
                break
        print("On est sortis de la boucle.")
    driver_maps.close() #ferme l'onglet ouvert
    driver_nominatim.close()
    
input_ = "../fichierGlobalTests.csv"
output_ = "résultats-comparatifs/fichierGlobalTests_automatise2.csv"
#testCoordonnees(input_, output_)

def testCoordonneesTag(fichierCSV, fichierOut) :
    """

    Paramètres
    ----------
    fichierCSV : TYPE
        Fichier CSV
    fichierOut : TYPE
        Fichier CSV

    Créer un fichier CSV contenant des informations pour chaque adresse, ainsi que
    le degré de précision
    Returns
    -------
    None.

    """
    driver_maps= webdriver.Chrome()
    driver_nominatim= webdriver.Chrome()

    driver_maps.get("https://www.google.com/maps") 
    driver_nominatim.get("https://nominatim.openstreetmap.org/ui")
    with open(fichierCSV, newline='', encoding='latin1') as csvfile:
        spamreader = pd.read_csv(csvfile, delimiter=';')
        
        

        # Extraire 500 lignes aléatoires sans rendre les résultats reproductibles
        #spamreader = df.sample(n=15)
        
        # Afficher le résultat
        print(spamreader.iterrows())
        i=0
        
        
        
            
        for occ, row in spamreader.iterrows():
            NomEntreprise = []
            Coeff = []
            Coordonnees = []
            Commentaires = []
            dictOut = {}
            
            Place = []
            Highway = []
            Power = []
            Shop = []
            Source = []
            Amenity = []
            
            i+=1
            print(row)
            Lat = float(row.iloc[2][1:])
            Long = float(row.iloc[3][1:])
            #source = row.iloc[0]
            amenity = row.iloc[1]
            #place = row.iloc[1]
            #highway = row.iloc[1]
            #power = row.iloc[5]
            #shop = [4]
            coordonnees_api = str(Lat)+","+str(Long)
            
            maps_url = f"https://www.google.com/maps/place/{Lat},{Long}/@{Lat},{Long},15z"
            nominatim = f"https://nominatim.openstreetmap.org/ui/search.html?q={coordonnees_api}"
            driver_maps.get(maps_url)
            driver_nominatim.get(nominatim)
            print(row.iloc[1], ":", i , "Bonne précision (1) : laisser vide, mauvaise : 0, peut-être : 2 ; Sortir : exit")
            out = input()
            
            coeff = 1
            commentaire = ""
            
            if out == "exit" :
                df_file = pd.read_csv(fichierOut, sep=";", encoding='latin1')
                doublons = df_file.duplicated(keep=False).sum()
                
                if doublons>0 :
                    df_file = df_file.drop_duplicates(keep='first')
                    df_file.to_csv(fichierOut, sep=";", header=False, index=False)
                    print("doublons trouvés")
                else:
                    print("aucun doublon trouvé")
                break
            #oui : coefficient de précision 1 (valeur par défaut)
            #non : coefficient de précision 0
            elif out == "0" :
                coeff = 0
            
            elif out == "2" :
                coeff = 2
            
            #peut-être : coefficient de précision 2
            print("Commentaire :", end="")
            commentaire = input()
            NomEntreprise.append(row.iloc[0])
            Coeff.append(coeff)
            Coordonnees.append(str(Lat)+", "+str(Long))
            Commentaires.append(commentaire)
            try: Source.append(source)
            except: Source.append("X")
            try: Place.append(place)
            except:  Place.append("X")
            try: Highway.append(highway)
            except:  Highway.append("")
            try: Power.append(power)
            except:  Power.append("")
            try: Shop.append(shop)
            except:  Shop.append("")
            try: Amenity.append(amenity)
            except:  Amenity.append("")
            
            
            bDictVide = (NomEntreprise == [] 
                          and Coeff == []
                          and Coordonnees == []
                          and Commentaires == []
                          and Place == []
                          and Highway == []
                          and Power == []
                          and Shop == []
                          and Source == []
                          and Amenity == [])
            bFileExists = os.path.isfile(fichierOut) #: comme son nom l'indique
            
            if not bDictVide :
                dictOut = {"Nom" : NomEntreprise, 
                           "Precision" : Coeff, 
                           "Coordonnees" : Coordonnees, 
                           "Commentaires" : Commentaires,
                           "Source" : Source,
                           "Amenity" : Amenity,
                           "Place" : Place,
                           "Shop" : Shop,
                           "Power" : Power,
                           "Highway" : Highway}
                df = pd.DataFrame(dictOut)

                #df_file.to_csv(fichierOut, sep=";", header=False, index=False)
                if bFileExists:
                    df.to_csv(fichierOut, mode='a', sep=";", header=False, index=False)
                else:
                    df.to_csv(fichierOut, sep=";", header=True, index=False)
                    
                df_file = pd.read_csv(fichierOut, sep=";", encoding='latin1')
                doublons = df_file.duplicated(keep=False).sum()
                
                if doublons>0 :
                    df_file = df_file.drop_duplicates(keep='first')
                    df_file.to_csv(fichierOut, sep=";", header=True, index=False)
                    print("doublons trouvés")
                else:
                    print("aucun doublon trouvé")
               
            
            

        print("On est sortis de la boucle.")
    driver_maps.close() #ferme l'onglet ouvert
    driver_nominatim.close()
    
input_ = "csv/TagsAmenityTests/MainAmenity_2-10.csv"
output_ = "résultats-comparatifs/TagsAmenity/fichierTests_Amenity_2-10.csv"
testCoordonneesTag(input_, output_)