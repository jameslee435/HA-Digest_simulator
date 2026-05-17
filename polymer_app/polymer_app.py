import random
import pandas as pd
import streamlit as st

# --- Core Simulation Logic ---


def generate_polymer_chain(length, modification_percentage):
    """Generate a polymer chain with specified modification percentage."""
    return [
        "B" if random.random() < modification_percentage / 100 else "A"
        for _ in range(length)
    ]


def degrade_polymer(polymer_chain):
    """Simulate polymer degradation based on cleavage rules."""
    degradation_products = []
    current_product = []

    for i in range(len(polymer_chain)):
        current_product.append(polymer_chain[i])

        # Check if cleavage should occur after this unit
        if i < len(polymer_chain) - 1:
            next_unit = polymer_chain[i + 1]
            # Cleave after A if followed by A or B if followed by A
            if (current_product[-1] == "A" and next_unit == "A") or (
                current_product[-1] == "B" and next_unit == "A"
            ):
                degradation_products.append("".join(current_product))
                current_product = []

    # Add any remaining units
    if current_product:
        degradation_products.append("".join(current_product))

    return degradation_products


def simulate_degradation(
    modification_percentage, chain_length=100, num_simulations=1000
):
    """Run simulations and calculate statistical distribution."""
    product_counter = {}

    for _ in range(num_simulations):
        chain = generate_polymer_chain(chain_length, modification_percentage)
        products = degrade_polymer(chain)

        for product in products:
            length = len(product)
            product_counter[length] = product_counter.get(length, 0) + 1

    # Convert counts to percentages and filter
    total = sum(product_counter.values())
    if total == 0:
        return {}

    return {
        length: (count / total) * 100
        for length, count in product_counter.items()
        if (count / total) * 100 > 0.25
    }


# --- Streamlit Web Interface ---

# Page config
st.set_page_config(page_title="Polymer Degradation Simulator", layout="wide")

st.title("🧪 Biopolymer Degradation Simulator")
st.write(
    "Simulate the statistical distribution of fragments following a controlled random cleavage pattern."
)

st.markdown("---")

# Sidebar Configuration Layout
st.sidebar.header("Simulation Parameters")

mod_percent = st.sidebar.slider(
    "Degree of Modification (DOM %)",
    min_value=0.0,
    max_value=100.0,
    value=30.0,
    step=0.5,
    help="Percentage of 'B' units in the generated chain.",
)

chain_length = st.sidebar.number_input(
    "Polymer Chain Length",
    min_value=10,
    max_value=5000,
    value=100,
    step=10,
    help="Number of monomer units per single chain.",
)

num_simulations = st.sidebar.number_input(
    "Number of Simulations",
    min_value=100,
    max_value=50000,
    value=5000,
    step=500,
    help="Total iterations to compile reliable statistical data.",
)

# Run button
if st.sidebar.button("Run Simulation", type="primary"):

    # Run the background calculation
    with st.spinner("Simulating cleavage patterns..."):
        distribution = simulate_degradation(
            modification_percentage=mod_percent,
            chain_length=chain_length,
            num_simulations=num_simulations,
        )

    if distribution:
        # Format data into a Pandas DataFrame for easy displaying/charting
        df = pd.DataFrame(
            list(distribution.items()), columns=["Fragment Length", "Occurrence (%)"]
        )
        df = df.sort_values(by="Fragment Length").reset_index(drop=True)

        # Create two side-by-side columns for results
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("📋 Distribution Data")
            # Display an interactive, clean table
            st.dataframe(
                df.style.format({"Occurrence (%)": "{:.2f}%"}),
                hide_index=True,
                use_container_width=True,
            )

        with col2:
            st.subheader("📊 Fragment Profile Visualization")
            # Display an interactive bar chart of the length vs occurrence
            st.bar_chart(df.set_index("Fragment Length"), y="Occurrence (%)")

    else:
        st.error("No fragments generated. Check your simulation parameters.")

else:
    st.info(
        "👈 Adjust the simulation parameters in the sidebar and click **Run Simulation** to view results."
    )