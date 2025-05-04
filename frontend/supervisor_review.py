# frontend/supervisor_review.py

import streamlit as st
import requests

st.set_page_config(page_title="👩‍⚖️ Agentic AI - Supervisor Review")

st.title("👩‍⚖️ Supervisor Review (Agentic AI)")

if st.button("Fetch Latest Applicant Data"):
    with st.spinner("Retrieving last applicant profile..."):
        # We simulate by calling pipeline again to get output
        response = requests.post("http://localhost:5000/run_pipeline")

        if response.status_code == 200:
            result = response.json()

            if result.get("success"):
                data = result.get("result")

                applicant_profile = data.get("applicant_profile")
                ai_decision = data.get("llm_decision")

                st.subheader("📄 Applicant Profile")
                for key, value in applicant_profile.items():
                    if key != "validation_summary":
                        st.markdown(f"**{key.replace('_',' ').title()}**: {value}")

                st.subheader("🧠 AI Decision Recommendation")
                st.markdown(f"**Decision**: {ai_decision.get('decision')}")
                st.markdown(f"**Reason**: {ai_decision.get('reason')}")

                st.subheader("✅ Supervisor Final Action")
                decision = st.radio("Choose your final decision:", ["Approve", "Request Modification", "Reject"])

                comments = ""
                if decision == "Request Modification":
                    comments = st.text_area("Please specify what should be modified or uploaded again:")

                if st.button("Submit Final Decision"):
                    st.success("✅ Supervisor decision recorded")
                    st.markdown(f"**Final Decision**: {decision}")
                    if comments:
                        st.markdown(f"**Comments**: {comments}")
            else:
                st.error(f"❌ Error: {result.get('error')}")
        else:
            st.error(f"❌ Failed to get data: {response.text}")
