import pandas as pd
import pydytuesday
import os


def get_annual_measles_data_with_per_population_change():
    download_data()
    df = pd.read_csv("cases_year.csv")

    # Impute South Sudan country for two records missing that name
    # Also change those records to the Africa region
    df.loc[df["iso3"] == "SSD", "country"] = "South Sudan"
    df.loc[df["iso3"] == "SSD", "region"] = "AFRO"

    # Drop 2025 because the year is not over
    df = df[df["year"] < 2025]

    # Prepare the dataset by adding columns for the difference in measles cases from the previous year
    g = df.groupby(["iso3", "year"])["measles_total"].sum()
    joined = (
        g.to_frame()
        .assign(current_measles=g)
        .join(g.groupby(level=[0]).shift().to_frame(), lsuffix="", rsuffix="_")
        .rename(columns={"measles_total_": "previous_measles"})
    )
    joined.update(
        joined[["current_measles", "previous_measles"]].mask(
            joined["previous_measles"].isna()
            | joined["previous_measles"].eq(joined["current_measles"]),
            0,
        )
    )
    agg_df = df.groupby(["iso3", "year"]).agg(
        {
            "region": "first",
            "measles_total": "sum",
            "country": "first",
            "total_population": "max",
            "year": "first",
        }
    )
    agg_df["previous_measles"] = joined["previous_measles"].astype("Int64")
    agg_df["absolute_change"] = agg_df["measles_total"] - agg_df["previous_measles"]
    agg_df["change_per_population_percent"] = (
        agg_df["absolute_change"] / agg_df["total_population"] * 100
    )
    agg_df["absolute_change_per_population_percent"] = abs(
        agg_df["change_per_population_percent"]
    )
    agg_df["year"] = agg_df["year"].astype(str)
    return agg_df


def download_data():
    if not os.path.exists("cases_year.csv") or not os.path.exists("cases_month.csv"):
        pydytuesday.tt_download_file("2025-06-24", "cases_year.csv")
        pydytuesday.tt_download_file("2025-06-24", "cases_month.csv")
