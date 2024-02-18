from population_trend.filter_data import filter_by_species_and_island
from population_trend.population_growth_model import (
    Population_Trend_Model,
    Plotter_Population_Trend_Model,
)
from population_trend.calculate_growth_rates import (
    Bootstrap_from_time_series_parametrizer,
    Bootstrap_from_time_series,
)
from population_trend.regional_lambdas import (
    Island_Bootstrap_Distribution_Concatenator,
    Calculator_Regional_Lambdas_Intervals,
)

from population_trend.plotter_growth_rate import Plotter_Growth_Rate

import pandas as pd
import typer
import json
import matplotlib.pyplot as plt

app = typer.Typer(help="Write filtered burrows data by species and island")


@app.command(help="Write json with bootstrap intervals")
def write_bootstrap_intervals_json(
    data_path: str = "data/processed/gumu_guadalupe_burrows.csv",
    blocks_length: int = 3,
    bootstrap_number: int = 2000,
    variable_of_interest: str = "Maxima_cantidad_nidos",
    alpha: float = 0.05,
    output_path: str = "reports/non-tabular/gumu_guadalupe_boostrap_intervals.json",
):
    data = pd.read_csv(data_path)
    parametrizer = Bootstrap_from_time_series_parametrizer(
        blocks_length=blocks_length,
        N=bootstrap_number,
        column_name=variable_of_interest,
        alpha=alpha,
    )
    parametrizer.set_data(data)
    bootstrap = Bootstrap_from_time_series(parametrizer)
    bootstrap.save_intervals(output_path)


@app.command(help="Write csv with ouput-path")
def write_burrows_by_species_and_island(
    data_path: str = "data/processed/subset_burrows_data.csv",
    species: str = "Guadalupe Murrelet",
    island: str = "Guadalupe",
    output_path: str = "data/processed/gumu_guadalupe_burrows.csv",
):
    data = pd.read_csv(data_path)
    filtered = filter_by_species_and_island(data, species, island)
    filtered.to_csv(output_path, index=False)


@app.command(help="Plot population trend")
def plot_population_trend(
    data_path: str = "",
    intervals_path: str = "",
    island: str = "Guadalupe",
    variable_of_interest: str = "Maxima_cantidad_nidos",
    output_path=None,
):
    fit_data = pd.read_csv(data_path)
    with open(intervals_path, "r") as read_file:
        intervals_json = json.load(read_file)
    lambda_latex = intervals_json["lambda_latex_interval"]

    Modelo_Tendencia_Poblacional = Population_Trend_Model(
        fit_data, intervals_json, variable_of_interest
    )
    Graficador = Plotter_Population_Trend_Model(fit_data, Modelo_Tendencia_Poblacional)
    Graficador.plot_smooth(Modelo_Tendencia_Poblacional)
    Graficador.plot_model(Modelo_Tendencia_Poblacional)
    Graficador.plot_data()
    legend_mpl_object = Graficador.set_legend_location(island)
    Graficador.plot_growth_rate_interval(legend_mpl_object, lambda_latex)
    Graficador.savefig(island, output_path)


@app.command(help="Write json with the regional trends")
def write_regional_trends(
    config_path: str = "data/processed/gumu_guadalupe_burrows.json",
    region: str = "",
    regional_trend_path: str = "",
    alpha: float = 0.05,
):
    concatenator = Island_Bootstrap_Distribution_Concatenator(config_path)
    concatenator.set_region(region)
    regional_lambdas = concatenator.mean_by_row()
    calculator = Calculator_Regional_Lambdas_Intervals(regional_lambdas, alpha)
    calculator.save_intervals(regional_trend_path)


@app.command()
def plot_growth_rate(
    intervals_california: str = "", intervals_pacific: str = "", output_path: str = ""
):
    lambdas_intervals_california = read_json(intervals_california)
    lambdas_intervals_pacific = read_json(intervals_pacific)

    plotter = Plotter_Growth_Rate(lambdas_intervals_california, lambdas_intervals_pacific)
    plotter.plot_error_bars()
    plt.savefig(output_path, transparent=True)


def read_json(intervals_json):
    with open(intervals_json, "r") as read_file:
        lambdas_intervals = json.load(read_file)
    return lambdas_intervals
