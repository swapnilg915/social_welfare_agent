# frontend/upload_documents.py

import streamlit as st
import requests
import json

st.set_page_config(page_title="Agentic AI - Upload Documents")
st.title("Upload Applicant Documents")

uploaded_files = st.file_uploader(
    "Upload documents (PDF, JPG, PNG, CSV)",
    type=["pdf", "jpg", "jpeg", "png", "csv"],  # ✅ added csv
    accept_multiple_files=True
)

if st.button("Upload Documents"):
    if uploaded_files:
        with st.spinner("Uploading..."):
            files = [("documents", (f.name, f.getvalue())) for f in uploaded_files]
            response = requests.post("http://localhost:5000/upload_documents", files=files)
            if response.status_code == 200:
                st.success("Documents uploaded successfully.")
            else:
                st.error(f"Upload failed: {response.text}")
    else:
        st.warning("Please upload at least one document.")

if st.button("Analyze with Agentic AI"):
    with st.spinner("Running pipeline..."):
        response = requests.post("http://localhost:5000/run_pipeline")
        if response.status_code == 200:
            try:
                outer = response.json()
                if outer.get("success"):
                    result_str = outer.get("result", "{}")

                    # result_data = eval(result_str)  # TEMP fix; replace with json.loads later

                    import json
                    if isinstance(result_str, str):
                        result_data = json.loads(result_str)
                    else:
                        result_data = result_str

                    st.success("Analysis completed.")

                    case_id = result_data.get("case_id")
                    st.markdown(f"**Case ID:** `{case_id}`")

                    st.subheader("Applicant Profile")
                    profile = result_data.get("applicant_profile", {})
                    if isinstance(profile, dict):
                        st.json(profile)
                    else:
                        st.error(f"Invalid profile: {profile}")

                    st.subheader("LLM Decision")
                    decision = result_data.get("llm_decision", {})
                    if isinstance(decision, dict):
                        st.json(decision)
                    else:
                        st.error(f"Invalid decision: {decision}")

                    # st.subheader("Download Uploaded Files")
                    # if isinstance(uploaded_files, list):
                    #     for file in uploaded_files:
                    #         filename = file.name
                    #         file_url = f"http://localhost:5000/case/{case_id}/file/{filename}"
                    #         st.markdown(f"[{filename}]({file_url})")
                else:
                    st.error(f"Pipeline error: {outer.get('error')}")
            except Exception as e:
                st.error(f"Failed to parse result: {str(e)}")
        else:
            st.error(f"Pipeline call failed: {response.text}")
