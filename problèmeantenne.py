import streamlit as st
import pandas as pd
from gurobipy import Model, GRB, quicksum
import plotly.express as px
import json
from streamlit_lottie import st_lottie

# Load Lottie animations
def load_lottie_file(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Solver Function
def solve_coverage_problem(zone_data):
    try:
        zones = [item[1] for item in zone_data]
        sites = [item[0] for item in zone_data]
        antennas_required = [item[2] for item in zone_data]

        model = Model("CoverageProblem")

        # Unique sites
        unique_sites = set(site for sublist in sites for site in sublist)

        # Decision variables
        x = {site: model.addVar(vtype=GRB.BINARY, name=f"x_{site}") for site in unique_sites}

        # Objective: Minimize number of antennas
        model.setObjective(quicksum(x[site] for site in unique_sites), sense=GRB.MINIMIZE)

        # Constraints: Ensure coverage
        for i, zone in enumerate(zones):
            model.addConstr(quicksum(x[site] for site in sites[i]) >= antennas_required[i], f"antenna_constraint_{i}")

        # Solve model
        model.optimize()

        if model.status == GRB.OPTIMAL:
            return [{"Site": site, "Antenna": int(x[site].x)} for site in unique_sites]
        else:
            return None
    except Exception as e:
        st.error(f"An error occurred while solving the problem: {e}")
        return None

# Streamlit App
def main():
    st.set_page_config(page_title="Antenna Placement Optimizer", layout="wide")

    # Load animations
    lottie_antenna = load_lottie_file("antenna.json")  # Replace with your Lottie file path
    lottie_network = load_lottie_file("network.json")  # Replace with your Lottie file path
    lottie_loading = load_lottie_file("loading.json")  # Replace with your Lottie file path

    # Custom CSS for better visuals
    st.markdown(
        """
        <style>
        .stButton button {
            background-color: #1f77b4;
            color: white;
            border-radius: 5px;
            padding: 10px 24px;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }
        .stButton button:hover {
            background-color: #16558f;
        }
        .stTextInput input {
            border-radius: 5px;
            padding: 10px;
            border: 1px solid #1f77b4;
        }
        .stNumberInput input {
            border-radius: 5px;
            padding: 10px;
            border: 1px solid #1f77b4;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #1f77b4;
        }
        .stMarkdown p {
            font-size: 16px;
            line-height: 1.6;
            color: #333;
        }
        .stSidebar {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
        }
        .stDataFrame {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Main title and introduction
    st.title("📡 Antenna Placement Optimization")
    st.markdown(
        """
        <div style="text-align: center;">
            <h2 style="color: #1f77b4;">Optimize Antenna Placement for Maximum Coverage</h2>
            <p style="font-size: 18px; color: #555;">
                This tool helps telecom companies minimize the number of antennas while ensuring optimal coverage across zones.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar for animations
    with st.sidebar:
        st_lottie(lottie_antenna, height=150, key="antenna")
        st.markdown(
            """
            <div style="text-align: center;">
                <h3 style="color: #1f77b4;">Problem Overview</h3>
                <p style="font-size: 14px; color: #555;">
                    Each antenna can cover certain sites, and zones require a minimum number of antennas for full coverage.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Initialize session state
    if "zone_data" not in st.session_state:
        st.session_state.zone_data = []

    if "step" not in st.session_state:
        st.session_state.step = "zone_count"

    if "current_zone" not in st.session_state:
        st.session_state.current_zone = 1

    # Step 1: Input number of zones
    if st.session_state.step == "zone_count":
        st.subheader("Step 1: Define Number of Zones")
        st.markdown("Enter the number of zones you want to optimize. Each zone will require specific sites and antennas.")
        zone_count = st.number_input("Enter the number of zones (Max: 17):", min_value=1, max_value=17, step=1)
        if st.button("Next", key="next_button"):
            if zone_count > 0:
                st.session_state.zone_count = zone_count
                st.session_state.step = "zone_details"
            else:
                st.error("Please enter a valid number of zones.")

    # Step 2: Define zone details
    elif st.session_state.step == "zone_details":
        current_zone = st.session_state.current_zone
        st.subheader(f"Step 2: Define Zone {current_zone}")
        st.markdown(f"Enter the details for Zone {current_zone}.")
        neighboring_sites = st.text_input("Enter neighboring sites (comma-separated, e.g., A,B,C):", key=f"neighboring_sites_{current_zone}")
        antennas_required = st.number_input(
            "Enter number of antennas required:", min_value=1, max_value=10, step=1, key=f"antennas_required_{current_zone}"
        )
        if st.button("Next Zone", key=f"next_zone_button_{current_zone}"):
            neighbors = [site.strip() for site in neighboring_sites.split(",") if site.strip()]
            if neighbors and antennas_required > 0:
                st.session_state.zone_data.append([neighbors, current_zone, antennas_required])
                if st.session_state.current_zone < st.session_state.zone_count:
                    st.session_state.current_zone += 1
                else:
                    st.session_state.step = "solve"
            else:
                st.error("Please enter valid neighboring sites and antennas required.")

    # Step 3: Solve and display results
    elif st.session_state.step == "solve":
        st.subheader("Results")
        with st.spinner("Optimizing antenna placement..."):
            st_lottie(lottie_loading, height=200, key="loading")
            zone_data = st.session_state.zone_data
            st.write("Zone Data:", pd.DataFrame(zone_data, columns=["Neighboring Sites", "Zone", "Antennas Required"]))

            results = solve_coverage_problem(zone_data)

            if results:
                st_lottie(lottie_network, height=200, key="network")
                st.success("Optimal antenna placement found!")
                df_results = pd.DataFrame(results)
                st.table(df_results.style.set_properties(**{'text-align': 'left'}).set_table_styles(
                    [{'selector': 'th', 'props': [('text-align', 'left')]}]
                ))

                # Visualize the results with a network-themed color palette
                fig = px.scatter(
                    df_results,
                    x="Site",
                    y="Antenna",
                    color="Antenna",
                    size="Antenna",
                    title="Antenna Distribution Across Sites",
                    color_continuous_scale=px.colors.sequential.Blues,  # Network-themed color scheme
                )
                st.plotly_chart(fig)

            else:
                st.error("No optimal solution found. Please check your input data and try again.")

        if st.button("Restart", key="restart_button"):
            st.session_state.clear()

if __name__ == "__main__":
    main()