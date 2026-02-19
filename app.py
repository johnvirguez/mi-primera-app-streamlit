import streamlit as st

st.title("Mi primera aplicación web desde Python")

nombre = st.text_input("Escribe tu nombre")

if nombre:
    st.success(f"Hola {nombre}, esta app está corriendo desde la nube 🚀")

numero = st.number_input("Ingresa un número", value=5)
st.write("El doble es:", numero * 2)
