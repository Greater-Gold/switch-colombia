import pandas as pd

import sys
import os
sys.path.append(os.path.abspath(os.path.join('..')))
import rain_seasons as rs
def cluster(generation):
    # Clustering: Aplicar la función para obtener el cuartil y combinar con el año
    generation['Date'] = pd.to_datetime(generation['Date'])
    generation = rs.format_hours(generation)

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

# Replace with new year
def replace_year(timestamp, new_year):
    new_timestamp = str(new_year) + str(timestamp)[4:]
    return pd.Timestamp(new_timestamp)

# Generate loads by Periods
def gen_loads_by_periods(XM_report, load_type, grow_rate, period, cycles):
    loads = XM_report[['Date',load_type]]
    # Init
    last_year = loads['Date'].iloc[-1].year
    next_year = last_year + period
    loads_future = loads.copy()
    for i in range(cycles-1):
        # Aplicar la función solo a las primeras letras
        loads_future['Date'] = loads_future['Date'].apply(replace_year, args=(next_year,))
        loads_future[load_type] = loads_future[load_type] * ((1+grow_rate)**period)

        #print(f'The year is: {next_year}')
        loads = pd.concat([loads, loads_future], axis=0)

        next_year += period
        loads_future = loads_future.copy()

    # Reiniciar el índice del DataFrame final
    loads.reset_index(drop=True, inplace=True)

    loads = loads.rename(columns={load_type: 'Load'})
    return loads, last_year

import pandas as pd
from tqdm.notebook import tqdm
def gen_loads_by_zones(loads, zone_consume_perc):
    # Convert to perentages
    zone_consume_perc['Proportion'] = zone_consume_perc['Value'] / 100
    # Store results
    res = []
    # Iterar sobre las filas de ventas y distribuir por zonas
    for _, load_row in tqdm(loads.iterrows(), total=loads.shape[0], desc="Processing Files"):
        for _, zone_row in zone_consume_perc.iterrows():
            zone_loads = load_row['Load'] * zone_row['Proportion']
            res.append({
                'Date': load_row['Date'],
                'Zone': zone_row['Zone'],
                'Load': zone_loads
            })
    
    res = pd.DataFrame(res)
    res['demand_mw'] = round(res['Load'] / 1000, 2)
    res = res.drop(columns=['Load'])
    return res

def loads_to_timestamps(loads):
    loads = loads.groupby(['Date','Zone']).agg({
        'demand_mw': 'sum'
    }).reset_index()

    loads['Date'] = pd.to_datetime(loads['Date'])
    loads = rs.format_hours(loads)

    loads = loads.groupby(['timestamp','Zone']).agg({
        'demand_mw': 'mean',
        'Date': 'max'
    }).reset_index()
    return loads