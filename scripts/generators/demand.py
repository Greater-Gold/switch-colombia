import pandas as pd

def add_tech(dema_path):
    generation = pd.read_csv(dema_path+'Gene_Recurso.csv')
    generation = generation.drop(generation.columns[:2], axis=1) # Remove the ID column
    print("Shape Gene_Recurso:",generation.shape)

    ListResour = pd.read_csv(dema_path+'LitadoRecursos_Sistema.csv')
    ListResour = ListResour[['Values_Code','Values_Type']]
    print("Shape LitadoRecursos_Sistema:",ListResour.shape)

    # Add 'Values_Type'(Tech) Column
    generation = pd.merge(generation, ListResour,
                          left_on="Values_code", right_on="Values_Code", how="inner")
    generation = generation.drop(columns=['Values_code','Values_Code'])

    return generation
    
def melt_into_dates(generation):
    generation = pd.melt(generation, id_vars=['Date','Values_Type'], var_name='Hora', value_name='GeneReal')
    # Convert Values into MW
    generation['GeneReal'] = generation['GeneReal'] / 1000
    # Aplica la función a la columna Hora
    generation['Hora'] = generation['Hora'].apply(rs.extract_hour)
    # Convierte la columna Date a string
    generation['Date'] = generation['Date'].astype(str)
    # Combina las columnas Date y Hora
    generation['Date'] = generation['Date'] + ' ' + generation['Hora']
    # Elimina la columna Hora ya que no la necesitamos más
    generation = generation.drop(columns=['Hora'])

    print("Shape Gene_Recurso (Melted):",generation.shape)
    # Group by Tech
    generation = generation.groupby(['Date','Values_Type']).agg({'GeneReal': 'sum'}).reset_index()
    generation = generation.rename(columns={'Values_Type': 'Tech'})
    print("Shape Gene_Recurso (Melted, Group by Tech):",generation.shape)

    return generation

import sys
import os
sys.path.append(os.path.abspath(os.path.join('..')))
import rain_seasons as rs
def cluster(generation):
    # Clustering: Aplicar la función para obtener el cuartil y combinar con el año
    generation['Date'] = pd.to_datetime(generation['Date'])
    generation['timestamp'] = generation['Date'].apply(\
        lambda x: f"{rs.year(x.year,x.strftime('%B'))}_{rs.quarter(x.strftime('%B'))}_{rs.day(x.day_name())}_{x.hour}h")

    generation = generation.groupby(['timestamp','Tech']).agg({
        'GeneReal': 'mean'}).reset_index()
    print("Shape Gene_Recurso (Melted, Group by Tech, Timestamp):",generation.shape)
    #gene_melted.to_csv(dema_path+'Melted_Gen_Res.csv')
    return generation

import plotly.express as px
def plot_multiple_line(generation, sort, x, y, color, title, labels):
    generation = generation.sort_values(by=sort)
    fig = px.line(
        generation, 
        x=x, y=y, 
        color=color, title=title,
        labels=labels
    )
    fig.show()