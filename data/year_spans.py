from typing import Tuple
import numpy as np
import pandas as pd


def get_names(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename)
    return df.melt(id_vars=["name"], var_name="year", value_name="num")


def year_span_for_name(df_all: pd.DataFrame, name: str, target_fraction: float) -> Tuple[float, float, float]:
    """
    Calculate the smallest year span that contains `target_fraction`
    of all people with the given name.
    """
    def fraction(df_name, years):
        return df_name.query("year in @years").num.sum() / df_name.num.sum()
    
    df_name = df_all.query("name == @name")
    top_year = df_name.year.values[df_name.num.argmax()]
    years = set((top_year, ))
    f = fraction(df_name, years)
    while f < target_fraction:
        right_year =  max(years) + 1
        left_year =  min(years) - 1
        if right_year <= df_name.year.max() and df_name.query("year == @right_year").num.values[0] > df_name.query("year == @left_year").num.values[0]:
            years.add(right_year)
        elif left_year >= df_name.year.min():
            years.add(left_year)
        f = fraction(df_name, years)
    return years, f, top_year


def std_for_name(df_all: pd.DataFrame, name: str) -> float:
    df_name = df_all.query("name == @name")
    years = np.concatenate([np.ones(data.num) * data.year for _, data in df_name.iterrows()])
    return years.std()


if __name__ == "__main__":
    df_boys = get_names("data/BE0001AM_20210507-184020.csv")
    df_girls = get_names("data/BE0001AM_20210507-183718.csv")
    df_all = pd.concat([df_boys, df_girls])

    def num_to_int(num):
        if num == "..":
            return 0
        return int(num)
    df_all.num = df_all.num.apply(num_to_int)
    df_all.year = df_all.year.apply(num_to_int)

    name_std = []

    for name in df_all.name.unique():
        years, frac, top_year = year_span_for_name(df_all, name, 0.33)
        span_length = len(years)
        std = std_for_name(df_all, name)
        name_std.append({"name": name,
                        "std": std,
                        "span_03": span_length,
                        "min_year": min(years),
                        "max_year": max(years),
                        "top_year": top_year,
                        "frac": frac
                        })
    df_name_std = pd.DataFrame(name_std)
    df_name_std.to_csv("data/names_with_year_spans.csv")