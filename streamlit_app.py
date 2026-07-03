import streamlit as st
import json
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import run_agent

# Page configuration
st.set_page_config(
    page_title="Suproc Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("🤖 Suproc Agent")
st.markdown("Local Suproc-style agentic search, matching, and verification system")

# Sidebar
with st.sidebar:
    st.header("About")
    st.info(
        "This agent interprets business requirements and finds matching records "
        "from the dataset with intelligent ranking and validation."
    )
    st.markdown("---")
    st.markdown("**Version:** 0.1.0")

# Main content area
st.markdown("### Enter Your Request")

# Input section
col1, col2 = st.columns([4, 1])
with col1:
    user_query = st.text_input(
        "What are you looking for?",
        placeholder="e.g., find me a good project to work on",
        label_visibility="collapsed"
    )

with col2:
    search_button = st.button("🔍 Search", type="primary", use_container_width=True)

# Process query
if search_button and user_query:
    with st.spinner("Processing your request..."):
        try:
            response = run_agent(user_query)
            
            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["Results", "Details", "Raw JSON"])
            
            with tab1:
                st.markdown("### Recommended Matches")
                if response.recommended_matches:
                    for i, match in enumerate(response.recommended_matches, 1):
                        with st.expander(f"{i}. {match.name} (Score: {match.score.total}/100)", expanded=i==1):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Entity ID:** {match.entity_id}")
                                st.markdown(f"**Type:** {match.entity_type}")
                                st.markdown(f"**Score:** {match.score.total}/100")
                            with col2:
                                st.markdown("**Evidence:**")
                                for evidence in match.evidence:
                                    st.markdown(f"- {evidence}")
                            
                            if match.missing_information:
                                st.warning("**Missing Information:**")
                                for info in match.missing_information:
                                    st.markdown(f"- {info}")
                
                # Summary
                st.markdown("---")
                st.markdown("### Summary")
                st.info(f"**Recommended Action:** {response.recommended_next_action}")
            
            with tab2:
                st.markdown("### Analysis Details")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Interpreted Requirement:**")
                    st.json(response.interpreted_requirement.model_dump())
                
                with col2:
                    st.markdown("**Validation Status:**")
                    st.json(response.validation.model_dump())
                
                st.markdown("**Plan Followed:**")
                for step in response.plan_followed:
                    st.markdown(f"✓ {step}")
            
            with tab3:
                st.markdown("### Full Response JSON")
                st.json(response.model_dump())
        
        except Exception as e:
            st.error(f"Error processing request: {str(e)}")
            st.exception(e)

else:
    st.info("💡 Enter a business requirement above to get started!")
