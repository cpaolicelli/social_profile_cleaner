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
    st.header("Scan Profile")
    username = st.text_input("Social Handle", placeholder="e.g. janesmith123")
    
    platforms = ["instagram", "twitter", "tiktok"]
    platform = st.selectbox("Select Platform", options=platforms, index=0)

    customers = list(CLIENT_MAPPING.keys())
    selected_customer = st.selectbox(
        "Select Customer", 
        options=customers, 
        index=customers.index("icc")
    )
    
    run_scan = st.button("Run Scan", type="primary", use_container_width=True)

    st.markdown("---")
    st.header("Remoderation")
    st.subheader("Usa questa funzione solo per rimoderare i messaggi")
    remod_username = st.text_input("User to Remoderate", placeholder="e.g. offensive_user")
    if st.button("Moderate", type="primary", use_container_width=True):
        if not remod_username:
            st.warning("Please enter a username to moderate.")
        else:
            try:
                # Ensure token is available (it's checked later for scan, but needed here too)
                token = st.secrets["BEARER_TOKEN"]
                # Change to GET call with path parameters
                remod_url = f"https://social-profile-scanner-prod.gobubble.cc/moderate/{platform}/{remod_username}"
                remod_headers = {"Authorization": f"Bearer {token}"}
                
                with st.spinner("Moderating..."):
                    remod_response = requests.get(remod_url, headers=remod_headers)
                
                if remod_response.status_code == 200:
                    st.success(f"Moderation triggered for {remod_username}")
                else:
                    st.error(f"Failed: {remod_response.status_code} - {remod_response.text}")
            except KeyError:
                st.error("Missing 'BEARER_TOKEN' in Streamlit secrets.")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.header("Hard Block")
    st.subheader("Blocca manualmente un utente")
    block_username = st.text_input("User to Block", placeholder="e.g. bad_user")
    
    # Use a different variable name and label/key to avoid conflict with the top selector
    block_platform = st.selectbox("Select Platform", options=platforms, key="block_platform_selector")
    
    if st.button("Hard Block", type="primary", use_container_width=True):
        if not block_username:
            st.warning("Please enter a username to block.")
        else:
            try:
                token = st.secrets["BEARER_TOKEN"]
                block_url = "https://social-profile-scanner-prod.gobubble.cc/block"
                block_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                block_payload = {
                     "username": block_username,
                     "platform": block_platform
                }
                
                with st.spinner("Blocking user..."):
                     block_response = requests.post(block_url, json=block_payload, headers=block_headers)
                
                if block_response.status_code == 200:
                     st.success(f"User {block_username} blocked successfully!")
                else:
                     st.error(f"Block failed: {block_response.status_code} - {block_response.text}")

            except KeyError:
                st.error("Missing 'BEARER_TOKEN' in Streamlit secrets.")
            except Exception as e:
                st.error(f"Error: {e}")

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
                profile = data.get("profile_info") or {}
                visual = data.get("visual_analysis") or {}
                risk_level = visual.get("final_risk_level", "Low").capitalize()
                full_name = profile.get("full_name")

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
                        elif risk_level == "Low" and full_name == "Blacklisted User":
                            st.success(f"**Zinnona già bloccata**")
                            st.write("### Manco Stanis lavora così, questa l'avete già bloccata, passa avanti")
                            st.image("https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExc2l5dWk5YmV1d2V2eW1hY3lobTY3NGVmdGFhaTN0enp4dDNrbG42YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Rh6aICkkBFhZ06seXL/giphy.gif", width=250)
                        else:
                            st.warning(f"**Risk Level: {risk_level}**")
                            st.write("### Hai mandato una persona potenzialmente innocente al patibolo, fatti un esame di coscienza")
                            st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExODk3ajJ1eXYwcWtodHozcmI4amlwYnR6MHRndWttd2hzcDk2cDU2ciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QDjeYvnJb1IXyy2xSn/giphy.gif", width=250)
                            
                            st.markdown("### Decision Override")
                            if st.button("Force User Block", type="primary"):
                                try:
                                    block_url = "https://social-profile-scanner-prod.gobubble.cc/block"
                                    # Reuse headers with token from earlier
                                    block_payload = {
                                        "username": username,
                                        "platform": platform
                                    }
                                    with st.spinner("Blocking user..."):
                                        block_response = requests.post(block_url, json=block_payload, headers=headers)
                                    
                                    if block_response.status_code == 200:
                                        st.success(f"User {username} blocked successfully!")
                                    else:
                                        st.error(f"Block failed: {block_response.status_code} - {block_response.text}")
                                except Exception as e:
                                    st.error(f"Error blocking user: {e}")

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
