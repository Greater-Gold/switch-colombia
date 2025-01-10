import pandas as pd
def generate(model_path, cycles, period, base_year):
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
        year = base_year+i*period
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

def save_loads(model_path, loads, timepoints):
    loads = pd.merge(loads, timepoints, on='timestamp', how='inner')
    loads['timepoint_id'] = pd.to_numeric(loads['timepoint_id'], errors='coerce')
    # Order by Timepoints
    loads = loads[['Zone', 'timepoint_id', 'demand_mw']].sort_values(by='timepoint_id', ascending=False)
    # Rename Columns
    loads.columns = ['LOAD_ZONE', 'timepoints', 'zone_demand_mw']
    loads.to_csv(model_path+'loads.csv', index=False)
    print('File written '+model_path+'loads.csv')

    return loads