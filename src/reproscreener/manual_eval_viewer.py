"""
Streamlit application for viewing and comparing manual evaluation datasets.

This app provides an interactive interface to explore:
- Abstract manual evaluations
- GPT agreement with manual evaluations  
- Full manuscript evaluations
- Combined abstract evaluation dataset
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from manual_eval import load_manual_evaluations

# Configure Streamlit page
st.set_page_config(
    page_title="Manual Evaluation Viewer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_data
def load_evaluation_data():
    """Load all evaluation datasets with caching."""
    parser = load_manual_evaluations()
    return parser.load_all_evaluations(), parser

def prepare_heatmap_df(df, evaluation_type="manual"):
    """Prepare dataframe for heatmap visualization in the style of the original code."""
    if df.empty:
        return None
    
    # Find binary metric columns based on evaluation type
    if evaluation_type == "manual":
        metric_cols = [col for col in df.columns if col.startswith('manual_') and col.endswith('_identified')]
        prefix = 'manual_'
    elif evaluation_type == "gpt":
        metric_cols = [col for col in df.columns if col.startswith('gpt_') and col.endswith('_identified')]
        prefix = 'gpt_'
    else:
        return None
    
    if not metric_cols:
        return None
    
    # Create heatmap results similar to original prepare_tex_heatmap_df
    heatmap_results = []
    
    for _, row in df.iterrows():
        paper_id = row['paper_id']
        
        # Check each metric for this paper
        found_metrics = []
        for col in metric_cols:
            val = row.get(col)
            if val == True or val == 1:
                # Clean metric name
                metric_name = col.replace(prefix, '').replace('_identified', '').replace('_', ' ').title()
                found_metrics.append(metric_name)
        
        # Add results to heatmap_results
        if not found_metrics:
            heatmap_results.append([paper_id, "No metrics identified"])
        else:
            for metric in found_metrics:
                heatmap_results.append([paper_id, metric])
    
    heatmap_df = pd.DataFrame(heatmap_results, columns=["Paper_ID", "Found_Metric"]).drop_duplicates()
    return heatmap_df

def create_binary_heatmap_matplotlib(df, evaluation_type="manual", sort_x=False, sort_y=True):
    """Create a binary heatmap using matplotlib/seaborn in the style of the original code."""
    heatmap_df = prepare_heatmap_df(df, evaluation_type)
    
    if heatmap_df is None or heatmap_df.empty:
        return None
    
    # Create binary crosstab similar to original plot_tex_heatmap
    binary_df = pd.crosstab(heatmap_df["Paper_ID"], heatmap_df["Found_Metric"]).replace({1: True, 0: False}).infer_objects(copy=False)
    
    if sort_y:
        # Sort by column frequency (metrics)
        column_order = binary_df.sum().sort_values(ascending=False).index
        binary_df = binary_df[column_order]
    
    if sort_x:
        # Sort by row frequency (papers)
        row_order = binary_df.T.sum().sort_values(ascending=False).index
        binary_df = binary_df.loc[row_order]
    
    # Transpose to match original style (metrics on y-axis, papers on x-axis)
    binary_df = binary_df.map(float).T
    
    # Use custom colormap similar to original: (empty, filled)
    custom_cmap = ListedColormap(["#FFF0F0", "#E74C3C"])
    
    # Create figure with similar styling to original, higher DPI for resolution
    fig, ax = plt.subplots(figsize=(max(12, binary_df.shape[1] * 0.5), max(4, binary_df.shape[0] * 0.4)), 
                          tight_layout={"pad": 1.5}, dpi=300)
    
    # Add border lines like original
    ax.axhline(y=0, color="k", linewidth=1)
    ax.axvline(x=0, color="k", linewidth=1)
    ax.axhline(y=binary_df.shape[0], color="k", linewidth=1)
    ax.axvline(x=binary_df.shape[1], color="k", linewidth=1)
    
    # Create heatmap
    sns.heatmap(binary_df, cmap=custom_cmap, cbar=False, linewidths=1, ax=ax)
    
    # Style similar to original
    ax.set(xlabel=None, ylabel=None)
    ax.set_title(f"{evaluation_type.title()} Evaluation Heatmap", pad=20)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    return fig

def create_agreement_heatmap(df):
    """Create a heatmap showing agreement rates across different metrics."""
    if df.empty:
        return None
    
    # Find all agreement columns
    agreement_cols = [col for col in df.columns if col.endswith('_agreement')]
    
    if not agreement_cols:
        return None
    
    # Calculate agreement rates for each metric
    agreement_data = {}
    for col in agreement_cols:
        metric_name = col.replace('_identified_agreement', '').replace('_available_agreement', '').replace('_agreement', '')
        agreements = df[col].dropna()
        if len(agreements) > 0:
            agreement_rate = (agreements == True).sum() / len(agreements)
            agreement_data[metric_name] = agreement_rate
    
    if not agreement_data:
        return None
    
    # Create heatmap data
    metrics = list(agreement_data.keys())
    rates = list(agreement_data.values())
    
    fig = go.Figure(data=go.Heatmap(
        z=[rates],
        x=metrics,
        y=['Agreement Rate'],
        colorscale='RdYlGn',
        zmin=0,
        zmax=1,
        text=[[f"{rate:.2%}" for rate in rates]],
        texttemplate="%{text}",
        textfont={"size": 12},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="GPT vs Manual Agreement Rates by Metric",
        xaxis_title="Metrics",
        height=200
    )
    
    return fig

def create_coverage_comparison(evaluations):
    """Create a chart comparing coverage across different evaluation types."""
    coverage_data = []
    
    for eval_type, df in evaluations.items():
        if df.empty:
            continue
            
        total_papers = len(df)
        
        # Count metrics with data
        metric_cols = [col for col in df.columns if col.endswith(('_identified', '_available', '_used'))]
        
        for col in metric_cols:
            metric_name = col.replace('_identified', '').replace('_available', '').replace('_used', '')
            non_null_count = df[col].notna().sum()
            positive_count = (df[col] == True).sum() if df[col].dtype == bool else (df[col] == 1).sum()
            
            coverage_data.append({
                'Evaluation Type': eval_type,
                'Metric': metric_name,
                'Coverage': non_null_count / total_papers if total_papers > 0 else 0,
                'Positive Rate': positive_count / non_null_count if non_null_count > 0 else 0,
                'Total Papers': total_papers
            })
    
    if not coverage_data:
        return None
    
    coverage_df = pd.DataFrame(coverage_data)
    
    fig = px.scatter(
        coverage_df,
        x='Coverage',
        y='Positive Rate',
        color='Evaluation Type',
        size='Total Papers',
        hover_data=['Metric'],
        title="Coverage vs Positive Rate by Evaluation Type",
        labels={
            'Coverage': 'Coverage (% of papers evaluated)',
            'Positive Rate': 'Positive Rate (% of evaluated papers with positive result)'
        }
    )
    
    fig.update_layout(height=500)
    
    return fig

def main():
    """Main Streamlit application."""
    st.title("Manual Evaluation Viewer")
    st.markdown("Explore manual and LLM evaluated datasets")
    
    # Load data
    try:
        evaluations, parser = load_evaluation_data()
    except Exception as e:
        st.error(f"Error loading evaluation data: {e}")
        return
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    
    # Dataset selection
    dataset_names = list(evaluations.keys())
    selected_datasets = st.sidebar.multiselect(
        "Select datasets to view:",
        dataset_names,
        default=dataset_names
    )
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Data Explorer", 
        "Metric Comparison", 
        "Agreement Analysis", 
        "Summary Statistics"
    ])
    
    with tab1:
        st.header("Data Explorer")
        
        # Dataset selector for detailed view
        selected_dataset = st.selectbox(
            "Select dataset to explore:",
            selected_datasets,
            key="explorer_dataset"
        )
        
        if selected_dataset and selected_dataset in evaluations:
            df = evaluations[selected_dataset]
            
            if not df.empty:
                st.subheader(f"{selected_dataset.replace('_', ' ').title()} Dataset")
                
                # Display basic stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Papers", len(df))
                with col2:
                    st.metric("Total Columns", len(df.columns))
                with col3:
                    unique_papers = df['paper_id'].nunique() if 'paper_id' in df.columns else 0
                    st.metric("Unique Papers", unique_papers)
                
                # Column selector
                st.subheader("Column Explorer")
                columns_to_show = st.multiselect(
                    "Select columns to display:",
                    df.columns.tolist(),
                    default=df.columns.tolist()[:10]  # Show first 10 columns by default
                )
                
                if columns_to_show:
                    # Filter and display data
                    filtered_df = df[columns_to_show]
                    
                    # Search functionality
                    search_term = st.text_input("Search papers (by Paper ID):")
                    if search_term:
                        if 'paper_id' in filtered_df.columns:
                            filtered_df = filtered_df[filtered_df['paper_id'].str.contains(search_term, case=False, na=False)]
                    
                    # Configure column display based on column names
                    column_config = {}
                    for col in filtered_df.columns:
                        if "_description" in col:
                            column_config[col] = st.column_config.TextColumn(width="small")
                        elif "_identified" in col:
                            column_config[col] = st.column_config.CheckboxColumn(width="small")
                        elif col == "paper_id":
                            column_config[col] = st.column_config.TextColumn(width="small")
                    
                    st.dataframe(filtered_df, use_container_width=True, height=400, column_config=column_config)
                
                # Download option
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download filtered dataset as CSV",
                    data=csv,
                    file_name=f"{selected_dataset}_filtered.csv",
                    mime="text/csv"
                )
            else:
                st.warning(f"No data available for {selected_dataset}")
    
    with tab2:
        st.header("Metric Comparison")
        
        # Focus on combined abstract dataset for detailed comparison
        if 'combined_abstract' in evaluations and 'combined_abstract' in selected_datasets:
            combined_df = evaluations['combined_abstract']
            
            if not combined_df.empty:
                st.subheader("Manual vs GPT Evaluation Heatmaps")
                
                st.subheader("Manual Evaluation")
                manual_heatmap = create_binary_heatmap_matplotlib(combined_df, "manual")
                if manual_heatmap:
                    st.pyplot(manual_heatmap, use_container_width=True)
                else:
                    st.warning("No manual evaluation data available")

                st.subheader("GPT Evaluation")
                gpt_heatmap = create_binary_heatmap_matplotlib(combined_df, "gpt")
                if gpt_heatmap:
                    st.pyplot(gpt_heatmap, use_container_width=True)
                else:
                    st.warning("No GPT evaluation data available")
                
                # Show summary statistics
                st.subheader("Summary Statistics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    manual_cols = [col for col in combined_df.columns if col.startswith('manual_') and col.endswith('_identified')]
                    if manual_cols:
                        manual_positive = sum((combined_df[col] == True).sum() for col in manual_cols)
                        manual_total = sum(combined_df[col].notna().sum() for col in manual_cols)
                        rate_text = f"{manual_positive/manual_total:.1%}" if manual_total > 0 else "N/A"
                        st.metric(
                            "Manual Positive Rate",
                            f"{manual_positive}/{manual_total}",
                            rate_text,
                            delta_color="off"
                        )
                
                with col2:
                    gpt_cols = [col for col in combined_df.columns if col.startswith('gpt_') and col.endswith('_identified')]
                    if gpt_cols:
                        gpt_positive = sum((combined_df[col] == True).sum() for col in gpt_cols)
                        gpt_total = sum(combined_df[col].notna().sum() for col in gpt_cols)
                        rate_text = f"{gpt_positive/gpt_total:.1%}" if gpt_total > 0 else "N/A"
                        st.metric(
                            "GPT Positive Rate",
                            f"{gpt_positive}/{gpt_total}",
                            rate_text,
                            delta_color="off"
                        )
                
                with col3:
                    agreement_cols = [col for col in combined_df.columns if col.endswith('_agreement')]
                    if agreement_cols:
                        total_agreements = sum((combined_df[col] == True).sum() for col in agreement_cols)
                        total_comparisons = sum(combined_df[col].notna().sum() for col in agreement_cols)
                        rate_text = f"{total_agreements/total_comparisons:.1%}" if total_comparisons > 0 else "N/A"
                        st.metric(
                            "Overall Agreement Rate",
                            f"{total_agreements}/{total_comparisons}",
                            rate_text,
                            delta_color="off"
                        )
        else:
            st.info("Combined abstract dataset not available or not selected")
    
    with tab3:
        st.header("Agreement Analysis")
        
        if 'combined_abstract' in evaluations and 'combined_abstract' in selected_datasets:
            combined_df = evaluations['combined_abstract']
            
            if not combined_df.empty:
                # Agreement heatmap
                st.subheader("Agreement Rates Heatmap")
                heatmap_fig = create_agreement_heatmap(combined_df)
                if heatmap_fig:
                    st.plotly_chart(heatmap_fig, use_container_width=True)
                
                # Overall agreement statistics
                st.subheader("Overall Agreement Statistics")
                
                if 'overall_agreement_rate' in combined_df.columns:
                    avg_agreement = combined_df['overall_agreement_rate'].mean()
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Average Agreement Rate", f"{avg_agreement:.1%}")
                    with col2:
                        total_agreements = combined_df['total_agreements'].sum()
                        total_comparisons = combined_df['total_comparisons'].sum()
                        overall_rate = total_agreements / total_comparisons if total_comparisons > 0 else 0
                        st.metric("Overall Agreement Rate", f"{overall_rate:.1%}")
                    with col3:
                        st.metric("Papers with Full Agreement", 
                                (combined_df['overall_agreement_rate'] == 1.0).sum())
                
                # Agreement distribution
                st.subheader("Agreement Rate Distribution")
                if 'overall_agreement_rate' in combined_df.columns:
                    fig = px.histogram(
                        combined_df,
                        x='overall_agreement_rate',
                        nbins=10,
                        title="Distribution of Overall Agreement Rates",
                        labels={'overall_agreement_rate': 'Agreement Rate', 'count': 'Number of Papers'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Combined abstract dataset not available for agreement analysis")
    
    with tab4:
        st.header("Summary Statistics")
        
        # Generate comprehensive statistics for all selected datasets
        for dataset_name in selected_datasets:
            if dataset_name in evaluations:
                df = evaluations[dataset_name]
                
                if not df.empty:
                    st.subheader(f"{dataset_name.replace('_', ' ').title()} Statistics")
                    
                    # Basic statistics
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Dataset Overview:**")
                        st.write(f"- Total papers: {len(df)}")
                        st.write(f"- Total columns: {len(df.columns)}")
                        if 'paper_id' in df.columns:
                            st.write(f"- Unique papers: {df['paper_id'].nunique()}")
                    
                    with col2:
                        # Count metrics by type
                        binary_cols = [col for col in df.columns if col.endswith(('_identified', '_available', '_used'))]
                        agreement_cols = [col for col in df.columns if col.endswith('_agreement')]
                        description_cols = [col for col in df.columns if col.endswith('_description')]
                        
                        st.write("**Column Types:**")
                        st.write(f"- Binary metrics: {len(binary_cols)}")
                        st.write(f"- Agreement metrics: {len(agreement_cols)}")
                        st.write(f"- Description fields: {len(description_cols)}")
                    
                    # Top metrics by coverage
                    if binary_cols:
                        st.write("**Top Metrics by Coverage:**")
                        coverage_stats = []
                        for col in binary_cols:
                            non_null = df[col].notna().sum()
                            positive = (df[col] == True).sum() if df[col].dtype == bool else (df[col] == 1).sum()
                            coverage_stats.append({
                                'Metric': col.replace('_identified', '').replace('_available', '').replace('_used', ''),
                                'Coverage': non_null,
                                'Positive': positive,
                                'Rate': f"{positive/non_null:.1%}" if non_null > 0 else "N/A"
                            })
                        
                        coverage_df = pd.DataFrame(coverage_stats).sort_values('Coverage', ascending=False)
                        st.dataframe(coverage_df.head(10), use_container_width=True)
                
                st.divider()

if __name__ == "__main__":
    main() 