# app.py -- Main python application

#Import Streamlit to create the web dashboard.
import streamlit as st 

#Import Pandas to read and analyze tabular data. 
import pandas as pd

#Import Plotly Express to create interactive charts. 
import plotly.express as px 

# Set the browser tab title and dashboard layout. 
st.set_page_config(
    page_title="CSV Insight Studio",
    page_icon="📊",
    layout="wide"
)

#Display the main heading and a short description. 
st.title("📊 CSV Insight Studio")
st.write(
    "Upload a CSV file to explore your data, "
    "check data quality, and create interactive charts."
)

#Let the user upload a CSV file from their computer. 
uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type={"csv"}
)


#Use the uploaded dataset if available. 
#Otherwise, load our sample file for demonstration. 
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as error:
        st.error(f"Could not read the CSV file: {error}")
        st.stop()
else:
    #skip the first comment line and read the actual CSV header. 
    df = pd.read_csv("sample_sales.csv", comment="#")
    st.info("Showing sample data. Upload your own CSV to explore it.")

# Stop the dashboard if the file has no rows or columns. 
if df.empty or len(df.columns) == 0:
    st.warning("The uploaded dataset is empty.")
    st.stop()

# Create tabs to organize the dashboard. 
overview_tab, explore_tab, quality_tab = st.tabs(
    ["Overview", "Explore Charts", "Data Quality"]
)


#------------------------OVERVIEW TAB----------------------------

with overview_tab:

    #Dispaly important dataset metrics as KPI cards. 
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Rows", f"{df.shape[0]:,}")
    col2.metric("Total Columns", f"{df.shape[1]:,}")
    col3.metric(
        "Missing Values",
        f"{int(df.isna().sum().sum()):,}"
    )

    # Show a preview so users can inspect the dataset. 
    st.subheader("Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True)

    # Calculate descriptive statistics for numeric columns. 
    st.subheader("Numerical Summary")
    numeric_df = df.select_dtypes(include="number")

    if not numeric_df.empty:
        st.dataframe(
            numeric_df.describe().round(2),
            use_container_width=True 
        )
    else:
        st.write("No numerial columns were found.")


#------------------------- EXPLORE CHARTS TAB--------------------

with explore_tab:

    st.subheader("Create an Interactive Chart")

    # Get the available column names from the dataset. 
    all_columns = df.columns.tolist()

    # Identify numerical columns for charts that need numbers. 
    numeric_columns = numeric_df.columns.tolist()

    # Let the user choose which chart to create. 
    chart_type = st.selectbox(
        "Select chart type",
        ["Bar", "Line", "Scatter", "Histogram"]
    )

    #Allow users to choose the columns for visualization. 
    x_column = st.selectbox(
        "Select X-axis column",
        all_columns 
    )

    # Histograms need only numerical column. 
    if chart_type == "Histogram":

        if x_column in numeric_columns:
            fig = px.histogram(
                df,
                x=x_column,
                title=f"Distribution of {x_column}"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Choose a numerical column for a hsitogram.")

    # Bar, line, and scatter charts use both X and Y. 
    elif numeric_columns:

        y_column = st.selectbox(
            "Select Y-axis numerical column",
            numeric_columns 
        )

        if chart_type == "Bar":
            fig = px.bar(
                df,
                x=x_column,
                y=y_column,
                title=f"{y_column} by {x_column}"
            )
        
        elif chart_type == "Line":
            fig = px.line(
                df,
                x=x_column,
                y=y_column,
                title=f"{y_column} across {x_column}"
            )

        else:
            fig = px.scatter(
                df,
                x=x_column,
                y=y_column,
                title=f"{y_column} vs {x_column}"
            )

        #Render the interactive Plotly chart in Streamlit. 
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("This dataset has no numerical columns.")


#--------------------------DATA QUALITY TAB-----------------------------\

with quality_tab:

    st.subheader("Missing Values by Column")

    # Count missing cells in every column.
    missing_counts = df.isna().sum()

    #Convert the counts into a table for display. 
    missing_report = pd.DataFrame({
        "Column": missing_counts.index,
        "Missing Values": missing_counts.values,
        "Missing Percentage": (
            missing_counts.values / len(df) * 100
        ).round(2)
    })

    st.dataframe(
        missing_report,
        use_container_width=True 
    )

    # Identify exact duplicate rows. 
    duplicate_count = int(df.duplicated().sum())

    st.metric("Duplicate Rows", duplicate_count)

    # Offer downloadable report of the dataset's missing values. 
    csv_report = missing_report.to_csv(index=False)

    st.download_button(
        label="Download Missing Values Report",
        data=csv_report,
        file_name="missing_values_report.csv",
        mime="text/csv"
    )

    # Show a correlation heatmap if two r more numeric columns exist.
    if len(numeric_columns) >= 2:

        st.subheader("Numerical Correlation")

        correlation = numeric_df.corr()

        fig = px.imshow(
            correlation,
            text_auto=".2f",
            aspect="auto",
            title="Correlation Heatmap"
        )

        st.plotly_chart(fig, use_container_width=True)


    else:
        st.write(
            "A correlation heatmap requires at least "
            "two numerical columns."
        )