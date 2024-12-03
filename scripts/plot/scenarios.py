import pandas as pd

def table(model_outputs_path, model_inputs_path):
    new_gen = pd.read_csv(model_outputs_path+'BuildGen.csv')
    new_gen = new_gen[new_gen['GEN_BLD_YRS_2'] >= 2023]
    new_gen = new_gen[new_gen['BuildGen'] > 1]

    gen_info = pd.read_csv(model_inputs_path+'gen_info.csv')
    new_gen = pd.merge(new_gen, gen_info,
                        left_on='GEN_BLD_YRS_1',right_on='GENERATION_PROJECT',how='inner')

    new_gen = new_gen.groupby(['gen_tech','GEN_BLD_YRS_2']).agg({
        'BuildGen' : 'sum'}).reset_index()
    new_gen.rename(columns={'GEN_BLD_YRS_2': 'Year'}, inplace=True)
    new_gen['BuildGen'] = new_gen['BuildGen'].round(2)

    pivot_table = new_gen.pivot_table(index='gen_tech',columns='Year',
                                    values='BuildGen',aggfunc='sum').fillna(0)
    pivot_table.loc['Total'] = pivot_table.sum()

    return 

import plotly.express as px
def dispatched_generation(scenario_outputs_path, file):
    gen_disp = pd.read_csv(scenario_outputs_path+file)
    gen_disp = gen_disp.drop(gen_disp.columns[0], axis=1)
    gen_disp['year'] = gen_disp['timestamp'].str[:4]

    gen_disp = gen_disp.groupby(['year','gen_tech']).agg({
        'Energy_GWh_typical_yr' : 'sum'}).reset_index()
    gen_disp['Energy_GWh_typical_yr'] = gen_disp['Energy_GWh_typical_yr'] / 1000
    # Convert gen_tech to a categorical type with the specified order
    gen_disp['gen_tech'] = pd.Categorical(gen_disp['gen_tech'], categories=[
        'Menores','Thermal', 'Hidro','Eolica','pv_solar'], ordered=True)
    gen_disp = gen_disp.sort_values(['year', 'gen_tech'])
    gen_disp.rename(columns={'gen_tech': 'Tech'}, inplace=True)

    # Create a stacked bar plot
    fig = px.bar(
        gen_disp, x='year', y='Energy_GWh_typical_yr',
        color='Tech', title='Generation Dispatch Over Time by Technology',
        labels={'Energy_GWh_typical_yr': 'Dispatched Generation (MW)', 'year': 'Year'})
    # Update layout for better readability if needed
    fig.update_layout(barmode='stack', xaxis_title="Timestamp", xaxis={'tickangle': -45},
                    yaxis_title="Dispatched Generation (TWh)")
    fig.show()