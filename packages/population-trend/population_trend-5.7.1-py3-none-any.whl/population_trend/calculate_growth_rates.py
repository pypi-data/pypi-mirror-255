from bootstrapping_tools import (
    bootstrap_from_time_series,
    calculate_intervals_from_p_values_and_alpha,
    calculate_p_values,
    generate_latex_interval_string,
    get_bootstrap_deltas,
    lambda_calculator,
    power_law,
)
from matplotlib.ticker import MaxNLocator

import json
import matplotlib.pyplot as plt
import numpy as np


def calculate_porcentual_diff(x, y):
    return 100 * (x - y) / y


def generate_number_and_season_string(number, season):
    return "{} ({})".format(
        number,
        season,
    )


def calculate_seasons_intervals(seasons):
    years = []
    first_index = 0
    for index in np.where(np.diff(seasons) != 1)[0]:
        if seasons[first_index] == seasons[index]:
            years.append(f"{seasons[index]}")
        else:
            years.append(f"{seasons[first_index]}-{seasons[index]}")
        first_index = index + 1
    years.append(f"{seasons[first_index]}-{seasons[-1]}")
    return years


def calculate_interest_numbers(cantidad_nidos, model):
    first_number = generate_number_and_season_string(
        cantidad_nidos["Maxima_cantidad_nidos"].iloc[0],
        cantidad_nidos["Temporada"].iloc[0],
    )
    first_number_calculated = generate_number_and_season_string(
        model.iloc[0], cantidad_nidos["Temporada"].iloc[0]
    )
    last_number = "{{{:,.0f}}} ({})".format(
        cantidad_nidos["Maxima_cantidad_nidos"].iloc[-1],
        int(cantidad_nidos["Temporada"].iloc[-1]),
    )
    last_number_calculated = generate_number_and_season_string(
        model.iloc[-1],
        cantidad_nidos["Temporada"].iloc[-1],
    )
    return first_number, first_number_calculated, last_number, last_number_calculated


def calculate_percent_diff_in_seasons(cantidad_nidos, model):
    if cantidad_nidos["Maxima_cantidad_nidos"].iloc[0] == 0:
        porcentaje_cambio = calculate_porcentual_diff(model.iloc[-1], model.iloc[0])
    else:
        porcentaje_cambio = calculate_porcentual_diff(
            model.iloc[-1], cantidad_nidos["Maxima_cantidad_nidos"].iloc[0]
        )
    return porcentaje_cambio


class Bootstrap_from_time_series_parametrizer:
    def __init__(self, blocks_length=3, N=2000, column_name="Maxima_cantidad_nidos", alpha=0.05):
        self.parameters = dict(
            dataframe=None,
            column_name=column_name,
            N=N,
            return_distribution=True,
            blocks_length=blocks_length,
            alpha=alpha,
        )

    def set_data(self, data):
        self.parameters["dataframe"] = data


Bootstrap = dict(
    default=Bootstrap_from_time_series_parametrizer(),
    testing=Bootstrap_from_time_series_parametrizer(blocks_length=2, N=100),
)


class Bootstrap_from_time_series:
    def __init__(self, bootstrap_parametrizer):
        self.parameters = bootstrap_parametrizer.parameters
        self.lambdas_n0_distribution, _ = self._calculate_distribution_and_interval()
        self.season_series = self.parameters["dataframe"]["Temporada"]
        self.data_series = self.parameters["dataframe"][self.parameters["column_name"]]
        self.lambdas = [lambdas_n0[0] for lambdas_n0 in self.lambdas_n0_distribution]
        self.p_values = self.get_p_values()
        self.intervals = self.intervals_from_p_values_and_alpha()
        self.interval_lambdas = [interval[0] for interval in self.intervals]
        self.lambda_latex_interval = self.get_lambda_interval_latex_string()

    def intervals_from_p_values_and_alpha(self):
        intervals = calculate_intervals_from_p_values_and_alpha(
            self.lambdas_n0_distribution, self.p_values, self.parameters["alpha"]
        )
        return intervals

    def get_p_values(self):
        p_value_mayor, p_value_menor = calculate_p_values(self.lambdas)
        p_values = (p_value_mayor, p_value_menor)
        return p_values

    def get_distribution(self):
        return self.lambdas_n0_distribution

    def _calculate_distribution_and_interval(self):
        lambdas_n0_distribution, intervals = bootstrap_from_time_series(**self.parameters)
        return lambdas_n0_distribution, intervals

    def get_inferior_central_and_superior_limit(self):
        inferior_limit, central, superior_limit = get_bootstrap_deltas(
            self.interval_lambdas, **{"decimals": 2}
        )
        return inferior_limit, central, superior_limit

    def get_lambda_interval_latex_string(self):
        lambda_latex_string = generate_latex_interval_string(
            self.interval_lambdas, deltas=False, **{"decimals": 2}
        )
        return lambda_latex_string

    def generate_season_interval(self):
        return "({}-{})".format(
            self.season_series.min(axis=0),
            self.season_series.max(axis=0),
        )

    def get_monitored_seasons(self):
        monitored_seasons = np.sort(self.season_series.astype(int).unique())
        if len(monitored_seasons) == 1:
            return f"{monitored_seasons[0]}"
        else:
            seasons_intervals = calculate_seasons_intervals(monitored_seasons)
            return ",".join(seasons_intervals)

    def fit_population_model(self):
        parameters = lambda_calculator(self.season_series, self.data_series)
        model = power_law(
            self.season_series - self.season_series.iloc[0],
            parameters[0],
            parameters[1],
        )
        return model

    def get_intermediate_lambdas(self):
        return [
            lambda_n0
            for lambda_n0 in self.lambdas_n0_distribution
            if (lambda_n0[0] > self.intervals[0][0]) and (lambda_n0[0] < self.intervals[2][0])
        ]

    def save_intervals(self, output_path):
        json_dict = {
            "intervals": list(self.intervals),
            "lambda_latex_interval": self.lambda_latex_interval,
            "p-values": self.p_values,
            "bootstrap_intermediate_distribution": self.get_intermediate_lambdas(),
        }
        with open(output_path, "w") as file:
            json.dump(json_dict, file)


def calculate_growth_rates_table(bootstrap: Bootstrap_from_time_series_parametrizer):
    bootstraper = Bootstrap_from_time_series(bootstrap)
    df = bootstrap.parameters["dataframe"]
    model = bootstraper.fit_population_model()
    inferior_limit, central, superior_limit = bootstraper.get_inferior_central_and_superior_limit()
    lambda_latex_string = bootstraper.get_lambda_interval_latex_string()
    bootstrap_distribution = bootstraper.get_distribution()
    lambdas_distribution = [interval[0] for interval in bootstrap_distribution]
    p_value_mayor, p_value_menor = calculate_p_values(lambdas_distribution)
    intervalo = bootstraper.generate_season_interval()
    monitored_seasons = bootstraper.get_monitored_seasons()
    porcentaje_cambio = calculate_percent_diff_in_seasons(df, model)
    (
        first_number,
        _,
        last_number,
        last_number_calculated,
    ) = calculate_interest_numbers(df, model)
    return [
        intervalo,
        first_number,
        last_number,
        last_number_calculated,
        lambda_latex_string,
        df["Latitud"].iloc[0],
        central,
        f"-{inferior_limit}",
        f"+{superior_limit}",
        f"{{{int(porcentaje_cambio):,}}}",
        p_value_mayor,
        p_value_menor,
        monitored_seasons,
    ]


def set_axis_plot_config(ax):
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    fontsize = 20
    plt.yticks(rotation=90, size=fontsize)
    locs_x, _ = plt.xticks()
    locs_y, _ = plt.yticks()
    plt.xticks(locs_x[1:], size=fontsize)
    plt.xlim(locs_x[0], locs_x[-1])
    plt.ylim(0, locs_y[-1])
    ax.set_xlabel("Año", size=fontsize, labelpad=10)
    plt.ylabel("Cantidad de parejas reproductoras", size=fontsize)
