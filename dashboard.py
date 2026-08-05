import streamlit as st
import pandas as pd

from analysis.kpi import calculate_kpis
from analysis.country_analysis import country_analysis
from analysis.operator_analysis import operator_analysis
from analysis.error_analysis import load_error_master

from reports.report_builder import generate_report

from ai.prompt_builder import build_prompt
from ai.ai_engine import generate_summary

from ai.vector_store import VectorStore
from ai.rag_engine import RAGEngine


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Telecom AI Traffic Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Telecom AI Traffic Analyzer")

# ==========================================================
# Upload File
# ==========================================================

uploaded_file = st.file_uploader(
    "Upload Telecom Log",
    type=["csv"]
)

# ==========================================================
# Main Application
# ==========================================================

if uploaded_file is not None:

    # -------------------------------------------------------
    # Load CSV
    # -------------------------------------------------------

    df = pd.read_csv(uploaded_file)

    filtered_df = df.copy()

    # -------------------------------------------------------
    # Filters
    # -------------------------------------------------------

    selected_date = st.selectbox(
        "📅 Select Date",
        ["All"] + sorted(df["date"].unique().tolist())
    )

    if selected_date != "All":

        filtered_df = filtered_df[
            filtered_df["date"] == selected_date
        ]

    selected_country = st.selectbox(
        "🌍 Select Country",
        ["All"] + sorted(df["country"].unique().tolist())
    )

    if selected_country != "All":

        filtered_df = filtered_df[
            filtered_df["country"] == selected_country
        ]

    selected_operator = st.selectbox(
        "📡 Select Operator",
        ["All"] + sorted(df["operator"].unique().tolist())
    )

    if selected_operator != "All":

        filtered_df = filtered_df[
            filtered_df["operator"] == selected_operator
        ]

    # -------------------------------------------------------
    # KPI Calculation
    # -------------------------------------------------------

    overall = calculate_kpis(filtered_df)

    country = country_analysis(filtered_df)

    operator = operator_analysis(filtered_df)

    # =======================================================
    # Overall KPI
    # =======================================================

    st.header("📈 Overall KPI")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Traffic", overall["total"])

    col2.metric("Delivered", overall["delivered"])

    col3.metric("Failed", overall["failed"])

    col4.metric(
        "Delivery %",
        f'{overall["delivered_percentage"]:.2%}'
    )

    st.divider()

    # =======================================================
    # Country Summary
    # =======================================================

    st.header("🌍 Country Summary")

    st.dataframe(
        country["country_summary"],
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🌍 Top Countries")

        st.dataframe(
            country["top_traffic"],
            use_container_width=True
        )

    with col2:

        st.subheader("📊 Country Traffic")

        st.bar_chart(
            country["top_traffic"].set_index("country")[
                "total_traffic"
            ]
        )

    st.divider()

    # =======================================================
    # Operator Summary
    # =======================================================

    st.header("📡 Operator Summary")

    st.dataframe(
        operator["operator_summary"],
        use_container_width=True
    )

    # =======================================================
    # AI Executive Summary
    # =======================================================

    st.divider()

    st.subheader("🤖 AI Executive Summary")

    if st.button("Generate AI Summary"):

        with st.spinner("Generating AI Summary..."):

            try:

                report = generate_report(
                    overall,
                    country,
                    operator
                )

                prompt = build_prompt(report)

                ai_report = generate_summary(prompt)

                st.success(
                    "AI Summary Generated Successfully!"
                )

                st.markdown(ai_report)

            except Exception as e:

                st.error(
                    f"AI generation failed : {e}"
                )

    # =======================================================
    # Telecom Operations Copilot
    # =======================================================

    st.divider()

    st.subheader("🧠 Telecom Operations Copilot")

    st.write(
        "Search telecom SOPs or generate an AI explanation."
    )

    st.info("""
Try these questions:

• Why am I getting SMSC Timeout?

• Explain Error Code 005

• What causes DLT Template Mismatch?

• Explain Invalid MSISDN

• Why are my SMS failing?
""")

    question = st.text_input(
        "Ask your telecom question"
    )

    # -------------------------------------------------------
    # Build Vector DB Only Once
    # -------------------------------------------------------

    if "vector_db_ready" not in st.session_state:

        with st.spinner(
            "Building Telecom Knowledge Base..."
        ):

            error_df = load_error_master(
                "data/error_codes.csv"
            )

            vector_db = VectorStore()

            vector_db.build_vector_db(error_df)

            st.session_state.vector_db_ready = True

    # -------------------------------------------------------
    # Initialize RAG Engine
    # -------------------------------------------------------

    rag = RAGEngine()

    col1, col2 = st.columns(2)

    # =======================================================
    # Search SOP
    # =======================================================

    with col1:

        if st.button("🔍 Search SOP"):

            if question.strip() == "":

                st.warning(
                    "Please enter a telecom question."
                )

            else:

                with st.spinner(
                    "Searching Telecom Knowledge Base..."
                ):

                    result = rag.search_sop(question)

                st.success(
                    "Knowledge Retrieved Successfully!"
                )

                with st.expander(
                    "📚 Telecom SOP",
                    expanded=True
                ):

                    st.code(result["context"])

    # =======================================================
    # AI Explain
    # =======================================================

    with col2:

        if st.button("🤖 AI Explain"):

            if question.strip() == "":

                st.warning(
                    "Please enter a telecom question."
                )

            else:

                with st.spinner(
                    "Generating AI Explanation..."
                ):

                    result = rag.ai_explain(question)

                if result["success"]:

                    st.success(
                        "AI Explanation Generated Successfully!"
                    )

                    st.markdown(
                        result["answer"]
                    )

                    with st.expander(
                        "📚 Knowledge Source"
                    ):

                        st.code(
                            result["context"]
                        )

                else:

                    st.warning(
                        "AI service is currently unavailable."
                    )

                    st.info(
                        "Showing Telecom SOP instead."
                    )

                    with st.expander(
                        "📚 Telecom SOP",
                        expanded=True
                    ):

                        st.code(
                            result["context"]
                        )

else:

    st.info(
        "📂 Please upload a telecom log file to begin analysis."
    )
st.divider()

with open("data/logs.csv", "rb") as file:

    st.download_button(
        label="⬇ Download Sample CSV",
        data=file,
        file_name="sample_telecom_logs.csv",
        mime="text/csv"
    )


st.markdown("""
---
### 👨‍💻 Developed by

**Shashi Ranjan Kumar**

Lead Customer Support | Telecom Operations | AI & Data Analytics

🔗 [GitHub](https://github.com/srkumar)

Version 2.0
""")