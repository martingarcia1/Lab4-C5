import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
## ATENCION: Debe colocar la direccion en la que ha sido publicada la aplicacion en la siguiente linea\
# url = https://tp8-59184.streamlit.app/

# Mostrar información del alumno
def mostrar_informacion_alumno():
    with st.container():
        st.markdown('**Legajo:** 59184')
        st.markdown('**Nombre:** Matías Leandro Lucena')
        st.markdown('**Comisión:** C5')

def calcular_metricas(df):
    df['Ingreso_total'] = df['Ingreso_total'].fillna(0)
    df['Unidades_vendidas'] = df['Unidades_vendidas'].replace(0, np.nan) 
    df['Costo_total'] = df['Costo_total'].fillna(0)

    df['Precio Promedio'] = df['Ingreso_total'] / df['Unidades_vendidas']
    df['Margen'] = ((df['Ingreso_total'] - df['Costo_total']) / df['Ingreso_total']) * 100

    df['Precio Promedio'] = df['Precio Promedio'].fillna(0)
    df['Margen'] = df['Margen'].fillna(0)
    
    return df

def calcular_variaciones(df):
    variaciones = {}
    for producto in df['Producto'].unique():
        datos_producto = df[df['Producto'] == producto]
        precio_promedio_anual = datos_producto.groupby('Año')['Precio Promedio'].mean()
        margen_promedio_anual = datos_producto.groupby('Año')['Margen'].mean()
        unidades_vendidas_anual = datos_producto.groupby('Año')['Unidades_vendidas'].sum()

        variaciones[producto] = {
            "variacion_precio_promedio": precio_promedio_anual.pct_change().dropna().mean() * 100,
            "variacion_margen_promedio": margen_promedio_anual.pct_change().dropna().mean() * 100,
            "variacion_unidades_vendidas": unidades_vendidas_anual.pct_change().dropna().mean() * 100
        }
    return variaciones

def graficar_evolucion(df, producto):
    datos_producto = df[df['Producto'] == producto].groupby(['Año', 'Mes']).sum().reset_index()

    datos_producto['Fecha'] = pd.to_datetime(
        {
            'year': datos_producto['Año'],
            'month': datos_producto['Mes'],
            'day': 1
        }
    )

    plt.figure(figsize=(12, 8))
    plt.plot(
        datos_producto['Fecha'],
        datos_producto['Unidades_vendidas'],
        label=f'{producto}',
        color='blue',
        linewidth=3  
    )

    z = np.polyfit(range(len(datos_producto)), datos_producto['Unidades_vendidas'], 1)
    p = np.poly1d(z)
    plt.plot(
        datos_producto['Fecha'],
        p(range(len(datos_producto))),
        "--",
        color='red',
        linewidth=2.5,
        label='Tendencia'
    )

    plt.title(f"Evolución de Ventas Mensual - {producto}", fontsize=18, fontweight='bold', pad=20)
    plt.xlabel("Fecha", fontsize=14, labelpad=15)
    plt.ylabel("Unidades Vendidas", fontsize=14, labelpad=15)
    plt.xticks(fontsize=12, rotation=45)
    plt.yticks(fontsize=12)
    plt.grid(visible=True, linestyle='--', alpha=0.5)
    plt.legend(fontsize=12, loc='upper left', frameon=False)
    plt.tight_layout()
    st.pyplot(plt)

def main():
    st.title("Aplicación de Ventas")
    mostrar_informacion_alumno()

    st.sidebar.header("Cargar archivo de datos")
    archivo_csv = st.sidebar.file_uploader("Subir archivo CSV", type=["csv"])

    if archivo_csv is not None:
        df = pd.read_csv(archivo_csv)

        df = calcular_metricas(df)

        sucursales = st.sidebar.selectbox("Seleccionar Sucursal", ["Todas"] + df['Sucursal'].unique().tolist())
        if sucursales != "Todas":
            df = df[df['Sucursal'] == sucursales]

        variaciones = calcular_variaciones(df)

        productos = df['Producto'].unique()
        for producto in productos:
            datos_producto = df[df['Producto'] == producto]
            precio_promedio = datos_producto['Precio Promedio'].mean()
            margen_promedio = datos_producto['Margen'].mean()
            unidades_vendidas = datos_producto['Unidades_vendidas'].sum()

            variacion_precio = variaciones[producto]["variacion_precio_promedio"]
            variacion_margen = variaciones[producto]["variacion_margen_promedio"]
            variacion_unidades = variaciones[producto]["variacion_unidades_vendidas"]

            col1, col2 = st.columns([1, 3])
            with col1:
                st.subheader(producto)
                st.metric("Precio Promedio", f"${precio_promedio:,.2f}", delta=f"{variacion_precio:+.2f}%")
                st.metric("Margen Promedio", f"{margen_promedio:,.2f}%", delta=f"{variacion_margen:+.2f}%")
                st.metric("Unidades Vendidas", f"{int(unidades_vendidas):,}", delta=f"{variacion_unidades:+.2f}%")
            with col2:
                graficar_evolucion(df, producto)

            st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
