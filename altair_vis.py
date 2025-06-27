from common import get_annual_measles_data_with_per_population_change
import altair as alt

data = get_annual_measles_data_with_per_population_change()
regions = list(data["region"].unique())
data.reset_index(inplace=True, drop=True)

# Search box for country name
search_box = alt.param(
    name="country_search",
    value="",
    bind=alt.binding(input="search", placeholder="Country", name="Search "),
)
search_matches = alt.expr.test(alt.expr.regexp(search_box, "i"), alt.datum.country)

c = (
    alt.Chart(data)
    .mark_line(point=True)
    .encode(
        x=alt.X("year").title("Year"),
        y=alt.Y("change_per_population_percent").title(
            "Percentage Change in Measles Cases per Population"
        ),
        color=alt.Color("country:N").title("Country"),
        tooltip=["country", "measles_total", "previous_measles", "year"],
    )
)

region_dropdown = alt.binding_select(
    options=[None] + regions, labels=["All"] + regions, name="Region"
)
region_select = alt.selection_point(fields=["region"], bind=region_dropdown)

filter_genres = (
    c.add_params(region_select, search_box)
    .transform_filter(region_select)
    .transform_filter(
        alt.expr.test(alt.expr.regexp(search_box, "i"), alt.datum.country)
    )
)
final = (
    filter_genres.properties(
        title=alt.TitleParams(
            [
                "* South Sudan changed region to Africa in 2014. For the purposes of this plot all of those points will appear in that region."
            ],
            baseline="bottom",
            orient="bottom",
            anchor="start",
            fontWeight="normal",
            fontSize=10,
            dy=20,
            dx=20,
        ),
    )
).properties(
    width="container",
    height=600,
    title=[
        "Annual Change in Measles Cases per Population by Country (2012-2024)",
    ],
)
final.save("altair_vis.html")
