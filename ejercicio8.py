#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from datetime import datetime

# Rutas de los archivos para persistir datos
file_tienda1 = "tienda1.csv"
file_tienda2 = "tienda2.csv"

# Cargar datos de las tiendas desde archivos CSV
@st.cache_data
def cargar_datos(file_path):
    try:
        return pd.read_csv(file_path, parse_dates=["Fecha"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Fecha", "Ventas Totales", "Transacciones"])

# Guardar datos en archivos CSV
def guardar_datos(file_path, df):
    df.to_csv(file_path, index=False)

# Inicializar datos en `session_state`
if "data_tienda1" not in st.session_state:
    st.session_state["data_tienda1"] = cargar_datos(file_tienda1)
if "data_tienda2" not in st.session_state:
    st.session_state["data_tienda2"] = cargar_datos(file_tienda2)
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Función para autenticar al usuario
def autenticar_usuario():
    st.title("Autenticación de Usuario")
    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
        if usuario == "admin" and contraseña == "admin123":
            st.session_state["authenticated"] = True
            st.success("Autenticación exitosa")
        else:
            st.error("Usuario o contraseña incorrectos")

# Función para mostrar el menú
def mostrar_menu():
    return st.sidebar.radio(
        "Menú",
        ["Altas", "Bajas", "Cambios", "Consultas"]
    )

# Funciones de cada opción
def realizar_altas(tienda):
    st.subheader(f"Altas en {tienda}")
    fecha = st.date_input("Fecha de operación", value=datetime.today())
    ventas = st.number_input("Ventas totales", min_value=0.0, format="%.2f")
    transacciones = st.number_input("Número de transacciones", min_value=0, step=1)

    if st.button(f"Guardar en {tienda}"):
        nueva_fila = pd.DataFrame([{
            "Fecha": fecha,
            "Ventas Totales": ventas,
            "Transacciones": transacciones
        }])
        if tienda == "Tienda 1":
            st.session_state["data_tienda1"] = pd.concat([st.session_state["data_tienda1"], nueva_fila], ignore_index=True)
            guardar_datos(file_tienda1, st.session_state["data_tienda1"])
        elif tienda == "Tienda 2":
            st.session_state["data_tienda2"] = pd.concat([st.session_state["data_tienda2"], nueva_fila], ignore_index=True)
            guardar_datos(file_tienda2, st.session_state["data_tienda2"])
        st.success("Datos guardados correctamente")

def realizar_bajas(tienda):
    st.subheader(f"Bajas en {tienda}")
    if tienda == "Tienda 1":
        df = st.session_state["data_tienda1"]
    elif tienda == "Tienda 2":
        df = st.session_state["data_tienda2"]

    if not df.empty:
        fila_eliminar = st.selectbox("Seleccionar fila para eliminar", df.index)
        if st.button(f"Eliminar de {tienda}"):
            df.drop(fila_eliminar, inplace=True)
            if tienda == "Tienda 1":
                guardar_datos(file_tienda1, df)
            elif tienda == "Tienda 2":
                guardar_datos(file_tienda2, df)
            st.session_state[f"data_{tienda.lower().replace(' ', '')}"] = df
            st.success("Fila eliminada correctamente")
    else:
        st.warning(f"No hay datos en {tienda} para eliminar")

def realizar_cambios(tienda):
    st.subheader(f"Cambios en {tienda}")
    if tienda == "Tienda 1":
        df = st.session_state["data_tienda1"]
    elif tienda == "Tienda 2":
        df = st.session_state["data_tienda2"]

    if not df.empty:
        fila_cambiar = st.selectbox("Seleccionar fila para modificar", df.index)
        ventas = st.number_input("Ventas totales", min_value=0.0, format="%.2f")
        transacciones = st.number_input("Número de transacciones", min_value=0, step=1)
        
        if st.button(f"Modificar en {tienda}"):
            df.loc[fila_cambiar, "Ventas Totales"] = ventas
            df.loc[fila_cambiar, "Transacciones"] = transacciones
            if tienda == "Tienda 1":
                guardar_datos(file_tienda1, df)
            elif tienda == "Tienda 2":
                guardar_datos(file_tienda2, df)
            st.session_state[f"data_{tienda.lower().replace(' ', '')}"] = df
            st.success("Datos modificados correctamente")
    else:
        st.warning(f"No hay datos en {tienda} para modificar")

def realizar_consultas():
    st.subheader("Consultas")
    st.write("Datos de Tienda 1")
    st.dataframe(st.session_state["data_tienda1"])
    st.write("Datos de Tienda 2")
    st.dataframe(st.session_state["data_tienda2"])

    if not st.session_state["data_tienda1"].empty and not st.session_state["data_tienda2"].empty:
        st.write("Diferencias entre Tienda 1 y Tienda 2")
        diferencias = pd.DataFrame({
            "Fecha": st.session_state["data_tienda1"]["Fecha"],
            "Diferencia Ventas": st.session_state["data_tienda1"]["Ventas Totales"] - st.session_state["data_tienda2"]["Ventas Totales"],
            "Diferencia Transacciones": st.session_state["data_tienda1"]["Transacciones"] - st.session_state["data_tienda2"]["Transacciones"]
        })
        st.dataframe(diferencias)
    else:
        st.warning("No hay datos suficientes para calcular diferencias")

# Main
if __name__ == "__main__":
    if not st.session_state["authenticated"]:
        autenticar_usuario()
    else:
        menu = mostrar_menu()

        if menu == "Altas":
            tienda = st.radio("Seleccionar tienda", ["Tienda 1", "Tienda 2"])
            realizar_altas(tienda)
        elif menu == "Bajas":
            tienda = st.radio("Seleccionar tienda", ["Tienda 1", "Tienda 2"])
            realizar_bajas(tienda)
        elif menu == "Cambios":
            tienda = st.radio("Seleccionar tienda", ["Tienda 1", "Tienda 2"])
            realizar_cambios(tienda)
        elif menu == "Consultas":
            realizar_consultas()

