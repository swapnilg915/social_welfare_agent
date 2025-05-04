import streamlit as st
import requests
import json

st.set_page_config(page_title="Agentic AI - Case Chatbot")
st.title("📄 Social Support Cases Chatbot")

API_URL = "http://localhost:5000"

# 1. Fetch all cases
def fetch_all_cases():
    try:
        response = requests.get(f"{API_URL}/cases")
        if response.status_code == 200:
            return response.json().get("cases", [])
        else:
            st.error("Failed to load cases")
            return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# 2. Display list of all cases
cases = fetch_all_cases()

if not cases:
    st.warning("No cases available yet. Please upload and run the pipeline.")
    st.stop()

case_titles = [f"{case['case_id']} - {case['applicant_profile'].get('account_name', 'N/A')}" for case in cases]
selected_index = st.selectbox("Select a Case", range(len(cases)), format_func=lambda i: case_titles[i])
selected_case = cases[selected_index]
case_id = selected_case["case_id"]

# 3. Display case details
st.subheader("Applicant Profile")
st.json(selected_case.get("applicant_profile", {}))

st.subheader("LLM Decision")
st.json(selected_case.get("llm_decision", {}))

st.subheader("Submitted Documents")
doc_list = selected_case.get("documents", [])

# for doc in doc_list:
#     fname = doc.get("filename")
#     if fname:
#         url = f"{API_URL}/case/{case_id}/file/{fname}"
#         st.markdown(f"[📄 {fname}]({url})")

st.subheader("📎 Download Uploaded Files")
if doc_list:
    for doc in doc_list:
        fname = doc.get("filename")
        if fname:
            file_url = f"{API_URL}/case/{case_id}/file/{fname}"
            st.markdown(f"🔗 [**{fname}**]({file_url})", unsafe_allow_html=True)
else:
    st.info("No documents found for this case.")

st.markdown("---")
st.subheader("🤖 Ask a Question to the Case Chatbot")
user_query = st.text_input("Type your question here:")

if st.button("Ask") and user_query:
    with st.spinner("Thinking..."):
        try:
            res = requests.post(f"{API_URL}/case/{case_id}/ask", json={"query": user_query})
            if res.status_code == 200:
                answer = res.json().get("answer", "No answer returned")
                st.success(answer)
            else:
                st.error(f"Error: {res.text}")
        except Exception as e:
            st.error(f"Failed to query chatbot: {e}")
