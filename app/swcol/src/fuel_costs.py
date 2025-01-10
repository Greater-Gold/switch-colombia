import pandas as pd

def generate(path, base_year, cycles, period):
    """
    Generate a fuel cost file by replicating data over multiple cycles.

    Args:
        path (str): Output path where the fuel cost CSV will be saved.
        base_year (int): Starting year for the fuel cost data.
        cycles (int): Number of cycles to replicate the data.
        period (int): Time increment in years for each cycle.

    Returns:
        pd.DataFrame: Combined fuel cost data for all cycles.
    """
    # Load the full fuel cost data from the source file
    fuel_cost_full = pd.read_csv('../../data/XM-API/fuel_cost.csv')
    fuel_cost = pd.DataFrame()

    # Repeat fuel cost data for the specified number of cycles
    for _ in range(cycles):
        # Filter data for the current base year and append it to the result
        fuel_cost = pd.concat([
            fuel_cost,
            fuel_cost_full[fuel_cost_full['period'] == base_year]
        ], axis=0)

        # Increment the base year by the specified period
        base_year += period

    # Save the resulting DataFrame to a CSV file
    fuel_cost.to_csv(path + 'fuel_cost.csv', index=False)
    print(f'Fuel cost data saved to {path}fuel_cost.csv')

    return fuel_cost
