import pandas as pd 
import plotly.express as px 
import streamlit as st 
import folium 
from streamlit_folium import st_folium 


# Configuration de la page Streamlit
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

@st.cache_data
def get_data_from_excel1():
    df = pd.read_excel(
        io="DATA.xlsx",
        engine="openpyxl",
        sheet_name="Base_avec_formules",
        usecols="A:M",
        nrows=1000
    )
    return df


@st.cache_data
def get_data_from_excel2():
    df2 = pd.read_excel(
        io="DATA.xlsx",
        engine="openpyxl",
        sheet_name="Objectifs",
        nrows=10
    )
    return df2


# Chargement des données
df = get_data_from_excel1()
df2 = get_data_from_excel2()

# Vérification temporaire des données
st.write("Données principales :", df.head())
st.write("Données des objectifs :", df2.head())



# Fusionner les deux DataFrames
df_merge = df.merge(df2, on="Produits", how="left")  # join des 2 sheets (feuilles) 

# Extraire les villes et produits
villes = sorted(df_merge["Villes"].unique())  # Correction de df_merged à df_merge
produits = sorted(df_merge["Produits"].unique())

# Sidebar pour filtrer les données
st.sidebar.header("Filtrer les données ici :")
produit = st.sidebar.multiselect(
    "Choisissez le produit :",
    options=produits,
    default=produits
)

ville = st.sidebar.multiselect(
    "Choisissez la ville :",
    options=villes,
    default=villes
)

# Sélection des données selon les filtres
#df_selection = df_merge.query(
    #"Villes == @ville & Produits == @produit"  # Correction pour respecter la casse
#)

df_selection = df_merge[
    df_merge["Villes"].isin(ville)
    & df_merge["Produits"].isin(produit)
]


# Vérifions si le DataFrame est vide
if df_selection.empty:
    st.warning("Aucune donnée disponible sur la base des paramètres de filtre actuels !")
    st.stop()

# Titre du dashboard
st.title(":bar_chart: Sales Dashboard")
st.markdown("##")


# KPIs 
chiffre_daffaire_total = int(df_selection["Chiffre_d'affaires"].sum())
cout_total_de_production = int(df_selection["Cout_total"].sum())
marge_brute = chiffre_daffaire_total - cout_total_de_production 

left_column, middle_column, right_column = st.columns(3) 
with left_column:
    st.subheader("Chiffre d'affaires:")
    st.subheader(f"EURO € {chiffre_daffaire_total:,}")

with middle_column:
    st.subheader("Coût production:")
    st.subheader(f"EURO € {cout_total_de_production}")

with right_column:
    st.subheader("Marge brute:")
    st.subheader(f"EURO € {marge_brute}")
    
st.markdown("""___""") 

# CHARTS 

Quantité_vendue_par_produit = df_selection.groupby(by=["Produits"])[["Quantité_vendue"]].sum().sort_values(by="Quantité_vendue")
fig_quantité_vendue_par_produit = px.bar(
    Quantité_vendue_par_produit,
    x="Quantité_vendue",
    y= Quantité_vendue_par_produit.index,
    orientation ="h",
    title="<b>Quantité vendue par produit</b>",
    color_discrete_sequence =["#0083B8"] * len(Quantité_vendue_par_produit),
    template ="plotly_white",
)

fig_quantité_vendue_par_produit.update_layout(
    plot_bgcolor ="rgba(0,0,0,0)",
    xaxis= (dict(showgrid=False))
)

fig_comparaison_CA =px.bar(
    df_selection,
    x= "Produits",
    y= ["CA produits", "CA objectifs"],
    barmode="group",
    labels={"value": "Chiffre d'Affaires", "variable": "Type"},
    title="<b>CA produits vs CA objectifs</b>",
)

fig_comparaison_CA.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor ="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)
    
    
fig3_pourcentage_produit =px.bar(
    df_selection,
    x= "Produits",
    y="% actuel",
    title="<b>Objectifs atteints par produit</b>",
    labels ={"% actuel": "%Objectifs atteints"}
)
fig3_pourcentage_produit.update_layout(
    xaxis= dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis= (dict(showgrid =False)),
)

revenu_brut_par_produit = df_selection.groupby(by=["Produits"])[["Revenu_brut_pa_produit"]].sum() 
fig_col_revenu_brut = px.bar(
    revenu_brut_par_produit.reset_index(),  # Réinitialisation de l'index pour accéder à la colonne 'Produits'
    x="Produits",                           # Utilisez la colonne 'Produits' pour l'axe X
    y="Revenu_brut_pa_produit",             # Axe Y
    title="<b>Revenu brut par produit</b>",
    color_discrete_sequence=["#0083B8"] * len(revenu_brut_par_produit),  # Correction de l'erreur de frappe
    template="plotly_dark"
)

fig_col_revenu_brut.update_xaxes(title="Produits")
fig_col_revenu_brut.update_yaxes(title="Revenu brut")
fig_col_revenu_brut.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid =False)),
)
    
left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_comparaison_CA, use_container_width=True)
right_column.plotly_chart(fig3_pourcentage_produit, use_container_width=True)


left_column2,right_column2 = st.columns(2)
left_column2.plotly_chart(fig_quantité_vendue_par_produit, use_container_width=True)
right_column2.plotly_chart(fig_col_revenu_brut, use_container_width=True) 

    
    
# Cartes

st.header("CA par ville")

#Calcul du  chiffre d'affaires total par ville 

#CA_par_ville = df_selection.groupby(by=["Villes"])[["Chiffre_d'affaires"]].sum().reset_index() 


# Calcul du chiffre d'affaires par ville
CA_par_ville = (
    df_selection.groupby("Villes", as_index=False)
    .agg({
        "Chiffre_d'affaires": "sum",
        "Latitude_Ville": "first",
        "Longitude_Ville": "first"
    })
)

CENTER = (46, 2.18883335)

carte = folium.Map(
    location=CENTER,
    zoom_start=6
)

# Ajouter les marqueurs
for _, row in CA_par_ville.iterrows():
    folium.Marker(
        location=[
            row["Latitude_Ville"],
            row["Longitude_Ville"]
        ],
        popup=f'{row["Villes"]} : {row["Chiffre_d'affaires"]:,.0f} €',
        tooltip=f'Chiffre d’affaires : {row["Villes"]}'
    ).add_to(carte)

st_folium(carte, width=725)


#Recupérer latitude, longitude, villes, CA dans une liste 
list = list(zip(df_selection["Latitude_Ville"], df_selection["Longitude_Ville"], df_selection["Villes"]))

CENTER = (46, 2.18883335) # lat, long de la france 
map = folium.Map(location=CENTER, zoom_start =6)

#Markers 

for(lat, lng, ville), ca in zip(list, CA_par_ville["Chiffre_d'affaires"]):
    folium.Marker(
        [lat, lng],
        popup=f"{ville}: {ca}€",
        tooltip="CHIFFRE D'AFFAIRES"
    ).add_to(map)
    
    
    
st_folium(map, width =725) # afficher la carte

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """ 
st.markdown(hide_st_style, unsafe_allow_html= True) 

# pour lancer l'appli en local executer dans le terminale le code suivant : python -m streamlit run streamlit_app.py

