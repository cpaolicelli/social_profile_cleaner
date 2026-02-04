import streamlit as st
import requests

# Mapping customers to their specific IDs
CLIENT_MAPPING = {
    "icc": "63125d7e96571fcbbdb75fe7",
    "mancity": "63125d7e96571fcbbdb75fe8"
}

st.set_page_config(page_title="Social Profile Scanner", page_icon="🔍", layout="centered")

st.title("🔍 Social Profile Scanner")

# --- UI Layout ---
with st.sidebar:
    st.header("Configuration")
    username = st.text_input("Social Handle", placeholder="e.g. janesmith123")
    
    platforms = ["instagram", "twitter", "facebook", "tiktok"]
    platform = st.selectbox("Select Platform", options=platforms, index=0)

    customers = list(CLIENT_MAPPING.keys())
    selected_customer = st.selectbox(
        "Select Customer", 
        options=customers, 
        index=customers.index("icc")
    )
    
    run_scan = st.button("Run Scan", type="primary", use_container_width=True)

# --- API Logic & Results View ---
if run_scan:
    if not username:
        st.warning("Please enter a username.")
    else:
        # Accessing secrets
        try:
            token = st.secrets["BEARER_TOKEN"]
        except KeyError:
            st.error("Missing 'BEARER_TOKEN' in Streamlit secrets.")
            st.stop()

        url = "https://social-profile-scanner-prod.gobubble.cc/scan"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "client_id": CLIENT_MAPPING[selected_customer],
            "client_handle": selected_customer,
            "username": username,
            "platform": platform
        }

        with st.spinner("Analyzing profile..."):
            try:
                response = requests.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # --- NEW USER FRIENDLY VIEW ---
                    st.markdown("---")
                    st.subheader("È questa la zinnona che volevi bloccare?")
                    
                    col1, col2 = st.columns([1, 2])
                    
                    # Profile Info from JSON
                    profile = data.get("profile_info", {})
                    visual = data.get("visual_analysis", {})
                    
                    with col1:
                        # Show profile pic
                        pic_url = profile.get("profile_pic_url")
                        if pic_url:
                            st.image(pic_url, use_container_width=True, caption=f"@{profile.get('username')}")
                        else:
                            st.info("No profile picture available")

                    with col2:
                        st.markdown(f"**Username:** `{profile.get('username')}`")
                        
                        # Risk Level Color Coding
                        risk_level = visual.get("final_risk_level", "Unknown")
                        risk_color = "red" if risk_level.lower() == "high" else "orange" if risk_level.lower() == "medium" else "green"
                        st.markdown(f"**Final Risk Level:** :{risk_color}[{risk_level}]")
                        
                        # Key Red Flags
                        st.markdown("**Key Red Flags:**")
                        flags = visual.get("key_red_flags", [])
                        if flags:
                            for flag in flags:
                                st.markdown(f"- {flag}")
                        else:
                            st.write("No specific red flags identified.")

                    # Optional: Expandable raw response for debugging
                    with st.expander("View Raw API Response"):
                        st.json(data)
                        
                else:
                    st.error(f"API Error: {response.status_code}")
                    st.write(response.text)
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.info("Fill in the handle on the left and click 'Run Scan' to begin.")
