import pandas as pd
import swcol
def cluster(generation):
    # Clustering: Aplicar la función para obtener el cuartil y combinar con el año
    generation['Date'] = pd.to_datetime(generation['Date'])
    generation = swcol.rain_seasons.format_hours(generation)

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
def generate_by_periods(XM_report, load_type, base_year, grow_rate, period, cycles):
    loads = XM_report[['Date',load_type]]
    last_year = loads['Date'].iloc[-1].year
    if (last_year != base_year):
        print("Error: Base year doesn't match with XM_Report")
        return
    next_year = last_year + period
    loads_future = loads.copy()
    for i in range(cycles-1):
        # Replace only year
        loads_future['Date'] = loads_future['Date'].apply(replace_year, args=(next_year,))
        loads_future[load_type] = loads_future[load_type] * ((1+grow_rate)**period)

        #print(f'The year is: {next_year}')
        loads = pd.concat([loads, loads_future], axis=0)

        next_year += period
        loads_future = loads_future.copy()

    # Reset Dataframe
    loads.reset_index(drop=True, inplace=True)

    loads = loads.rename(columns={load_type: 'Load'})
    return loads

import pandas as pd
from tqdm.notebook import tqdm
def generate_by_zones(loads, zone_consume_perc):
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
    loads = swcol.rain_seasons.format_hours(loads)

    loads = loads.groupby(['timestamp','Zone']).agg({
        'demand_mw': 'mean',
        'Date': 'max'
    }).reset_index()
    return loads

import swcol
def melt_xm(path):
    """
    Args:
        path string: Path to DemaReal_Sistema.csv, DemaCome_Sistema.csv, Gene_Sistema.csv, GeneIdea_Sistema.csv

    Returns dataframe: Merged columns [Date, DemaReal_Sistema, DemaCome_Sistema, Gene_Sistema, GeneIdea_Sistema, timestamp]
    """
    # GetData
    DemaReal = pd.read_csv(path+'DemaReal_Sistema.csv')
    DemaReal = DemaReal.drop(DemaReal.columns[0], axis=1) # Drop Unnamed Column
    DemaCome = pd.read_csv(path+'DemaCome_Sistema.csv')
    DemaCome = DemaCome.drop(DemaCome.columns[0], axis=1) # Drop Unnamed Column
    Gene = pd.read_csv(path+'Gene_Sistema.csv')
    Gene = Gene.drop(Gene.columns[0], axis=1) # Drop Unnamed Column
    GeneIdea = pd.read_csv(path+'GeneIdea_Sistema.csv')
    GeneIdea = GeneIdea.drop(GeneIdea.columns[0], axis=1) # Drop Unnamed Column

    # Melt tables
    DemaReal = pd.melt(DemaReal.iloc[:,2:], id_vars=['Date'], var_name='Hora', value_name='DemaReal_Sistema')
    DemaCome = pd.melt(DemaCome.iloc[:,2:], id_vars=['Date'], var_name='Hora', value_name='DemaCome_Sistema')
    Gene = pd.melt(Gene.iloc[:,2:], id_vars=['Date'], var_name='Hora', value_name='Gene_Sistema')
    GeneIdea = pd.melt(GeneIdea.iloc[:,2:], id_vars=['Date'], var_name='Hora', value_name='GeneIdea_Sistema')

    # Merge Tables
    XM_report= pd.merge(DemaReal, DemaCome, on=['Date', 'Hora'])
    XM_report = pd.merge(XM_report, Gene, on=['Date', 'Hora'])
    XM_report = pd.merge(XM_report, GeneIdea, on=['Date', 'Hora'])

    XM_report['Hora'] = XM_report['Hora'].apply(swcol.rain_seasons.extract_hour)
    XM_report['Date'] = XM_report['Date'].astype(str)
    XM_report['Date'] = XM_report['Date'] + ' ' + XM_report['Hora']
    # Delete column "Hora"
    XM_report = XM_report.drop(columns=['Hora'])
    # Transform into timestamps
    XM_report = swcol.rain_seasons.format_hours(XM_report)
    
    XM_report = XM_report.sort_values(by='Date')
    XM_report = XM_report.reset_index(drop=True)

    return XM_report