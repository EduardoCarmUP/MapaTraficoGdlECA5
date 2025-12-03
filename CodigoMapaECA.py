import streamlit as st
import pandas as pd
import pydeck as pdk
import time

#como referencia, todo lo que es una copia directa de los ejemplos del 19 Nov,
# dice "(como en ejemplos del 19 Nov)". Hay cosas, como los colores que no son rojo, que 
# son de investigar aparte, porque en ningun ejemplo venían puntos de colores.


st.title("Tráfico Zona Metropolitana GDL")
st.markdown("1 Segundo = 1 Hora de Tráfico")
#st.markdown("Cargando...")    Lo quité porque si no se queda aunque ya le piques play

    
# Carga directa del archivo, sin usar lo de "encoding ISO-8859-1" que venía en los ejemplos,
# pero vi que no afecta, no sé para qué era originalmente.

def load_data():
    file_path = "dataset2024.csv"
    #df = pd.read_csv(file_path)
    df = pd.read_csv('dataset2024.zip', compression='zip')
 

    
    # Convertir coordenadas a numérico y eliminar errores (como en ejemplos del 19 Nov) 
    df["Coordx"] = pd.to_numeric(df["Coordx"], errors="coerce")
    df["Coordy"] = pd.to_numeric(df["Coordy"], errors="coerce")
    df = df.dropna(subset=["Coordx", "Coordy"])
    
    # Convertir timestamp a objeto datetime para poder ordenarlo
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    return df

# Colores
def get_color(color_name):
    # Devuelve formato [R, G, B, A]
    if color_name == "green":
        return [24, 160, 57, 160]    # Verde oliva
    elif color_name == "red_wine":
        return [180, 0, 50, 200]     # Rojo vino (en lo del dataset venía como "wine")
    elif color_name == "red":        # Rojo Brillante
        return [255, 0, 0, 160] 
    elif color_name == "yellow":
        return [255, 255, 0, 160]    # Amarillo
    elif color_name == "orange":
        return [255, 140, 0, 180]    # Naranja
    else:
        return [128, 128, 128, 140]  # Gris por default, es porque como no sé si en las 1 988 521
                                         # lineas de "dataset2024" viene mencionado algun otro color 
        

# Cargar datos otra vez
df = load_data()

# Aplicar función de color al dataframe (crea una columna 'color_rgb')
df["color_rgb"] = df["predominant_color"].apply(get_color)

# Centro fijo, basado en promedio de plots (como en ejemplos del 19 Nov)
center_lat = df["Coordy"].mean()
center_lon = df["Coordx"].mean()

view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=11, #jugando con el zoom vi que el centro geométrico de los datos es avenida España
    pitch=0,  # Le puse sin inclincación (como en ejemplos del 19 Nov)
)


# Crear contenedor para mapa, y en este caso, también la hora (como en ejemplos del 19 Nov)
map_placeholder = st.empty()
status_text = st.empty()

# Botón para iniciar mapa (lo puse porque como se tarda en cargar el archivo, así da tiempo)
if st.button("Iniciar / Reiniciar   Mapa"):
    
    # Obtenemos los momentos únicos de tiempo ordenados
    unique_times = df["timestamp"].sort_values().unique()
    
    if len(unique_times) == 0:
        st.error("No hay datos de tiempo válidos para animar.")
    else:
        # Bucle principal de animación
        for current_time in unique_times:
            # Filtramos los datos para sólo este momento específico
            # (Aquí asumimos que cada timestamp representa una "foto" del tráfico en ese instante)
            batch = df[df["timestamp"] == current_time]
            
            # Formato para la hora
            formatted_time = pd.to_datetime(current_time).strftime('%Y-%m-%d %H:%M:%S')
            status_text.markdown(f"###  Fecha y Hora: {formatted_time}")

            # Crear capa de puntos (como en ejemplos del 19 Nov)
            # Usa el color precalculado en lo de rgba
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=batch,
                get_position=["Coordx", "Coordy"],
                get_fill_color="color_rgb",  # Usa la columna que creamos con lo de rgba
                get_radius=100,              # Tamaño del punto
                pickable=True,
                opacity=0.8,
                stroked=True,
                filled=True,
                radius_min_pixels=5,
                radius_max_pixels=50,
            )

            # Renderizar el mapa (como en ejemplos del 19 Nov)
            map_placeholder.pydeck_chart(
                pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_state,
                    tooltip={"html": "<b>ID:</b> {id}<br><b>Color:</b> {predominant_color}<br><b>Lógica:</b> {diffuse_logic_traffic}"}
                )
            )

            # Pausa para la animación (1 segundo = 1 hora de datos) para que cada 1 segundo reinicie
            # Esto basandome en que en los datos, se toman cada 1 hr, entonces solo tengo
            # que pausar el programa 1 segundo, y por la naturaleza de los datos,
            # la siguiente pasada va a ser 1 hora después den datos (porque así se registraron).
            # excepto cuando por alguna razón se salta unas horas de mañana a la tarde directo.

            time.sleep(1)

        st.success("Simulación finalizada.")