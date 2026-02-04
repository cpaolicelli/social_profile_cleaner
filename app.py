import streamlit as st
import requests
import random

# Mapping customers to their specific IDs
CLIENT_MAPPING = {
    "icc": "63125d7e96571fcbbdb75fe7",
    "mancity": "63125d7e96571fcbbdb75fe8"
}

# List of "Loading" GIFs
WAITING_GIFS = [
    "https://media.tenor.com/bqxGG15mB_0AAAAC/loading.gif",
    "https://media.tenor.com/btpjr9_Gg30AAAAC/loading-load.gif",
    "https://media.tenor.com/bB0gx1Ie_68AAAAC/loading.gif",
    "https://media.tenor.com/bh9U0I2v108AAAAC/loading.gif",
    "https://media.tenor.com/bzLgyp6m44wAAAAC/loading.gif",
    "https://media.tenor.com/bE1DG1p1_o8AAAAC/loading.gif",
    "https://media.tenor.com/bBKvM1p1_o8AAAAC/loading.gif"
]

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

# Placeholder for results or loading state
main_container = st.empty()

# --- API Logic ---
if run_scan:
    if not username:
        st.warning("Please enter a username.")
    else:
        # 1. Show a random loading GIF
        with main_container.container():
            st.markdown("### Sto analizzando... porta pazienza...")
            st.image(random.choice(WAITING_GIFS), width=300)
        
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

        try:
            response = requests.post(url, json=payload, headers=headers)
            
            # 2. Replace loading GIF with actual results
            if response.status_code == 200:
                data = response.json()
                profile = data.get("profile_info", {})
                visual = data.get("visual_analysis", {})
                risk_level = visual.get("final_risk_level", "Low").capitalize()
                
                with main_container.container():
                    st.markdown("---")
                    st.subheader("È questa la zinnona che volevi bloccare?")
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        pic_url = profile.get("profile_pic_url")
                        if pic_url:
                            st.image(pic_url, use_container_width=True)
                        st.markdown(f"**Username:** `@{profile.get('username')}`")

                    with col2:
                        if risk_level == "High":
                            st.error(f"**Risk Level: {risk_level}**")
                            st.write("### Hai beccato na zinnona molestatrice di social")
                            st.image("https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExOTNmcDBhY3pieGI5bjVmcHE1NnlzYWo3ejllbWdndWp4dHZ2MGpoZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/PfFbqwqk99lic5FQZT/giphy.gif", width=250)
                        
                        elif risk_level == "Medium":
                            st.warning(f"**Risk Level: {risk_level}**")
                            st.write("### Mmmmm verifica il profilo su instagram, questa me puzza ma non sono sicuro")
                            st.image("https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExeDFoODB4c251Ymw2ZTQ2cWRnazlvbGxsMGxjMWQ1bmU3eHA2ZDM2dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ZX3iRfERJYfOVKEzTb/giphy.gif", width=250)
                        
                        else:
                            st.success(f"**Risk Level: {risk_level}**")
                            st.write("### Hai mandato una persona potenzialmente innocente al patibolo, fatti un esame di coscienza")
                            st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExODk3ajJ1eXYwcWtodHozcmI4amlwYnR6MHRndWttd2hzcDk2cDU2ciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QDjeYvnJb1IXyy2xSn/giphy.gif", width=250)

                        st.markdown("---")
                        st.markdown("**Key Red Flags:**")
                        flags = visual.get("key_red_flags", [])
                        for flag in flags:
                            st.markdown(f"🚩 {flag}")

                    with st.expander("View Full Report Details"):
                        st.json(data)
            else:
                main_container.error(f"API Error: {response.status_code}")
                st.write(response.text)
        
        except Exception as e:
            main_container.error(f"An error occurred: {e}")
else:
    main_container.info("Fill in the handle on the left and click 'Run Scan' to begin.")
