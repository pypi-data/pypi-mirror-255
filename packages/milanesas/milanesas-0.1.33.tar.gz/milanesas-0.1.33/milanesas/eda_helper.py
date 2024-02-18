import itertools
import pandas as pd
import random
import matplotlib.pyplot as plt
import numpy as np


def random_hex():
    # List of dark Material colors
    dark_material_colors = [
        "#121212",
        "#1E88E5",
        "#00897B",
        "#39BBB0",
        "#26C6DA",
        "#42A5F5",
        "#64B5F6",
        "#9C27B0",
        "#E91E63",
        "#F44336",
        "#D81B60",
        "#880E4F",
    ]

    # Choose a random color from the list
    random_color = random.choice(dark_material_colors)

    return random_color


def replace_column_content(df, col, repl):
    """Replaces values in a DataFrame column using a replacement dictionary.

    Modifies a DataFrame column in-place by replacing values based on a
    provided dictionary. The replacement dictionary maps original values to
    their desired replacements. Regular expressions can be used for flexible
    matching.

    Args:
        df (pandas.DataFrame): The DataFrame to modify.
        col (str): The name of the column to modify.
        repl (dict): A dictionary containing replacement mappings, where keys
            represent original values and values represent their replacements.

    Raises:
        ValueError: If the specified column does not exist in the DataFrame.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'genero': ['HOMBRE', 'MUJER', 'NO COMPARTO']})
        >>> gen_repl = {
        ...     "HOMBRE": "MAN",
        ...     "MUJER": "WOMAN",
        ...     "NO COMPARTO": "DONT SHARE",
        ... }
        >>> replace_column_content(df, "genero", gen_repl)
        >>> print(df)  # Output:
                       genero
        0                 MAN
        1              WOMAN
        2       DONT SHARE
    """

    df[col].replace(
        repl,
        regex=True,
        inplace=True,
    )


def get_percentage(value):
    """Formats a value as a percentage string.

    Converts a numerical value into a percentage representation, rounded to the
    nearest integer, and returns it as a formatted string with a percentage sign.

    Args:
        value (float): The numerical value to convert to a percentage.

    Returns:
        str: The formatted percentage string (e.g., "42%").

    Example:
        >>> percentage_string = get_percentage(0.4235)
        >>> print(percentage_string)  # Output: "42%"
    """
    # Multiply the value by 100 to get the percentage.
    percentage = value * 100

    # Round the percentage to the nearest integer value.
    percentage = round(percentage)

    return f"{percentage}%"


def percentage_to_normal(val):
    """Formats a Series of percentage values with rounding and percentage sign.

    Converts a Series of values to percentages, rounds them to one decimal place,
    and adds a percentage sign. The output is formatted as a string.

    Args:
        val (pandas.Series): A Series containing numerical values.

    Returns:
        pandas.Series: A Series with the same index as the input, but containing
        formatted percentage strings.

    Example:
        >>> import pandas as pd
        >>> s = pd.Series([0.1234, 0.5678, 0.9012])
        >>> formatted_percentages = percentage_to_normal(s)
        >>> print(formatted_percentages)
        0    12.3 %
        1    56.8 %
        2    90.1 %
        dtype: object
    """

    return val.mul(100).round(1).astype(str) + " %"


def explode_pie(pie_size):
    """Generates a list of values to explode slices of a pie chart.

    Creates a list of random values between 0.01 and 0.05, suitable for
    visually exploding slices of a pie chart. The number of values in the
    list is determined by the `pie_size` argument.

    Args:
        pie_size: An integer representing the number of slices in the pie chart.

    Returns:
        A list of floating-point values between 0.01 and 0.05, with a length
        equal to `pie_size`.

    Example:
        >>> import pandas as pd
        >>> imp_df = pd.DataFrame({'A': [10, 20, 30]})
        >>> explode_values = explode_pie(imp_df.size)
        >>> print(explode_values)  # Example output: [0.03546542, 0.01237543, 0.04892357]
    """
    exp = [random.uniform(0.01, 0.05) for i in range(0, pie_size)]
    return exp


def get_column_uniques(df, col):
    """Prints unique values in a DataFrame column, handling semicolon-separated lists.

    Prints the unique values found within a specified column of a DataFrame.
    Treats semicolon-separated values within cells as individual elements.

    Args:
        df (pandas.DataFrame): The DataFrame to analyze.
        col (str): The name of the column to extract unique values from.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'exp_en_IT': ['A;B;C', 'A;B', 'D']})
        >>> print_column_uniques(df, "exp_en_IT")
        {'A', 'B', 'C', 'D'}
    """

    return list(
        set(itertools.chain.from_iterable([i.split(";") for i in df[col].dropna()]))
    )


def print_column_uniques(df, col):
    print(set(itertools.chain.from_iterable([i.split(";") for i in df[col]])))


def make_dataframe(df, col, cat_col, count_col):
    # Drop all rows with float values from the DataFrame.
    df = df.dropna(subset=[col])

    # Get all unique categories in the column.
    categories = set(
        itertools.chain.from_iterable([i.split(";") for i in df[col].values])
    )

    # Create a dictionary to store the category counts.
    category_counts = {}
    for category in categories:
        category_counts[category] = df[df[col].str.contains(category)].shape[0]

    # Create a new DataFrame from the category counts dictionary.
    new_df = pd.DataFrame(data=category_counts.items(), columns=[cat_col, count_col])

    return new_df


def make_df(df, col, x_label, y_label):
    """Creates a DataFrame counting occurrences of unique values (including those within semicolon-separated lists).

    Constructs a new DataFrame that tallies the number of occurrences of each unique
    value within a specified column of a given DataFrame. Handles cases where cells
    contain multiple values separated by semicolons.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        col (str): The name of the column to analyze.
        x_label (str): The label for the column containing unique values in the output DataFrame.
        y_label (str): The label for the column containing counts in the output DataFrame.

    Returns:
        pandas.DataFrame: A new DataFrame with two columns:
            - x_label: Contains the unique values from the specified column.
            - y_label: Contains the counts of those values.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'educacion': ['A;B', 'A', 'C;B', 'D']})
        >>> new_df = make_df(df, "educacion", "categories", "count")
        >>> print(new_df)
       categories  count
        0          A      2
        1          B      2
        2          C      1
        3          D      1
    """

    c = set(
        itertools.chain.from_iterable(
            [i.split(";") for i in df[col].value_counts().keys()]
        )
    )
    cats = {i: 0 for i in c}
    for i in c:
        df[col] = df[col].fillna(False)
        cats[i] = df[df[col].str.contains(i)].shape[0]

    df = pd.DataFrame(
        data=[i for i in cats.items()],
        columns=[x_label.replace(" ", ""), y_label.replace(" ", "")],
    )  # .set_index(x_label.replace(' ',''))

    return df


def get_normal_uniques_col_count(df, col):
    """Counts occurrences of unique values (including those within semicolon-separated lists), normalizing counts by row count.

    Calculates the count of each unique value within a specified column of a DataFrame,
    handling cases where cells contain multiple values separated by semicolons. Normalizes
    the counts by dividing them by the total number of rows in the DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        col (str): The name of the column to analyze.

    Returns:
        dict: A dictionary where keys represent unique values from the column and values
            represent their normalized counts (fraction of total rows).

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'educacion': ['A;B', 'A', 'A;C', 'B']})
        >>> normalized_counts = get_normal_uniques_col_count(df, "educacion")
        >>> print(normalized_counts)
        {'A': 0.75, 'B': 0.5, 'C': 0.25}
    """

    c = set(
        itertools.chain.from_iterable(
            [i.split(";") for i in df[col].value_counts(normalize=True).keys()]
        )
    )
    cats = {i: 0 for i in c}
    for i in c:
        cats[i] = df[df[col].str.contains(i)].shape[0]

    return cats


def get_uniques_col_count(df, col):
    """Counts occurrences of unique values (including those within semicolon-separated lists).

    Calculates the count of each unique value within a specified column of a DataFrame,
    handling cases where cells contain multiple values separated by semicolons.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        col (str): The name of the column to analyze.

    Returns:
        dict: A dictionary where keys represent unique values from the column and values
            represent their counts.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'educacion': ['A;B', 'A', 'A;C', 'B']})
        >>> counts = get_uniques_col_count(df, "educacion")
        >>> print(counts)
        {'A': 3, 'B': 2, 'C': 1}
    """
    c = set(
        itertools.chain.from_iterable(
            [i.split(";") for i in df[col].value_counts().keys()]
        )
    )
    cats = {i: 0 for i in c}
    for i in c:
        cats[i] = df[df[col].str.contains(i)].shape[0]

    return cats


def make_vertical_grouped_chart(df, g1, g2, col, labels, config):
    """Creates a vertical grouped bar chart comparing values between two groups.

    Generates a vertical bar chart with two sets of bars, one for each group
    (g1 and g2), comparing their counts for unique values in a specified column.
    Labels, title, and other chart elements are customized using a configuration
    dictionary.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        g1 (pandas.DataFrame): A subset of the DataFrame representing the first group.
        g2 (pandas.DataFrame): A subset of the DataFrame representing the second group.
        col (str): The name of the column to compare values for.
        labels (list): A list of unique values from the column to use as labels.
        config (dict): A configuration dictionary with keys:
            - title (str): The title of the chart.
            - c1_label (str): The label for the first group's bars.
            - c2_label (str): The label for the second group's bars.
            - xlabel (str): The label for the x-axis.
            - ylabel (str): The label for the y-axis.

    Raises:
        ValueError: If the specified column does not exist in the DataFrame.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'edad_actual': [25, 30, 30, 25, 35], 'gender': ['MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN']})
        >>> gen = df.groupby('gender')
        >>> group_config = {
        ...     'title': "edad_actual by Gender",
        ...     'c1_label': "Hombres",
        ...     'c2_label': "Mujeres",
        ...     'xlabel': "edad_actual level",
        ...     'ylabel': "Count"
        ... }
        >>> make_vertical_grouped_chart(df, gen.get_group("MAN"), gen.get_group("WOMAN"), "edad_actual", df["edad_actual"].unique(), group_config)
    """

    g1_count = get_uniques_col_count(g1, col)
    g2_count = get_uniques_col_count(g2, col)
    labels = get_column_uniques(df, col)

    # Values
    g1_val = [g1_count.get(i, 0) for i in labels]
    g2_val = [g2_count.get(i, 0) for i in labels]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, g1_val, width, label=config.get("c1_label", ""))
    rects2 = ax.bar(x + width / 2, g2_val, width, label=config.get("c2_label", ""))

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(config.get("ylabel", ""))
    ax.set_title(config.get("title", ""))
    ax.set_xlabel(config.get("xlabel", ""))
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()

            ax.annotate(
                "{}".format(height),
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha="center",
                va="bottom",
            )

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()

    plt.show()


def make_horizontal_grouped_chart(df, g1, g2, col, labels, config):
    """Creates a horizontal grouped bar chart comparing values between two groups.

    Generates a horizontal bar chart with two sets of bars, one for each group
    (g1 and g2), comparing their counts for unique values in a specified column.
    Labels, title, and other chart elements are customized using a configuration
    dictionary.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        g1 (pandas.DataFrame): A subset of the DataFrame representing the first group.
        g2 (pandas.DataFrame): A subset of the DataFrame representing the second group.
        col (str): The name of the column to compare values for.
        labels (list): A list of unique values from the column to use as labels.
        config (dict): A configuration dictionary with keys:
            - title (str): The title of the chart.
            - c1_label (str): The label for the first group's bars.
            - c2_label (str): The label for the second group's bars.
            - xlabel (str): The label for the x-axis.
            - ylabel (str): The label for the y-axis.

    Raises:
        ValueError: If the specified column does not exist in the DataFrame.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'exp_en_IT': ['A', 'B', 'A', 'C', 'B'], 'gender': ['MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN']})
        >>> gen = df.groupby('gender')
        >>> group_config = {
        ...     'title': "exp_en_IT by Gender",
        ...     'c1_label': "MAN",
        ...     'c2_label': "WOMAN",
        ...     'xlabel': "Count",
        ...     'ylabel': "exp_en_IT level"
        ... }
        >>> make_horizontal_grouped_chart(df, gen.get_group("MAN"), gen.get_group("WOMAN"), "exp_en_IT", df["exp_en_IT"].unique(), group_config)
    """
    g1_count = get_uniques_col_count(g1, col)
    g2_count = get_uniques_col_count(g2, col)
    labels = get_column_uniques(df, col)

    # Values
    g1_val = [g1_count.get(i, 0) for i in labels]
    g2_val = [g2_count.get(i, 0) for i in labels]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.barh(x - width / 2, g1_val, width, label=config.get("c1_label", ""))
    rects2 = ax.barh(x + width / 2, g2_val, width, label=config.get("c2_label", ""))

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(config.get("xlabel", ""))
    ax.set_title(config.get("title", ""))
    ax.set_xlabel(config.get("ylabel", ""))
    ax.set_yticks(x)
    ax.set_yticklabels(labels)
    ax.legend()

    for k, v in enumerate(rects1):
        height = v.get_height()

        if len(labels) >= 10:
            # Set the position of the annotation text
            x_pos = v.get_x() + v.get_width() + 1.5
        else:
            # Set the position of the annotation text
            x_pos = v.get_x() + v.get_width() + 1

        # x_pos = v.get_x() + v.get_width() / 2
        y_pos = v.get_y() - height * 0.5
        # y_pos = v.get_y() + height

        # Add the annotation text
        if int(g1_val[k]) != 0:
            # x_pos = v.get_x() + v.get_width()
            # ax.annotate(str(g1_val[k]), (x_pos, y_pos), ha='center', va='bottom')
            ax.annotate("  " + str(g1_val[k]), (x_pos, y_pos), ha="center", va="bottom")

    for k, v in enumerate(rects2):
        height = v.get_height()

        # Set the position of the annotation text
        # x_pos = v.get_x() + v.get_width()+1

        if len(labels) >= 10:
            # Set the position of the annotation text
            x_pos = v.get_x() + v.get_width() + 1
        else:
            # Set the position of the annotation text
            x_pos = v.get_x() + v.get_width() + 0.5

        # x_pos = v.get_x() + v.get_width() + 5
        # x_pos = v.get_x() + v.get_width() / 2
        y_pos = v.get_y() - height * 0.05 - 0.05
        # y_pos = v.get_y() + height

        # Add the annotation text
        if int(g2_val[k]) != 0:
            # ax.annotate(str(g2_val[k]), (x_pos, y_pos), ha='center', va='bottom')
            ax.annotate("  " + str(g2_val[k]), (x_pos, y_pos), ha="center", va="bottom")

    fig.tight_layout()
    plt.show()


def make_normalized_df(df, col):
    """Creates a DataFrame with normalized counts of unique values, handling semicolon-separated lists.

    Constructs a new DataFrame that displays the percentage of occurrences for each unique
    value within a specified column of a given DataFrame. Values in cells can be separated
    by semicolons, and each unique value within a semicolon-separated list is counted
    separately.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        col (str): The name of the column to analyze.

    Returns:
        pandas.DataFrame: A new DataFrame with two columns:
            - categories: Contains the unique values from the specified column.
            - total count: Contains the percentage of occurrences for each unique value.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'imp_ed_formal': ['A;B', 'A', 'C;B', 'A;B']})
        >>> normalized_counts = make_normalized_df(df, "imp_ed_formal")
        >>> print(normalized_counts)
              total count
        categories
        A           50.0
        B           50.0
        C           25.0
    """
    # Split each row content by ";"
    df_split = df[col].str.split(";").explode()

    # Count how many times each unique value appears in the column
    df_counts = df_split.value_counts().reset_index(name="total count")

    # Calculate the percentage of times each category appears in the column
    df_counts["total count"] = (
        df_counts["total count"] / df_counts["total count"].sum() * 100
    )

    # Rename the columns
    df_counts.columns = ["categories", "total count"]

    # Set the index to the 'categories' column
    df_counts = df_counts.set_index("categories")

    return df_counts


def make_horizontal_bar(df, col, titulo, x_label, y_label, legend):
    """Creates a horizontal bar chart for a specified column in a DataFrame.

    Generates a horizontal bar chart that visualizes the counts of unique values
    within a given column of a DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        col (str): The name of the column to visualize.
        titulo (str): The title of the chart.
        x_label (str): The label for the x-axis.
        y_label (str): The label for the y-axis.
        legend (bool): True to display a legend, False to hide it.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'carr_especialidades': ['A', 'B', 'A', 'C', 'B']})
        >>> make_horizontal_bar(df, "carr_especialidades", "Carreras o especialidades", "Total", "Carreras / Especialidades", False)
    """
    # Making a plot for this column.
    fig = plt.figure(figsize=(9, 5))

    aux_df = make_df(df, col, "categorias", "conteo")

    aux_df_plot = aux_df.plot(kind="barh", title=f"{titulo} \n", legend=legend)

    aux_df_column_uniques = get_column_uniques(df, col)

    aux_df_plot.set_yticks(
        [k for k, v in enumerate(aux_df_column_uniques)], minor=False
    )

    aux_df_plot.set_yticklabels(
        [i for i in aux_df_column_uniques],
        fontdict=None,
        minor=False,
    )

    aux_df_plot.set_xlabel(f"{x_label}")
    aux_df_plot.set_ylabel(f"{y_label}")

    cat_values = [i for i in aux_df.conteo.value_counts().keys()]

    # Plot annotations.
    for k, v in enumerate(cat_values):
        aux_df_plot.annotate(v, (v, k), va="center")

        # nv_ed_plot.annotate(v, (v,k),va='center')

    plt.show()


def make_custom_horizontal_bar(df, col, titulo, x_label, y_label, legend):
    """Creates a horizontal bar chart from a pre-formatted DataFrame.

    Generates a horizontal bar chart from a DataFrame that's already been prepared
    with specific column names ("Category" for categories and "count" for values).

    Args:
        df (pandas.DataFrame): The input DataFrame, containing a 'Category' column
                                and a 'count' column.
        col (str): Unused in this function, but kept for consistency with other
                    charting functions.
        titulo (str): The title of the chart.
        x_label (str): The label for the x-axis.
        y_label (str): The label for the y-axis.
        legend (bool): True to display a legend, False to hide it.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Category': ['A', 'B', 'A', 'C'], 'count': [4, 2, 3, 1]})
        >>> make_custom_horizontal_bar(df, "col", "Carreras o especialidades", "Total", "Carreras / Especialidades", False)
    """
    # Making a plot for this column.
    fig = plt.figure(figsize=(9, 5))

    # aux_df = make_df(df, col, "categorias", "conteo")

    aux_df_plot = df.plot(kind="barh", title=f"{titulo} \n", legend=legend)

    aux_df_column_uniques = get_column_uniques(df, "Category")

    aux_df_plot.set_yticks(
        [k for k, v in enumerate(aux_df_column_uniques)], minor=False
    )

    aux_df_plot.set_yticklabels(
        [i for i in aux_df_column_uniques],
        fontdict=None,
        minor=False,
    )

    aux_df_plot.set_xlabel(f"{x_label}")
    aux_df_plot.set_ylabel(f"{y_label}")

    cat_values = [i for i in df["count"].value_counts().keys()]

    # Plot annotations.
    for k, v in enumerate(cat_values):
        aux_df_plot.annotate(v, (v, k), va="center")

        # nv_ed_plot.annotate(v, (v,k),va='center')

    plt.show()
