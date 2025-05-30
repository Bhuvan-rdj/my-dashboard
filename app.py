import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import zipfile
import base64
from datetime import datetime

# Configure app
st.set_page_config(page_title="Multi-Graph Visualizer", layout="wide")
st.title("📊 Multi-Graph Visualizer with Download Selected")

# Initialize session state
if "all_plots" not in st.session_state:
    st.session_state.all_plots = {}
if "selected_plots" not in st.session_state:
    st.session_state.selected_plots = set()
if "show_graph_collection" not in st.session_state:
    st.session_state.show_graph_collection = False

# File uploader
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if not numeric_cols:
            st.warning("No numeric columns found!")
        else:
            st.markdown('<h3 style="text-align: center;">Controls</h3>', unsafe_allow_html=True)

            # Graph type selection (centered)
            r_col1, r_col2, r_col3 = st.columns([1, 2, 1])
            with r_col2:
                graph_type = st.radio(
                    "Choose graph type:",
                    ["Histogram", "Boxplot", "Scatter", "Line", "Bar"],
                    horizontal=True
                )

            # X-axis selection as buttons
            x_axis = st.radio("Select X-axis column:", numeric_cols, horizontal=True)

            y_axis = None
            if graph_type in ["Scatter", "Line", "Bar"]:
                possible_y = [col for col in numeric_cols if col != x_axis]
                if possible_y:
                    y_axis = st.radio("Select Y-axis column:", possible_y, horizontal=True)
                else:
                    st.warning("No other numeric columns available for Y-axis.")

            if graph_type == "Histogram":
                bins = st.slider("Bins", 5, 50, 20)

            # Add graph button
            if st.button("Add This Graph to Collection"):
                fig, ax = plt.subplots()
                if graph_type == "Histogram":
                    sns.histplot(df[x_axis], bins=bins, kde=True)
                    title = f"Histogram of {x_axis}"
                elif graph_type == "Boxplot":
                    sns.boxplot(df[x_axis])
                    title = f"Boxplot of {x_axis}"
                elif graph_type == "Scatter":
                    sns.scatterplot(data=df, x=x_axis, y=y_axis)
                    title = f"Scatter {x_axis} vs {y_axis}"
                elif graph_type == "Line":
                    sns.lineplot(data=df, x=x_axis, y=y_axis)
                    title = f"Line {y_axis} over {x_axis}"
                elif graph_type == "Bar":
                    if y_axis:
                        df.groupby(x_axis)[y_axis].mean().plot(kind='bar')
                        title = f"Bar chart of {y_axis} by {x_axis}"
                    else:
                        df[x_axis].value_counts().plot(kind='bar')
                        title = f"Bar chart of {x_axis}"

                plt.title(title)
                buf = BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                plt.close()

                unique_title = f"{title} ({datetime.now().strftime('%H-%M-%S')})"
                st.session_state.all_plots[unique_title] = buf.getvalue()
                st.success(f"Added {unique_title} to collection! Total graphs: {len(st.session_state.all_plots)}")

            # Current Graph Preview
            st.subheader("Current Graph Preview")
            fig, ax = plt.subplots()
            if graph_type == "Histogram":
                sns.histplot(df[x_axis], bins=bins, kde=True)
                plt.title(f"Histogram of {x_axis} (Preview)")
            elif graph_type == "Boxplot":
                sns.boxplot(df[x_axis])
                plt.title(f"Boxplot of {x_axis} (Preview)")
            elif graph_type == "Scatter":
                sns.scatterplot(data=df, x=x_axis, y=y_axis)
                plt.title(f"Scatter {x_axis} vs {y_axis} (Preview)")
            elif graph_type == "Line":
                sns.lineplot(data=df, x=x_axis, y=y_axis)
                plt.title(f"Line {y_axis} over {x_axis} (Preview)")
            elif graph_type == "Bar":
                if y_axis:
                    df.groupby(x_axis)[y_axis].mean().plot(kind='bar')
                    plt.title(f"Bar chart of {y_axis} by {x_axis} (Preview)")
                else:
                    df[x_axis].value_counts().plot(kind='bar')
                    plt.title(f"Bar chart of {x_axis} (Preview)")

            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close()

            cols = st.columns(3)
            cols[1].image(buf.getvalue(), use_column_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

# Toggle graph collection visibility
if st.button("Graphs"):
    st.session_state.show_graph_collection = not st.session_state.show_graph_collection

# Display graph collection with selection
if st.session_state.show_graph_collection and st.session_state.all_plots:
    st.subheader("Graph Collection")

    # Select All checkbox
    select_all = st.checkbox(
        "Select All Graphs",
        value=len(st.session_state.selected_plots) == len(st.session_state.all_plots),
        key="select_all_checkbox"
    )
    if select_all:
        st.session_state.selected_plots = set(st.session_state.all_plots.keys())
    else:
        if len(st.session_state.selected_plots) == len(st.session_state.all_plots):
            st.session_state.selected_plots = set()

    # Individual graph selection
    for title, plot_data in st.session_state.all_plots.items():
        checked = title in st.session_state.selected_plots
        new_checked = st.checkbox(title, value=checked, key=f"chk_{title}")
        if new_checked and not checked:
            st.session_state.selected_plots.add(title)
        elif not new_checked and checked:
            st.session_state.selected_plots.discard(title)

    # Show selected graph previews in columns
    if st.session_state.selected_plots:
        st.write("### Selected Graph Previews")
        selected = list(st.session_state.selected_plots)
        cols = st.columns(3)
        for i, title in enumerate(selected):
            cols[i % 3].image(st.session_state.all_plots[title], caption=title, use_column_width=True)
    else:
        st.info("No graphs selected.")

    # Download selected graphs as ZIP
    if st.session_state.selected_plots and st.button("Download Selected Graphs as ZIP"):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
            for title in st.session_state.selected_plots:
                zip_file.writestr(f"{title}.png", st.session_state.all_plots[title])
        zip_buffer.seek(0)
        b64 = base64.b64encode(zip_buffer.read()).decode()
        href = f'<a href="data:application/zip;base64,{b64}" download="selected_graphs.zip">Download Selected Graphs ZIP</a>'
        st.markdown(href, unsafe_allow_html=True)

    # Clear graph collection button
    if st.button("Clear Graph Collection"):
        st.session_state.all_plots.clear()
        st.session_state.selected_plots.clear()
        st.success("Graph collection cleared!")
