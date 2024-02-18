import numpy as np
from geci_plots import geci_plot, roundup, ticks_positions_array, order_magnitude
from bootstrapping_tools import power_law, lambda_calculator
import matplotlib.pyplot as plt


def normalize_seasons(df):
    first_season = int(df.Temporada.min())
    last_season = int(df.Temporada.max())
    return np.linspace(first_season, last_season, last_season - first_season + 1).astype(int)


def calculate_model_domain(data):
    last_value = data.Temporada.max() - data.Temporada.min()
    return np.linspace(0, last_value, 100)


def calculate_upper_limit(data_interest_variable):
    upper_limit = roundup(
        data_interest_variable.max() * 1.2,
        10 ** order_magnitude(data_interest_variable),
    )
    return upper_limit


class Population_Trend_Model:
    def __init__(self, fit_data, json_parameters, interest_variable):
        self.intervals = json_parameters["intervals"]
        self.model_domain = calculate_model_domain(fit_data)
        self.interest_variable = interest_variable
        self.initial_population = lambda_calculator(
            fit_data["Temporada"], fit_data[self.interest_variable]
        )
        self.bootstrap_distribution = json_parameters["bootstrap_intermediate_distribution"]

    def intern_model(self, i):
        return power_law(
            self.model_domain, self.bootstrap_distribution[i][0], self.bootstrap_distribution[i][1]
        )

    @property
    def min_model(self):
        return power_law(self.model_domain, self.intervals[0][0], self.intervals[0][1])

    @property
    def med_model(self):
        return power_law(self.model_domain, self.intervals[1][0], self.intervals[1][1])

    @property
    def max_model(self):
        return power_law(self.model_domain, self.intervals[2][0], self.intervals[2][1])


class Plotter_Population_Trend_Model:
    def __init__(self, data, population_model):
        self.fig, self.ax = geci_plot()
        self.data = data
        self.plot_seasons = self.data["Temporada"][:] - self.data["Temporada"].iloc[0] + 1
        self.ticks_text = normalize_seasons(self.data)
        self.ticks_positions = ticks_positions_array(self.ticks_text)
        self.plot_domain = np.linspace(self.ticks_positions.min(), self.ticks_positions.max(), 100)
        self.interest_variable = population_model.interest_variable

    def plot_smooth(self, Population_Trend_Model):
        self.ax.fill_between(
            self.plot_domain,
            Population_Trend_Model.min_model,
            Population_Trend_Model.med_model,
            label="Confidence zone",
            color="powderblue",
        )
        self.ax.fill_between(
            self.plot_domain,
            Population_Trend_Model.med_model,
            Population_Trend_Model.max_model,
            color="powderblue",
        )
        self.ax.fill_between(
            self.plot_domain,
            Population_Trend_Model.min_model,
            Population_Trend_Model.max_model,
            color="powderblue",
        )
        number_of_samples = len(Population_Trend_Model.bootstrap_distribution)
        for i in range(0, number_of_samples - 1, 10):
            self.ax.fill_between(
                self.plot_domain,
                Population_Trend_Model.intern_model(i),
                Population_Trend_Model.med_model,
                color="powderblue",
            )
            self.ax.fill_between(
                self.plot_domain,
                Population_Trend_Model.intern_model(i),
                Population_Trend_Model.intern_model(i + 1),
                color="powderblue",
            )
        self.ax.fill_between(
            self.plot_domain,
            Population_Trend_Model.intern_model(i + 1),
            Population_Trend_Model.med_model,
            color="powderblue",
        )

    def plot_model(self, Population_Trend_Model):
        plt.plot(
            self.plot_domain,
            Population_Trend_Model.med_model,
            label="Population growth model",
            color="b",
        )
        return self.fig

    def plot_data(self):
        plt.plot(
            self.plot_seasons,
            self.data[self.interest_variable],
            "-Dk",
            label="Active Nests",
        )

    def plot_growth_rate_interval(self, legend_mpl_object, lambda_latex):
        legend_box_positions = legend_mpl_object.get_window_extent()
        self.ax.annotate(
            r"$\lambda =$ {}".format(lambda_latex),
            (legend_box_positions.p0[0], legend_box_positions.p1[1] - 320),
            xycoords="figure pixels",
            fontsize=25,
            color="k",
            alpha=1,
        )

    def set_y_lim(self):
        self.ax.set_ylim(
            0,
            calculate_upper_limit(self.data[self.interest_variable]),
        )

    def set_x_lim(self):
        plt.xlim(
            self.ticks_positions.min() - 0.2,
            self.ticks_positions.max(),
        )

    def set_labels(self):
        plt.ylabel("Number of breeding pairs", size=20)
        plt.xlabel("Seasons", size=20)

    def set_ticks(self):
        plt.xticks(
            self.ticks_positions,
            self.ticks_text,
            rotation=90,
            size=20,
        )
        plt.yticks(size=20)

    def draw(self):
        plt.gcf().subplots_adjust(bottom=0.2)
        plt.draw()

    def savefig(self, islet, output_path=None):
        self.set_x_lim()
        self.set_y_lim()
        self.set_labels()
        self.set_ticks()
        self.draw()
        transparent_background = True
        if output_path is None:
            plt.savefig(
                "reports/figures/cormorant_population_trend_{}".format(
                    islet.replace(" ", "_").lower()
                ),
                dpi=300,
                transparent=transparent_background,
            )
        else:
            plt.savefig(output_path, dpi=300, transparent=transparent_background)

    def set_legend_location(self, islet):
        legend_mpl_object = plt.legend(loc="best")
        if islet == "Natividad":
            legend_mpl_object = plt.legend(loc="upper left")
        return legend_mpl_object
