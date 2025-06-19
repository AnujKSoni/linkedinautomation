import streamlit as st
import requests

st.set_page_config(page_title="LinkedAutomator", layout="centered")
st.title("🔗 LinkedAutomator")

# Sidebar for input
st.sidebar.header("Settings")
company = st.sidebar.selectbox("Select Company", ["Apple", "NVIDIA", "AMD", "ARM", "Broadcom", "Qualcomm"])
count = st.sidebar.slider("Connection Requests", 1, 20, 5)

st.sidebar.markdown("---")
message = st.sidebar.text_area("Custom Message Template", 
    "Hi {first_name}, I came across your profile while exploring {company}. I'd love to connect and learn more about your work on {company}." )

if st.button("🚀 Send Requests"):
    st.info(f"Sending {count} requests to {company}...")
    # Personalize message (example for demonstration)
    final_message = message.format(first_name="<NAME>", company=company)
    payload = {
        "company": company,
        "count": count,
        "message": final_message
    }
    try:
        response = requests.post("https://linkedinautomation-3oyq.onrender.com/api/connect", json=payload)
        result = response.json()
        if response.status_code == 200:
            st.success(f"Sent {result.get('requests_sent')} requests!")
            if result.get('failures'):
                st.error("Some failures occurred:")
                st.write(result.get('failures'))
        else:
            st.error(f"Error: {result.get('error')}")
    except Exception as e:
        st.error(f"API Request failed: {e}")

st.markdown("---")
st.write("Built with ❤️ by Anuj Kumar Soni")
