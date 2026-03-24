import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns


# ------------------ CONFIG UI ------------------
st.set_page_config(page_title="Pricing App", layout="wide")

st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💰 App de Pricing basado en Valor")

# ------------------ PASO 1 ------------------
st.header("1️⃣ Definición de Competidores")
st.info("Asegúrate de ingresar al menos 2 competidores para un análisis preciso")

df_comp = pd.DataFrame({
    "Competidor": ["A", "B"],
    "Servicio": ["Asesoría", "Asesoría"],
    "Opcion": ["Oro", "Plata"],
    "Precio": [1000, 800]
})

df_comp = st.data_editor(
    df_comp,
    num_rows="dynamic",
    column_config={
        "Opcion": st.column_config.SelectboxColumn(
            "Opción de valor",
            options=["Oro", "Plata", "Bronce"],
            required=True
        ),
        "Servicio": st.column_config.TextColumn("Servicio"),
        "Competidor": st.column_config.TextColumn("Competidor"),
        "Precio": st.column_config.NumberColumn("Precio", min_value=0)
    }
)

# ------------------ PASO 2 ------------------
st.header("2️⃣ Valor percibido por el cliente")
st.info("Describa 4  atributos de valor y su importancia según la necesidad de los clientes, estos deben sumar el 100%")

df_attr = pd.DataFrame({
    "Atributo": ["Calidad", "Soporte", "Tecnología", "Personalización"],
    "Importancia (%)": [40, 30, 20, 10]
})

df_attr = st.data_editor(df_attr, num_rows=4)

total = df_attr["Importancia (%)"].sum()
if total != 100:
    st.error(f"❌ La suma debe ser 100%. Actual: {total}%")
else:
    st.success("✅ Pesos correctos")

# ------------------ PASO 3 ------------------
st.header("3️⃣ Evaluación de la competencia")
st.info("Califique objetivamente a la competencia (Bajo, Medio, Alto), acorde a los atributos de valor relacionados en el paso anterior")


escala = ["Bajo", "Medio", "Alto"]

if len(df_comp) >= 1:
    cols = ["Competidor"] + df_attr["Atributo"].tolist()
    df_eval = pd.DataFrame(columns=cols)
    df_eval["Competidor"] = df_comp["Competidor"]

    for col in df_attr["Atributo"]:
        df_eval[col] = "Medio"

    df_eval = st.data_editor(
    df_eval,
    column_config={
        "Competidor": st.column_config.TextColumn(
            "Competidor",
            disabled=True  # 🔒 BLOQUEADO
        ),
        **{
            col: st.column_config.SelectboxColumn(
                options=escala
            )
            for col in df_attr["Atributo"]
        }
    }
)



    # ------------------ PASO 4 ------------------
    mapping = {"Bajo": 1, "Medio": 3, "Alto": 5}
    df_calc = df_eval.copy()

    for col in df_attr["Atributo"]:
        df_calc[col] = df_calc[col].map(mapping)

    pesos = df_attr["Importancia (%)"].values / 100
    df_calc["Valor Percibido"] = df_calc[df_attr["Atributo"]].mul(pesos).sum(axis=1)

    df_final = df_calc.merge(df_comp[["Competidor", "Precio"]], on="Competidor")

    st.subheader("4️⃣ Calculo del valor percibido de la competencia")
    st.info("🔒 Este cálculo es automático y no editable")

    st.dataframe(df_final[["Competidor", "Valor Percibido", "Precio"]])

    

    # ------------------ PASO 5 ------------------
    st.subheader("5️⃣ Diseña tu servicio")
    st.info("Diseña tu servicio , asignandole una opción y atributos de valor a ofrecer a nuestros clientes.")

    st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: 50px;
}
[data-testid="stMetricLabel"] {
    font-size: 22px;
}
</style>
""", unsafe_allow_html=True)

    opcion = st.selectbox("Opción de valor", ["Oro", "Plata", "Bronce"])
    servicio = st.text_input("Descripción del servicio")

    user_scores = {}
    for attr in df_attr["Atributo"]:
        user_scores[attr] = st.selectbox(f"{attr}", escala, key=attr)

    user_numeric = [mapping[v] for v in user_scores.values()]
    user_vp = np.dot(user_numeric, pesos)

    
    st.metric("📊 Valor Percibido de tu servicio", round(user_vp, 2))
   

# ------------------ BOTÓN ------------------
if st.button("🚀 Definir Pricing"):

    if len(df_comp) < 2:
        st.error("Debes ingresar al menos 2 competidores")
        st.stop()

    if total != 100:
        st.error("Los pesos deben sumar 100%")
        st.stop()

    # ------------------ PASO 6 ------------------
    X = df_final[["Valor Percibido"]]
    y = df_final["Precio"]

    model = LinearRegression()
    model.fit(X, y)

    precio_pred = model.predict([[user_vp]])[0]

    col1, col2 = st.columns(2)
    col1.metric("💰 Precio sugerido", f"${precio_pred:,.0f}")
    

    

    # ------------------ PASO 7 ------------------
    st.subheader("📍 Mapa de Valor")

    sns.set_style("whitegrid")

    fig, ax = plt.subplots()

    # Scatter competidores
    sns.scatterplot(
        data=df_final,
        x="Valor Percibido",
        y="Precio",
        s=100,
        ax=ax
    )

    # Punto del usuario
    ax.scatter(user_vp, precio_pred, marker="X", s=200)

    # Línea de regresión
    sns.regplot(
        data=df_final,
        x="Valor Percibido",
        y="Precio",
        scatter=False,
        ax=ax
    )

    # Labels
    for i, row in df_final.iterrows():
        ax.text(row["Valor Percibido"], row["Precio"], row["Competidor"])

    ax.set_title("Mapa de Valor")
    ax.set_xlabel("Valor Percibido")
    ax.set_ylabel("Precio")

    st.pyplot(fig)