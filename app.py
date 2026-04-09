import streamlit as st
import pandas as pd
import io

# Configuración visual de la App
st.set_page_config(page_title="Liquidador Ecommerce League", page_icon="💰", layout="centered")

st.title("⚖️ Liquidador Financiero - Dropi")
st.markdown("Sube el Excel de Dropi para separar las cuentas y saber cuánto le toca a cada tienda.")

# 1. El botón para subir el archivo
archivo_subido = st.file_uploader("Arrastra aquí tu Excel de Dropi (.xlsx)", type=["xlsx"])

if archivo_subido is not None:
    with st.spinner("Procesando las cuentas..."):
        # 2. Leer el Excel
        df = pd.read_excel(archivo_subido)
        
        cols_dinero = ['Valor Recaudo', 'Costo Flete', 'Costo Producto']
        for col in cols_dinero:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 3. Identificar a quién le pertenece
        def identificar_tienda(row):
            sku = str(row.get('SKU', '')).upper()
            if sku.startswith('CRIS'): return 'Cristhian'
            elif sku.startswith('ALE'): return 'Alejandro'
            elif sku.startswith('JHO'): return 'Jhoan'
            elif sku.startswith('NEX'): return 'NexusMarket'
            return 'Sin Identificar / Error SKU'

        if 'Tienda Origen' not in df.columns:
            df['Tienda Origen'] = df.apply(identificar_tienda, axis=1)

        # 4. Calcular la plata real
        def calcular_balance(row):
            estado = str(row.get('Estado Logístico', '')).lower()
            if 'entregado' in estado:
                return row['Valor Recaudo'] - row['Costo Flete'] - row['Costo Producto']
            elif 'devolución' in estado or 'novedad' in estado:
                return -(row['Costo Flete'])
            return 0 

        df['Resultado Neto (Ganancia/Pérdida)'] = df.apply(calcular_balance, axis=1)

        # 5. Agrupar y mostrar los resultados en pantalla
        resumen = df.groupby('Tienda Origen').agg({
            'Valor Recaudo': 'count', # Usado como contador de pedidos
            'Resultado Neto (Ganancia/Pérdida)': 'sum'
        }).rename(columns={'Valor Recaudo': 'Pedidos Procesados'}).reset_index()

        st.success("¡Liquidación exitosa!")
        
        # Mostrar la tabla bonita
        st.dataframe(resumen, use_container_width=True)

        # 6. Botón para descargar el resultado en Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            resumen.to_excel(writer, index=False, sheet_name='Liquidacion')
        
        st.download_button(
            label="📥 Descargar Reporte Final en Excel",
            data=buffer.getvalue(),
            file_name="Cuentas_Claras_Ecommerce.xlsx",
            mime="application/vnd.ms-excel"
        )