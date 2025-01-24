import gurobipy as gp
from gurobipy import GRB
import streamlit as st
import numpy as np

def input_data():
    # Interface Streamlit pour obtenir les entrées de l'utilisateur
    row = st.number_input("Enter number of origins", min_value=1, step=1)
    col = st.number_input("Enter number of destinations", min_value=1, step=1)
    
    cost_matrix = []
    for i in range(row):
        row_data = []
        for j in range(col):
            cost = st.number_input(f"Enter cost for ORIGIN {i+1} to DESTINATION {j+1}", min_value=0, step=1, key=f"cost_{i}_{j}")
            row_data.append(cost)
        cost_matrix.append(row_data)
    
    supply = []
    for i in range(row):
        s = st.number_input(f"Enter supply for ORIGIN {i+1}", min_value=0, step=1, key=f"supply_{i}")
        supply.append(s)
    
    demand = []
    for j in range(col):
        d = st.number_input(f"Enter demand for DESTINATION {j+1}", min_value=0, step=1, key=f"demand_{j}")
        demand.append(d)
    
    return np.array(cost_matrix), supply, demand

def transportation_optimization(cost_matrix, supply, demand):
    # Création du modèle Gurobi
    model = gp.Model("Transportation_Problem")
    
    row, col = cost_matrix.shape
    
    # Déclaration des variables de décision (quantité transportée entre chaque origine et chaque destination)
    x = model.addVars(row, col, vtype=GRB.CONTINUOUS, name="x")
    
    # Fonction objectif : minimisation du coût total
    model.setObjective(gp.quicksum(cost_matrix[i][j] * x[i, j] for i in range(row) for j in range(col)), GRB.MINIMIZE)
    
    # Contraintes de capacité (supply)
    for i in range(row):
        model.addConstr(gp.quicksum(x[i, j] for j in range(col)) <= supply[i], f"Supply_{i}")
    
    # Contraintes de demande (demand)
    for j in range(col):
        model.addConstr(gp.quicksum(x[i, j] for i in range(row)) >= demand[j], f"Demand_{j}")
    
    # Optimisation
    model.optimize()
    
    # Récupérer la solution
    if model.status == GRB.OPTIMAL:
        total_cost = model.objVal
        solution = np.zeros_like(cost_matrix)
        for i in range(row):
            for j in range(col):
                solution[i][j] = x[i, j].x
        return total_cost, solution
    else:
        return None, None

def display_solution(total_cost, solution):
    # Affichage des résultats dans Streamlit
    if total_cost is not None:
        st.write(f"Total minimum cost: {total_cost}")
        st.write("Optimal transport quantities:")
        st.table(solution)
    else:
        st.write("No optimal solution found")

def main():
    # Interface Streamlit
    st.title("Transportation Problem Optimization")

    # Entrée des données
    cost_matrix, supply, demand = input_data()
    
    # Résolution du problème de transport avec Gurobi
    total_cost, solution = transportation_optimization(cost_matrix, supply, demand)
    
    # Affichage des résultats
    display_solution(total_cost, solution)

if __name__ == "__main__":
    main()
