import streamlit as st


title = "Cahier des charges"
sidebar_name = "Cahier des charges"


def run():

    st.title(title)

    st.markdown("---")

    st.write("Schéma d'implantation - TOUT A FAIRE !")
    st.image("/airflow/data_others/JPG-PNG/schema_implantation.png")

    st.write("Suivi du cahier des charges  => à refaire proprement + images")
    st.image("/airflow/data_others/JPG-PNG/cahier_des_charges_1.png")
    st.image("/airflow/data_others/JPG-PNG/cahier_des_charges_2.png")
    st.image("/airflow/data_others/JPG-PNG/cahier_des_charges_3.png")