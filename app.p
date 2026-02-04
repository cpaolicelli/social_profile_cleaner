import streamlit as st
import requests

# Mapping customers to their specific IDs
CLIENT_MAPPING = {
    "icc": "63125d7e96571fcbbdb75fe7",
    "mancity": "63125d7e96571fcbbdb75fe8"
}

st.set_page_config(page_title="Social Profile Scanner", page_icon="🔍")

st.title("🔍 Social Profile Scanner")
st.markdown("Enter the details below to trigger a profile scan.")

# --- UI Layout ---
with st.container():
    # Social Handle Input
    username = st.text_input("Social Handle", placeholder="e.g. janesmith123")

    # Platform Dropdown (Default: Instagram)
    platforms = ["instagram", "tiktok"]
    platform = st.selectbox("Select Platform", options=platforms, index=0)

    # Customer Dropdown (Default: ICC)
    customers = list(CLIENT_MAPPING.keys())
    selected_customer = st.selectbox(
        "Select Customer", 
        options=customers, 
        index=customers.index("icc")
    )

# --- Logic ---
if st.button("Run Scan", type="primary"):
    if not username:
        st.warning("Please enter a username before scanning.")
    else:
        # Prepare API Details
        url = "https://social-profile-scanner-prod.gobubble.cc/scan"
        
        # Accessing secrets (Make sure this is set up in .streamlit/secrets.toml)
        try:
            token = st.secrets["BEARER_TOKEN"]
        except KeyError:
            st.error("Missing 'BEARER_TOKEN' in Streamlit secrets.")
            st.stop()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "client_id": CLIENT_MAPPING[selected_customer],
            "client_handle": selected_customer,
            "username": username,
            "platform": platform
        }

        with st.spinner(f"Scanning {username} on {platform}..."):
            try:
                response = requests.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    st.success("Scan Request Successful!")
                    st.json(response.json())
                else:
                    st.error(f"API Error: {response.status_code}")
                    st.write(response.text)
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
