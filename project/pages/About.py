import streamlit as st

st.header("About Me")

st.write(
    """
    👋 **Hello!**  
    I’m **Tawanda Motsi** — a technically minded and goal-oriented professional with a unique background in both **Irrigation Engineering** and **Computer Engineering**.

    I hold a Bachelor’s degree in Irrigation Engineering from **Chinhoyi University of Technology** in Zimbabwe and I’m currently completing my BSc in **Software Engineering** at the **Technological University of the Shannon**. My diverse experience includes designing and installing micro, overhead, and surface irrigation systems, along with pump selection and water system planning.

    More recently, I’ve been expanding my focus to include **software development**, **data analysis**, and **programming**, with strong proficiency in **Java** and growing experience in building full-stack applications.

    This web application showcases my ability to collect, clean, process, analyse, and visualise data, blending technical skill with practical insight.

    If you'd like to connect or have any questions, feel free to reach out via LinkedIn:🔗 [link]((https://www.linkedin.com/in/tawanda-motsi-24593b84))
    """,
    unsafe_allow_html=True
)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("images/tawa.jpeg", caption="Somewhere on the Globe")
