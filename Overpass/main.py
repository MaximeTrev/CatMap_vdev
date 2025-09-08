import streamlit as st
import pandas as pd
import folium
from folium import IFrame
from streamlit_folium import folium_static 
import plotly.graph_objects as go
import plotly.express as px
import os
import CSS as css
import mergeCountries as mc
import name_to_georef as ntg

css_path = os.path.join(os.path.dirname(__file__), "styles.css")
with open(css_path) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def pieChart(pays,entreprise, _effectif, effectif) :
    EffectifMax = sum(effectif)
    seuil = int(0.02 * EffectifMax)
    _effectif = _effectif[_effectif >= seuil]
    fig = go.Figure(data=[go.Pie(labels=_effectif.index, 
                                 values=_effectif, hole=0.3)],
                    layout_title_text=f"PieChart {entreprise}")
    return fig

# Fonction pour compter les occurrences (mise en cache pour optimiser)
@st.cache_data
def get_pays_counts(df):
    pays_counts = df["pays"].value_counts().reset_index()
    pays_counts.columns = ["pays", "count"]
    return pays_counts

#A adapter plus tard en fonction de la target: amenity + shop
def get_amenity_counts(df):
    amenity_counts = df["amenity"].value_counts().reset_index()
    amenity_counts.columns = ["amenity", "count"]
    return amenity_counts


def NAF_division_to_section(df, col_division="naf_division", col_section="naf_section_estimee"):
    """
    Ajoute une colonne avec la section NAF estimée à partir de l'intitulé de division.

    Source: Ensemble des postes de la NAF rév. 2, Libellés longs, courts et abrégés de tous les postes
    -> https://www.insee.fr/fr/information/2120875
    """
    naf_dict = {
    # SECTION A
    "Culture et production animale, chasse et services annexes": "AGRICULTURE, SYLVICULTURE ET PÊCHE",
    "Sylviculture et exploitation forestière": "AGRICULTURE, SYLVICULTURE ET PÊCHE",
    "Pêche et aquaculture": "AGRICULTURE, SYLVICULTURE ET PÊCHE",

    # SECTION B
    "Extraction de houille et de lignite": "INDUSTRIES EXTRACTIVES",
    "Extraction d'hydrocarbures": "INDUSTRIES EXTRACTIVES",
    "Extraction de minerais métalliques": "INDUSTRIES EXTRACTIVES",
    "Autres industries extractives": "INDUSTRIES EXTRACTIVES",
    "Services de soutien aux industries extractives": "INDUSTRIES EXTRACTIVES",

    # SECTION C
    "Industries alimentaires": "INDUSTRIE MANUFACTURIÈRE",
    "Fabrication de boissons": "INDUSTRIE MANUFACTURIÈRE",
    "Fabrication de produits à base de tabac": "INDUSTRIE MANUFACTURIÈRE",
    "Fabrication de textiles": "INDUSTRIE MANUFACTURIÈRE",
    "Industrie de l'habillement": "INDUSTRIE MANUFACTURIÈRE",
    "Industrie du cuir et de la chaussure": "INDUSTRIE MANUFACTURIÈRE",
    "Travail du bois et fabrication d'articles en bois et en liège, à l’exception des meubles ; fabrication d’articles en vannerie et sparterie": "INDUSTRIE MANUFACTURIÈRE",
    "Industrie du papier et du carton": "INDUSTRIE MANUFACTURIÈRE",
    "Imprimerie et reproduction d'enregistrements": "INDUSTRIE MANUFACTURIÈRE",
    "Cokéfaction et raffinage": "INDUSTRIE MANUFACTURIÈRE",
    "Industrie chimique": "INDUSTRIE MANUFACTURIÈRE",
    "Industrie pharmaceutique": "INDUSTRIE MANUFACTURIÈRE",
    "Fabrication de produits en caoutchouc et en plastique": "INDUSTRIE MANUFACTURIÈRE",
    "Fabrication d'autres produits minéraux non métalliques": "INDUSTRIE MANUFACTURIÈRE",
    "Métallurgie": "INDUSTRIE MANUFACTURIÈRE",
    "Fabrication de produits métalliques, à l’exception des machines et des équipements": "INDUSTRIE MANUFACTURIÈRE",
    "Fabrication de produits informatiques, électroniques et optiques": "INDUSTRIE MANUFACTURIÈRE",
    "Fabrication d'équipements électriques": "INDUSTRIE MANUFACTURIÈRE",
    "Fabrication de machines et équipements n.c.a.": "INDUSTRIE MANUFACTURIÈRE",
    "Industrie automobile": "INDUSTRIE MANUFACTURIÈRE",
    "Fabrication d'autres matériels de transport": "INDUSTRIE MANUFACTURIÈRE",
    "Fabrication de meubles": "INDUSTRIE MANUFACTURIÈRE",
    "Autres industries manufacturières": "INDUSTRIE MANUFACTURIÈRE",
    "Réparation et installation de machines et d'équipements": "INDUSTRIE MANUFACTURIÈRE",

    # SECTION D
    "Production et distribution d'électricité, de gaz, de vapeur et d'air conditionné": "PRODUCTION ET DISTRIBUTION D'ÉLECTRICITÉ, DE GAZ, DE VAPEUR ET D'AIR CONDITIONNÉ",

    # SECTION E
    "Captage, traitement et distribution d'eau": "PRODUCTION ET DISTRIBUTION D'EAU ; ASSAINISSEMENT, GESTION DES DÉCHETS ET DÉPOLLUTION",
    "Collecte et traitement des eaux usées": "PRODUCTION ET DISTRIBUTION D'EAU ; ASSAINISSEMENT, GESTION DES DÉCHETS ET DÉPOLLUTION",
    "Collecte, traitement et élimination des déchets ; récupération": "PRODUCTION ET DISTRIBUTION D'EAU ; ASSAINISSEMENT, GESTION DES DÉCHETS ET DÉPOLLUTION",
    "Dépollution et autres services de gestion des déchets": "PRODUCTION ET DISTRIBUTION D'EAU ; ASSAINISSEMENT, GESTION DES DÉCHETS ET DÉPOLLUTION",

    # SECTION F
    "Construction de bâtiments": "CONSTRUCTION",
    "Génie civil": "CONSTRUCTION",
    "Travaux de construction spécialisés": "CONSTRUCTION",

    # SECTION G
    "Commerce et réparation d'automobiles et de motocycles": "COMMERCE ; RÉPARATION D'AUTOMOBILES ET DE MOTOCYCLES",
    "Commerce de gros, à l’exception des automobiles et des motocycles": "COMMERCE ; RÉPARATION D'AUTOMOBILES ET DE MOTOCYCLES",
    "Commerce de détail, à l’exception des automobiles et des motocycles": "COMMERCE ; RÉPARATION D'AUTOMOBILES ET DE MOTOCYCLES",

    # SECTION H
    "Transports terrestres et transport par conduites": "TRANSPORTS ET ENTREPOSAGE",
    "Transports par eau": "TRANSPORTS ET ENTREPOSAGE",
    "Transports aériens": "TRANSPORTS ET ENTREPOSAGE",
    "Entreposage et services auxiliaires des transports": "TRANSPORTS ET ENTREPOSAGE",
    "Activités de poste et de courrier": "TRANSPORTS ET ENTREPOSAGE",

    # SECTION I
    "Hébergement": "HÉBERGEMENT ET RESTAURATION",
    "Restauration": "HÉBERGEMENT ET RESTAURATION",

    # SECTION J
    "Édition": "INFORMATION ET COMMUNICATION",
    "Production de films cinématographiques, de vidéo et de programmes de télévision ; enregistrement sonore et édition musicale": "INFORMATION ET COMMUNICATION",
    "Programmation et diffusion": "INFORMATION ET COMMUNICATION",
    "Télécommunications": "INFORMATION ET COMMUNICATION",
    "Programmation, conseil et autres activités informatiques": "INFORMATION ET COMMUNICATION",
    "Services d'information": "INFORMATION ET COMMUNICATION",

    # SECTION K
    "Activités des services financiers, hors assurance et caisses de retraite": "ACTIVITÉS FINANCIÈRES ET D'ASSURANCE",
    "Assurance": "ACTIVITÉS FINANCIÈRES ET D'ASSURANCE",
    "Activités auxiliaires de services financiers et d'assurance": "ACTIVITÉS FINANCIÈRES ET D'ASSURANCE",

    # SECTION L
    "Activités immobilières": "ACTIVITÉS IMMOBILIÈRES",

    # SECTION M
    "Activités juridiques et comptables": "ACTIVITÉS SPÉCIALISÉES, SCIENTIFIQUES ET TECHNIQUES",
    "Activités des sièges sociaux ; conseil de gestion": "ACTIVITÉS SPÉCIALISÉES, SCIENTIFIQUES ET TECHNIQUES",
    "Activités d'architecture et d'ingénierie ; activités de contrôle et analyses techniques": "ACTIVITÉS SPÉCIALISÉES, SCIENTIFIQUES ET TECHNIQUES",
    "Recherche-développement scientifique": "ACTIVITÉS SPÉCIALISÉES, SCIENTIFIQUES ET TECHNIQUES",
    "Publicité et études de marché": "ACTIVITÉS SPÉCIALISÉES, SCIENTIFIQUES ET TECHNIQUES",
    "Autres activités spécialisées, scientifiques et techniques": "ACTIVITÉS SPÉCIALISÉES, SCIENTIFIQUES ET TECHNIQUES",
    "Activités vétérinaires": "ACTIVITÉS SPÉCIALISÉES, SCIENTIFIQUES ET TECHNIQUES",

    # SECTION N
    "Activités de location et location-bail": "ACTIVITÉS DE SERVICES ADMINISTRATIFS ET DE SOUTIEN",
    "Activités liées à l'emploi": "ACTIVITÉS DE SERVICES ADMINISTRATIFS ET DE SOUTIEN",
    "Activités des agences de voyage, voyagistes, services de réservation et activités connexes": "ACTIVITÉS DE SERVICES ADMINISTRATIFS ET DE SOUTIEN",
    "Enquêtes et sécurité": "ACTIVITÉS DE SERVICES ADMINISTRATIFS ET DE SOUTIEN",
    "Services relatifs aux bâtiments et aménagement paysager": "ACTIVITÉS DE SERVICES ADMINISTRATIFS ET DE SOUTIEN",
    "Activités administratives et autres activités de soutien aux entreprises": "ACTIVITÉS DE SERVICES ADMINISTRATIFS ET DE SOUTIEN",

    # SECTION O
    "Administration publique et défense ; sécurité sociale obligatoire": "ADMINISTRATION PUBLIQUE",

    # SECTION P
    "Enseignement": "ENSEIGNEMENT",

    # SECTION Q
    "Activités pour la santé humaine": "SANTÉ HUMAINE ET ACTION SOCIALE",
    "Hébergement médico-social et social": "SANTÉ HUMAINE ET ACTION SOCIALE",
    "Action sociale sans hébergement": "SANTÉ HUMAINE ET ACTION SOCIALE",

    # SECTION R
    "Activités créatives, artistiques et de spectacle": "ARTS, SPECTACLES ET ACTIVITÉS RÉCRÉATIVES",
    "Bibliothèques, archives, musées et autres activités culturelles": "ARTS, SPECTACLES ET ACTIVITÉS RÉCRÉATIVES",
    "Organisation de jeux de hasard et d'argent": "ARTS, SPECTACLES ET ACTIVITÉS RÉCRÉATIVES",
    "Activités sportives, récréatives et de loisirs": "ARTS, SPECTACLES ET ACTIVITÉS RÉCRÉATIVES",

    # SECTION S
    "Activités des organisations associatives": "AUTRES ACTIVITÉS DE SERVICES",
    "Réparation d'ordinateurs et de biens personnels et domestiques": "AUTRES ACTIVITÉS DE SERVICES",
    "Autres services personnels": "AUTRES ACTIVITÉS DE SERVICES",

    # SECTION T
    "Activités des ménages en tant qu'employeurs de personnel domestique": "ACTIVITÉS DES MÉNAGES EN TANT QU'EMPLOYEURS ; ACTIVITÉS INDIFFÉRENCIÉES DES MÉNAGES EN TANT QUE PRODUCTEURS DE BIENS ET SERVICES POUR USAGE PROPRE",
    "Activités indifférenciées des ménages en tant que producteurs de biens et services pour usage propre": "ACTIVITÉS DES MÉNAGES EN TANT QU'EMPLOYEURS ; ACTIVITÉS INDIFFÉRENCIÉES DES MÉNAGES EN TANT QUE PRODUCTEURS DE BIENS ET SERVICES POUR USAGE PROPRE",

    # SECTION U
    "Activités des organisations et organismes extraterritoriaux": "ACTIVITÉS EXTRA-TERRITORIALES"

    df[col_section] = df[col_division].map(naf_dict)
    
    return df


def show_map(df):
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=5)
    
    for _, row in df.iterrows():
        _popup=str(row["lat"]) + " " + str(row["long"]) + "\n"
        _popup +="name:"+row["name"]+"\n"
        _popup += "amenity:"+row["amenity"]
        cssClassPopup = css.__CssClassPopup()
        _popup = f"""<div style="{cssClassPopup}">{_popup}</div>"""
            
        iframe = IFrame(_popup, width=105, height=80)  # Ajuster la taille ici
        popup = folium.Popup(iframe, max_width=250)  # Ajuster la largeur max du popup
        folium.CircleMarker(
            location=[float(row["lat"]), float(row["long"])],
            radius=6,
            weight=0,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.6,
            popup=popup
        ).add_to(m)
    folium_static(m)

def __main__(progress_container, option, NomEntreprise="", FichierCSV="") :
    listeFichiers, entreprise = [], ""
    dfOut = pd.DataFrame()
    
    if option == NomEntreprise:
        entreprise = st.text_input("Company name")
        
        progress_container.markdown(
            '<span class="progress-bar-container">Loading ...<div class="progress-bar" id="progress"></div></span>',
            unsafe_allow_html=True)
            
        if entreprise != "":
            listeFichiers, _, = ntg.georef(option, progress_container, entreprise, "")
            
            #si pas de résultats, homogénéisation du nom plante
            if not listeFichiers.empty:
                listeFichiers["name"] = listeFichiers["name"].str.upper()
                dfOut, Pays = mc.findCountry(listeFichiers)
            
            #st.markdown(f'<span style="font-size:12px; margin-left:10px;"> {dfOut.shape[0]} results </span>', unsafe_allow_html=True)
            st.write(f"{dfOut.shape[0]} results")
            st.dataframe(dfOut)
            show_map(dfOut)
               
    elif option == FichierCSV:
        entreprise = "résultats entreprises"
        uploaded_file = st.file_uploader("Select CSV file", type=["csv"])   
        progress_container.markdown(
            '<span class="progress-bar-container">Loading ...<div class="progress-bar" id="progress"></div></span>',
            unsafe_allow_html=True)
        
        if uploaded_file is not None:
            # Initialisation des variable
            listeFichiers, entreprises = ntg.georef(option, progress_container, "", uploaded_file) #possible de virer les ""
            listeFichiers["name"] = listeFichiers["name"].str.upper()

            #Check si des noms n'ont pas de résultats 
            no_results=  []
            uploaded_df = pd.read_csv(uploaded_file)
            for name in uploaded_df.iloc[:, 0].str.upper():
                if name not in set(listeFichiers["name"]):
                    no_results.append(name)
            
            dfOut, Pays = mc.findCountry(listeFichiers)
            st.write(f"{dfOut.shape[0]} results (download available)")
            st.write(f"No result for: {', '.join(no_results)}")
            entreprises.pop()
            st.dataframe(dfOut)
            show_map(dfOut) 
            
    try:
        if dfOut is not None:
            st.session_state.dfOut = dfOut
            
            # Bloc NAF
                # Amenity -> section NAF
            amenity_NAF = pd.read_csv(r"Overpass/NAF/amenity_with_naf.csv")
            dfOut = dfOut.merge(amenity_NAF[["amenity", "naf_section"]], on="amenity", how="left")

                # Shop -> sous section NAF
            shop_NAF = pd.read_csv(r"Overpass/NAF/shop_with_naf.csv")
            dfOut = dfOut.merge(shop_NAF[["amenity", "naf_division"]], on="amenity", how="left")

                # Regroupement des sous-section en section
            dfOut = NAF_division_to_section(dfOut)
            df[naf_section_f] = df[naf_section].fillna(df[naf_section_estime])


            
        else:
            st.write("Erreur : dfOut is void")
        col_fig1, col_fig2 = st.columns(2)
        
        with col_fig1:
            # Plot camembert de la repartition de la sélection par pays en fonction des noms
            with st.expander("Select companie(s)", expanded=False):
                selected_names = st.multiselect(
                    "Companie(s):", 
                    options=st.session_state.dfOut["name"].unique(),
                    default=st.session_state.dfOut["name"].unique())  # Tout sélectionné par défaut)
            # Appliquer le filtre sur dfOut
            filtered_df = st.session_state.dfOut[st.session_state.dfOut["name"].isin(selected_names)]
            pays_counts = get_pays_counts(filtered_df)
        
            # Limiter à 10 catégories max
            if len(pays_counts) > 10:
                # Trier les pays par nombre d'occurrences décroissant
                pays_counts = pays_counts.sort_values(by="count", ascending=False)
                top_pays = pays_counts.iloc[:10]
                other_count = pays_counts.iloc[10:]["count"].sum()
                other_row = pd.DataFrame([["Autres", other_count]], columns=["pays", "count"])
                pays_counts = pd.concat([top_pays, other_row], ignore_index=True)
                
            # Afficher le Pie Chart
            # Création des colonnes pour la mise en page
            fig = px.pie(pays_counts, names="pays", values="count")
            fig.update_layout(
                legend=dict(font=dict(size=8)),
                margin=dict(l=5, r=50))
            fig.update_traces(texttemplate="%{percent:.0%}")
            st.plotly_chart(fig, use_container_width=True)

        with col_fig2:
            # Plot camembert de la repartition amenity (à modifier plus tard) en fonction du pays
            with st.expander("Select country(ies)", expanded=False):
                selected_country = st.multiselect(
                    "Country(ies):", 
                    options=st.session_state.dfOut["pays"].unique(),
                    default=st.session_state.dfOut["pays"].unique()  # Tout sélectionné par défaut
                )
            # Appliquer le filtre sur dfOut
            filtered_df2 = st.session_state.dfOut[st.session_state.dfOut["pays"].isin(selected_country)]
            amenity_counts = get_amenity_counts(filtered_df2)
        
            # Limiter à 10 catégories max
            if len(amenity_counts) > 10:
                # Trier les amenities par nombre d'occurrences décroissant
                amenity_counts = amenity_counts.sort_values(by="count", ascending=False)
                top_amenity = amenity_counts.iloc[:10]
                other_count2 = amenity_counts.iloc[10:]["count"].sum()
                other_amenity = pd.DataFrame([["Autres", other_count2]], columns=["amenity", "count"])
                amenity_counts = pd.concat([top_amenity, other_amenity], ignore_index=True)
                
            # Afficher le Pie Chart
            # Création des colonnes pour la mise en page
            fig2 = px.pie(amenity_counts, names="amenity", values="count")
            fig2.update_layout(
                legend=dict(font=dict(size=8)),
                margin=dict(l=5, r=50))
            fig2.update_traces(texttemplate="%{percent:.0%}")
            st.plotly_chart(fig2, use_container_width=True)
        
    except:
        pass
    
    
def load() :
    # Création de la disposition en trois colonnes pour la bannière
    col1, col2, col3 = st.columns([1, 4, 1])  # Colonnes de tailles différentes
    with col2:
        st.image("Overpass/PNG/TopBanner.png", width=1500)
    
    NomEntreprise = "Geolocation of company buildings by name"
    FichierCSV = "Geolocation of company buildings by csv file"
    option = st.radio("Select the chosen method :", (NomEntreprise, FichierCSV))
    st.write(option)
    
    # Conteneur pour la barre de progression
    barre_de_chargement = st.empty()
    
    __main__(barre_de_chargement, option, NomEntreprise, FichierCSV)
    
    # Fin du bloc HTML
    st.markdown('</div>', unsafe_allow_html=True)
load()
