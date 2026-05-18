import streamlit as st
import random
import pandas as pd

def generate_polymer_chain(length, modification_percentage):
    """Generate a polymer chain with specified modification percentage."""
    return ['B' if random.random() < modification_percentage / 100 else 'A' 
            for _ in range(length)]

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
            if (current_product[-1] == 'A' and next_unit == 'A') or \
               (current_product[-1] == 'B' and next_unit == 'A'):
                degradation_products.append(''.join(current_product))
                current_product = []
    
    # Add any remaining units
    if current_product:
        degradation_products.append(''.join(current_product))
        
    return degradation_products

def simulate_degradation(modification_percentage, chain_length=100, num_simulations=1000):
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
        
    return {length: (count/total)*100 
            for length, count in product_counter.items() 
            if (count/total)*100 > 0.10}

# --- STREAMLIT USER INTERFACE ---
st.title("HA Digestion Simulator (Version 2)")
st.write("Simulate biopolymer degradation distributions based on the Degree of Modification (DOM%).")

# Initialize session state for DOM if it doesn't exist
if 'dom_value' not in st.session_state:
    st.session_state.dom_value = 10.00

# Callback functions to sync the slider and the input box
def update_slider():
    st.session_state.dom_value = st.session_state.numeric_input

def update_numeric():
    st.session_state.dom_value = st.session_state.slider_input

# Two-column layout for side-by-side inputs
col1, col2 = st.columns([3, 1])

with col1:
    mod_percent_slider = st.slider(
        "Select DOM%", 
        min_value=0.00, 
        max_value=100.00, 
        step=0.01,
        key="slider_input",
        value=st.session_state.dom_value,
        on_change=update_numeric
    )

with col2:
    mod_percent_numeric = st.number_input(
        "Manually Input DOM%", 
        min_value=0.00, 
        max_value=100.00, 
        step=0.01,
        format="%.2f",
        key="numeric_input",
        value=st.session_state.dom_value,
        on_change=update_slider
    )

# Current active DOM value to use in simulation
active_dom = st.session_state.dom_value

# Optional Simulation Parameters
with st.expander("Advanced Simulation Settings"):
    c_length = st.number_input("Chain Length", min_value=10, max_value=1000, value=100, step=10)
    n_sims = st.number_input("Number of Simulations", min_value=100, max_value=10000, value=1000, step=100)

if st.button("Run Degradation Simulation", type="primary"):
    with st.spinner("Calculating fragment distributions..."):
        distribution = simulate_degradation(active_dom, chain_length=c_length, num_simulations=n_sims)
        
    st.subheader(f"Degradation Product Distribution ({active_dom:.2f}% modification)")
    
    if distribution:
        # Format data for display
        df = pd.DataFrame([
            {"Length": length, "Occurrence (%)": round(pct, 2)}
            for length, pct in sorted(distribution.items())
        ])
        
        # Display as an interactive data table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Display as a clean bar chart
        st.bar_chart(df.set_index("Length"))
    else:
        st.warning("No degradation products detected above the 0.10% threshold.")
