import streamlit as st
from gurobipy import Model, GRB

# Titre de l'application
st.title("Optimisation du Problème de Mélange")

# Entrée des données principales
st.header("Paramètres Généraux")

nombre_de_ressources = st.number_input("Nombre de ressources", min_value=1, step=1, value=3)
quantite_totale = st.number_input("Quantité totale de produit final", min_value=0.0, step=1.0, value=100.0)
caracteristique_principale_minimale = st.number_input("Contribution minimale de la caractéristique principale (%)", min_value=0.0, max_value=100.0, step=1.0, value=30.0)

# Initialisation des données des ressources
st.header("Paramètres des Ressources")

noms = []
couts = {}
stocks = {}
contributions = {}
unites = {}

# Saisie dynamique des paramètres de chaque ressource
for i in range(nombre_de_ressources):
    st.subheader(f"Ressource {i + 1}")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        nom = st.text_input(f"Nom de la ressource {i + 1}", value=f"Ressource_{i + 1}")
    with col2:
        cout = st.number_input(f"Coût de la ressource {i + 1}", min_value=0.0, step=0.1, value=10.0)
    with col3:
        stock = st.number_input(f"Stock disponible {i + 1}", min_value=0.0, step=1.0, value=50.0)
    with col4:
        contribution = st.number_input(f"Contribution (%) {i + 1}", min_value=0.0, max_value=100.0, step=1.0, value=20.0)
    with col5:
        unite = st.selectbox(f"Unité {i + 1}", ["kg", "litre", "tonne", "unité"], index=0)

    noms.append(nom)
    couts[nom] = cout
    stocks[nom] = stock
    contributions[nom] = contribution
    unites[nom] = unite

# Bouton pour lancer l'optimisation
if st.button("Optimiser"):
    try:
        # Calcul de la contribution minimale requise
        contribution_min_absolue = caracteristique_principale_minimale / 100 * quantite_totale

        # Création du modèle Gurobi
        model = Model("Probleme_de_Melange")

        # Variables de décision
        quantites_var = model.addVars(noms, name="x", lb=0)

        # Fonction objectif : minimiser le coût total
        model.setObjective(
            sum(couts[nom] * quantites_var[nom] for nom in noms),
            GRB.MINIMIZE
        )

        # Contraintes
        # 1. Quantité totale
        model.addConstr(
            sum(quantites_var[nom] for nom in noms) == quantite_totale,
            "quantiteTotale"
        )

        # 2. Contribution minimale
        model.addConstr(
            sum(contributions[nom] * quantites_var[nom] for nom in noms) >= contribution_min_absolue,
            "contributionMin"
        )

        # 3. Stock maximum
        for nom in noms:
            model.addConstr(
                quantites_var[nom] <= stocks[nom],
                f"stock_max_{nom}"
            )

        # Résolution du modèle
        model.optimize()

        # Affichage des résultats
        if model.status == GRB.OPTIMAL:
            st.success("Solution optimale trouvée !")
            st.write(f"Coût total minimisé : **{model.objVal}**")
            st.write("Quantités allouées :")
            for nom in noms:
                st.write(f"- {nom} : {quantites_var[nom].x:.2f} {unites[nom]}")
        else:
            st.error("Aucune solution optimale trouvée.")

    except Exception as e:
        st.error(f"Erreur : {str(e)}")
