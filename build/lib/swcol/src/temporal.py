import pandas as pd
def write_time(model_path, cycles, period, last_year):
    # Sample input values
    Quartiles = [1, 2, 3, 4]
    day_types = ["labor", "holidays"]
    hours = 24
    # Initialize an empty list to collect data
    timepoints = []
    timeseries = []
    periods = []
    # Loop to generate timepoint data
    n = 0
    for i in range(cycles):
        year = last_year+i*period
        periods.append([year,year,year+period-1])
        for Q in Quartiles:
            Q_year = year
            #if Q == 1: Q_year = year-1
            for day_type in day_types:
                timeseries_name = f"{Q_year}_Q{Q}_{day_type}"
                if day_type == 'labor':
                    timeseries.append([timeseries_name,Q_year,1,24,(365/4/7)*6*period])
                else:
                    timeseries.append([timeseries_name,Q_year,1,24,(365/4/7)*period])
                for hour in range(hours):
                    n += 1
                    timepoint_id = str(n)
                    timestamp = f"{Q_year}_Q{Q}_{day_type}_{hour}h"                
                    timepoints.append([timepoint_id, timestamp, timeseries_name])

    # Create DataFrame from collected data
    timepoints = pd.DataFrame(timepoints, columns=["timepoint_id", "timestamp", "timeseries"])
    timeseries = pd.DataFrame(timeseries, columns=["TIMESERIES","ts_period","ts_duration_of_tp","ts_num_tps","ts_scale_to_period"])
    periods = pd.DataFrame(periods, columns=["INVESTMENT_PERIOD","period_start","period_end"])

    # Display the DataFrame
    timepoints.to_csv(model_path+'timepoints.csv', index=False)
    print('File written '+model_path+'timepoints.csv')
    timeseries.to_csv(model_path+'timeseries.csv', index=False)
    print('File written '+model_path+'timeseries.csv')
    periods.to_csv(model_path+'periods.csv', index=False)
    print('File written '+model_path+'periods.csv')

    return timepoints

# Test
def write_loads(model_path, loads, timepoints):
    loads = pd.merge(loads, timepoints, on='timestamp', how='inner')
    loads['timepoint_id'] = pd.to_numeric(loads['timepoint_id'], errors='coerce')
    # Order by Timepoints
    loads = loads[['Zone', 'timepoint_id', 'demand_mw']].sort_values(by='timepoint_id', ascending=False)
    # Rename Columns
    loads.columns = ['LOAD_ZONE', 'timepoints', 'zone_demand_mw']
    loads.to_csv(model_path+'loads.csv', index=False)
    print('File written '+model_path+'loads.csv')

    return loads

import sys
import os
sys.path.append(os.path.abspath(os.path.join('..')))
import rain_seasons as rs
def to_timestamp(path):
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

    XM_report['Hora'] = XM_report['Hora'].apply(rs.extract_hour)
    XM_report['Date'] = XM_report['Date'].astype(str)
    XM_report['Date'] = XM_report['Date'] + ' ' + XM_report['Hora']
    # Delete column "Hora"
    XM_report = XM_report.drop(columns=['Hora'])
    # Transform into timestamps
    XM_report = rs.format_hours(XM_report)
    
    XM_report = XM_report.sort_values(by='Date')
    XM_report = XM_report.reset_index(drop=True)

    return XM_report

