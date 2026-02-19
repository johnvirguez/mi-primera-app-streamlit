import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Calculadora de Crédito — Amortización", layout="centered")

st.title("Calculadora de crédito y tabla de amortización")

st.markdown(
    """  
    Ingresa los datos del crédito. La tasa que pides debe ser **Efectiva Anual (EAR)**.
    La app convierte EAR a tasa mensual y calcula la **cuota fija (método francés)**,
    la tabla de amortización y los gráficos de evolución de saldo y desglose interés/principal.
    """
)

# --- Inputs ---
col1, col2 = st.columns([2,1])
with col1:
    monto = st.number_input("Capital (monto del préstamo)", min_value=0.0, value=10000000.0, step=100000.0, format="%.2f")
    plazo_anos = st.number_input("Plazo (años)", min_value=1, max_value=50, value=5, step=1)
with col2:
    tasa_efectiva_anual = st.number_input("Tasa Efectiva Anual (%)", min_value=0.0, value=12.0, step=0.1, format="%.4f")

periodos_meses = int(plazo_anos * 12)

st.write("---")
st.subheader("Parámetros calculados")
# Convertir EAR a tasa mensual efectiva
r_mensual = (1 + tasa_efectiva_anual/100) ** (1/12) - 1
st.write(f"Tasa mensual efectiva: **{r_mensual*100:.6f}%**  (equivalente de {tasa_efectiva_anual:.2f}% E.A.)")
st.write(f"Plazo en meses: **{periodos_meses}**")

# --- Cálculo cuota según método francés (cuota fija) ---
if r_mensual == 0:
    cuota = monto / periodos_meses
else:
    cuota = monto * (r_mensual / (1 - (1 + r_mensual) ** (-periodos_meses)))

st.write(f"Cuota mensual (constante): **{cuota:,.2f}**")

# --- Construir tabla de amortización ---
months = np.arange(0, periodos_meses + 1)  # incluye mes 0
balance = monto
rows = []
rows.append({"Mes": 0, "Saldo Inicial": monto, "Cuota": 0.0, "Interés": 0.0, "Abono a Capital": 0.0, "Saldo Final": monto})

for m in range(1, periodos_meses + 1):
    interes = balance * r_mensual
    abono = cuota - interes
    # proteger contra pequeñas diferencias numéricas en el último pago
    if abono > balance:
        abono = balance
        cuota_real = interes + abono
    else:
        cuota_real = cuota
    saldo_final = balance - abono
    rows.append({
        "Mes": m,
        "Saldo Inicial": balance,
        "Cuota": cuota_real,
        "Interés": interes,
        "Abono a Capital": abono,
        "Saldo Final": saldo_final
    })
    balance = saldo_final

df = pd.DataFrame(rows)
# Formateo para presentación
df_display = df.copy()
df_display[["Saldo Inicial","Cuota","Interés","Abono a Capital","Saldo Final"]] = df_display[["Saldo Inicial","Cuota","Interés","Abono a Capital","Saldo Final"]].round(2)

st.write("---")
st.subheader("Tabla de amortización (primeros y últimos registros)")
st.dataframe(pd.concat([df_display.head(6), df_display.tail(6)]).reset_index(drop=True), height=300)

# Full table expandible
with st.expander("Ver tabla completa"):
    st.dataframe(df_display.style.format("{:,.2f}"), height=400)

# --- Gráficos ---
st.write("---")
st.subheader("Gráficos")

# Evolución del saldo
fig1, ax1 = plt.subplots(figsize=(8,3.5))
ax1.plot(df["Mes"], df["Saldo Final"], marker="o", markersize=3, linewidth=1)
ax1.set_title("Evolución del saldo del préstamo")
ax1.set_xlabel("Mes")
ax1.set_ylabel("Saldo (COP)")
ax1.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig1)

# Desglose interés vs abono a capital (stacked area)
fig2, ax2 = plt.subplots(figsize=(8,3.5))
ax2.stackplot(df["Mes"], df["Interés"], df["Abono a Capital"], labels=["Interés","Abono a capital"], colors=["#E74C3C", "#2ECC71"])
ax2.set_title("Desglose mensual: interés vs abono a capital")
ax2.set_xlabel("Mes")
ax2.set_ylabel("Valor (COP)")
ax2.legend(loc="upper right")
ax2.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig2)

# Gráfico de cuota (demuestra estabilidad)
fig3, ax3 = plt.subplots(figsize=(8,2.5))
ax3.plot(df["Mes"][1:], df["Cuota"][1:], marker=".", linewidth=1)
ax3.set_title("Cuotas mensuales")
ax3.set_xlabel("Mes")
ax3.set_ylabel("Cuota (COP)")
ax3.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig3)

# Resumen numérico
st.write("---")
st.subheader("Resumen numérico")
total_pagado = df["Cuota"].sum()
total_interes = df["Interés"].sum()
st.metric("Total pagado", f"{total_pagado:,.2f} COP")
st.metric("Total pagado en intereses", f"{total_interes:,.2f} COP")
st.write("Duración (meses):", periodos_meses)

# Descargar CSV
csv_buffer = df_display.to_csv(index=False).encode('utf-8')
st.download_button("Descargar tabla (CSV)", data=csv_buffer, file_name="tabla_amortizacion.csv", mime="text/csv")

st.caption("Nota: cálculos con fines orientativos. Revisar redondeos y condiciones contractuales reales.")
