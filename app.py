import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO

# Config
st.set_page_config(page_title="📊 Multi-Plot Generator", layout="centered")
st.title("📈 Custom Data Plot Generator")
st.markdown("Upload your dataset, choose multiple plots, customize inputs, and download each figure as needed.")

# Upload
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

# Load and explore data
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File loaded successfully!")
        st.dataframe(df.head())

        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        all_cols = df.columns.tolist()

        if not all_cols:
            st.warning("No usable columns found in the uploaded dataset.")
        else:
            st.markdown("### 📌 Select plot types")
            plot_types = st.multiselect(
                "Choose the plots you want to generate:",
                [
                    "Histogram", "Box Plot", "Violin Plot",
                    "Scatter Plot", "Line Plot", "Bar Plot",
                    "Heatmap", "Pairplot", "Countplot"
                ]
            )

            # Helper: Save figure to buffer
            def save_fig(fig):
                buf = BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight")
                buf.seek(0)
                return buf

            # Generate plots
            for plot_type in plot_types:
                st.markdown(f"---\n### 📊 {plot_type}")
                fig = None

                if plot_type == "Histogram":
                    col = st.selectbox(f"[{plot_type}] Select column:", numeric_cols, key=f"{plot_type}-col")
                    fig, ax = plt.subplots()
                    ax.hist(df[col], bins=20, color='skyblue', edgecolor='black')
                    ax.set_title(f"{col} Histogram")
                    ax.set_xlabel(col)
                    ax.set_ylabel("Frequency")
                    st.pyplot(fig)

                elif plot_type == "Box Plot":
                    y = st.selectbox(f"[{plot_type}] Y-axis (numeric):", numeric_cols, key=f"{plot_type}-y")
                    x = st.selectbox(f"[{plot_type}] Group by (categorical):", ["None"] + categorical_cols, key=f"{plot_type}-x")
                    fig, ax = plt.subplots()
                    sns.boxplot(data=df, x=x if x != "None" else None, y=y, ax=ax)
                    st.pyplot(fig)

                elif plot_type == "Violin Plot":
                    y = st.selectbox(f"[{plot_type}] Y-axis (numeric):", numeric_cols, key=f"{plot_type}-y")
                    x = st.selectbox(f"[{plot_type}] Group by (categorical):", ["None"] + categorical_cols, key=f"{plot_type}-x")
                    fig, ax = plt.subplots()
                    sns.violinplot(data=df, x=x if x != "None" else None, y=y, ax=ax)
                    st.pyplot(fig)

                elif plot_type == "Scatter Plot":
                    x = st.selectbox(f"[{plot_type}] X-axis:", numeric_cols, key=f"{plot_type}-x")
                    y = st.selectbox(f"[{plot_type}] Y-axis:", numeric_cols, key=f"{plot_type}-y")
                    hue = st.selectbox(f"[{plot_type}] Hue (optional):", ["None"] + categorical_cols, key=f"{plot_type}-hue")
                    fig, ax = plt.subplots()
                    sns.scatterplot(data=df, x=x, y=y, hue=hue if hue != "None" else None, ax=ax)
                    st.pyplot(fig)

                elif plot_type == "Line Plot":
                    x = st.selectbox(f"[{plot_type}] X-axis:", numeric_cols, key=f"{plot_type}-x")
                    y = st.selectbox(f"[{plot_type}] Y-axis:", numeric_cols, key=f"{plot_type}-y")
                    fig, ax = plt.subplots()
                    sns.lineplot(data=df, x=x, y=y, ax=ax)
                    st.pyplot(fig)

                elif plot_type == "Bar Plot":
                    x = st.selectbox(f"[{plot_type}] X-axis (categorical):", categorical_cols, key=f"{plot_type}-x")
                    y = st.selectbox(f"[{plot_type}] Y-axis (numeric):", numeric_cols, key=f"{plot_type}-y")
                    fig, ax = plt.subplots()
                    sns.barplot(data=df, x=x, y=y, ax=ax)
                    st.pyplot(fig)

                elif plot_type == "Heatmap":
                    corr = df[numeric_cols].corr()
                    fig, ax = plt.subplots()
                    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
                    ax.set_title("Correlation Heatmap")
                    st.pyplot(fig)

                elif plot_type == "Pairplot":
                    selected = st.multiselect(f"[{plot_type}] Select numeric columns:", numeric_cols, default=numeric_cols[:3], key=f"{plot_type}-cols")
                    hue = st.selectbox(f"[{plot_type}] Hue (optional):", ["None"] + categorical_cols, key=f"{plot_type}-hue")
                    if selected:
                        fig = sns.pairplot(df[selected + ([hue] if hue != "None" else [])], hue=hue if hue != "None" else None).fig
                        st.pyplot(fig)
                    else:
                        st.warning("Please select at least one column.")

                elif plot_type == "Countplot":
                    col = st.selectbox(f"[{plot_type}] Select a categorical column:", categorical_cols, key=f"{plot_type}-col")
                    fig, ax = plt.subplots()
                    sns.countplot(data=df, x=col, ax=ax)
                    ax.set_title(f"Countplot of {col}")
                    st.pyplot(fig)

                # Show download if fig is available
                if fig:
                    st.download_button(
                        label="📥 Download Plot as PNG",
                        data=save_fig(fig),
                        file_name=f"{plot_type.lower().replace(' ', '_')}.png",
                        mime="image/png",
                        key=f"{plot_type}-dl"
                    )

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
else:
    st.info("Upload a CSV file to begin.")
