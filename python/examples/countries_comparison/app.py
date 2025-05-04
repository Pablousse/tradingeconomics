import pandas as pd
import plotly.express as px
import tradingeconomics as te
from flask import Flask, render_template, request

app = Flask(__name__)

CATEGORIES = [
    "GDP Growth Rate",
    "GDP Annual Growth Rate ",
    "Unemployment Rate",
    "Inflation Rate",
    "Interest Rate",
    "Manufacturing PMI",
    "Non Manufacturing PMI",
    "Services PMI",
]


def get_plot(country: str, second_country: str = ""):
    """
    Return a plot of the one or two countries' interest rate
    Args:
        country: string.
        second_country: string.
    """
    # Loging in the API
    te.login("e05eb96d7d4444e:xuqp4jtyp2r6txu")

    # Retrieving the data
    data = te.getHistoricalData(
        country=country, indicator="Interest Rate", output_type="raw"
    )

    # Formating the data into a dataframe
    df = pd.DataFrame(data)
    df = df.iloc[1:]

    if second_country != "":
        data_second_country = te.getHistoricalData(
            country=second_country, indicator="Interest Rate", output_type="raw"
        )
        df_second_country = pd.DataFrame(data_second_country)
        df_second_country = df_second_country.iloc[1:]
        df = pd.concat([df, df_second_country], ignore_index=True)

    # Plotting the data
    fig = px.line(df, x="DateTime", y="Value", color="Country")
    html_plot = fig.to_html(full_html=False)

    return html_plot


def get_country_data(country: str):
    """
    Return the datas of the selected country
    Args:
        country: string.
    """
    # Loging in the API
    te.login("e05eb96d7d4444e:xuqp4jtyp2r6txu")

    # Retrieving the data
    data = te.getIndicatorData(country=country)

    new_list = {x["Category"]: x for x in data if x["Category"] in CATEGORIES}

    return new_list


def get_country_table(country: str):
    """
    Return a table filled with the selected country indicators
    Args:
        country: string.
    """

    html = """<table>
    <tr>
        <th>Category</th>
        <th>Previous Value</th>
        <th>Latest Value</th>
        <th>Difference</th>
    </tr>
    """
    data = get_country_data(country)
    for category in CATEGORIES:
        html += "<tr>"
        html += f"<td>{category}</td>"
        if category in data:
            html += f"<td>{data[category]["PreviousValue"]}</td>"
            html += f"<td>{data[category]["LatestValue"]}</td>"
            html += f"<td>{data[category]["LatestValue"] - data[category]["PreviousValue"]}</td>"
        else:
            html += "<td>No value</td><td>No value</td><td>No value</td>"

        html += "</tr>"

    html += "</table>"
    return html


@app.route("/")
def index():
    countries = ["Mexico", "New Zealand", "Sweden", "Thailand"]

    return render_template("index.html", countries=countries)


@app.route("/country-changed", methods=["POST"])
def country_changed():
    """
    Refresh the plot to use the new country selected and return a table with the country's indicators
    """
    selected_country = request.form.get(request.headers.environ["HTTP_HX_TRIGGER_NAME"])
    first_country = request.form.get("first-country")
    second_country = request.form.get("second-country")
    html_plot = get_plot(first_country, second_country)

    table = get_country_table(selected_country)

    html = f"""{table}
    <div id="image-container" hx-swap-oob="true">{html_plot}</div>"""

    return html


# Main Driver Function
if __name__ == "__main__":
    # Run the application on the local development server
    app.run(debug=True)
