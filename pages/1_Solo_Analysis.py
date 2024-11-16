import streamlit as st
import pandas as pd
import altair as alt
from utils import StateManager, with_state_management, MONTH_ORDER

# Page Configuration
st.set_page_config(page_title="Solo Sales Analysis", page_icon="📊", layout="wide")

# Constants
MONTH_ORDER = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']

# Custom styling
st.markdown("""
    <style>
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-out;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .metric-label {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 8px;
    }
    
    .metric-delta {
        font-size: 0.875rem;
        font-weight: 500;
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    .metric-delta.positive {
        color: #166534;
        background: #dcfce7;
    }
    
    .metric-delta.negative {
        color: #991b1b;
        background: #fee2e2;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'solo_data' not in st.session_state:
    st.session_state.solo_data = None

# Sidebar
with st.sidebar:
    if st.session_state.solo_data is None:
        uploaded_file = st.file_uploader("Upload Solo Sales Data", type=['csv', 'xlsx'])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                required_columns = ['Month', 'Year', 'Subscription Package', 'Number of Subscriptions', 'Amount (GHS)']
                if all(col in df.columns for col in required_columns):
                    st.session_state.solo_data = df
                    st.rerun()
                else:
                    st.error("Upload failed: Missing required columns")
                    st.write("Expected columns:", required_columns)
                    st.write("Found columns:", df.columns.tolist())
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    else:
        if st.button("Clear Data", key='clear_data'):
            st.session_state.solo_data = None
            st.rerun()
        
        st.markdown("### Filters")
        
        # Get the data
        df = st.session_state.solo_data
        
        # Year filter
        years = sorted(df['Year'].unique())
        selected_year = st.selectbox(
            'Select Year', 
            years, 
            index=len(years)-1,
            key='year_filter'
        )
        
        # Create filtered dataframes
        current_year_df = df[df['Year'] == selected_year]
        prev_year_df = df[df['Year'] == selected_year - 1]
        
       
        
        # Month filter section
        st.markdown("---")
        
        # Initialize session state for month filter if not exists
        if 'month_filter_reset' not in st.session_state:
            st.session_state.month_filter_reset = False
        
        # Month filter
        months = sorted(current_year_df['Month'].unique().tolist(), key=lambda x: MONTH_ORDER.index(x))
        month_options = ['All'] + months
        
        # Handle month filter reset
        
            
        selected_months = st.multiselect(
            'Select Months',
            options=month_options,
            default=['All'] if not st.session_state.month_filter_reset else ['All'],
            key='month_filter'
        )
        if st.button('↺ Reset months', key='clear_months', type='secondary', use_container_width=True):
            st.session_state.month_filter_reset = True
            st.rerun()
        # Package filter section
        
        st.markdown("---")
        # Initialize session state for package filter if not exists
        if 'package_filter_reset' not in st.session_state:
            st.session_state.package_filter_reset = False
        
        # Package filter
        packages = sorted(current_year_df['Subscription Package'].unique().tolist())
        package_options = ['All'] + packages
        
        # Handle package filter reset
        
            
        selected_packages = st.multiselect(
            'Select Packages',
            options=package_options,
            default=['All'] if not st.session_state.package_filter_reset else ['All'],
            key='package_filter'
        )
        if st.button('↺ Reset packages', key='clear_packages', type='secondary', use_container_width=True):
            st.session_state.package_filter_reset = True
            st.rerun()
        # Handle "All" selection for months and packages
        if 'All' in selected_months:
            selected_months = months
            
        if 'All' in selected_packages:
            selected_packages = packages
        
        # Reset the reset flags after they've been used
        if st.session_state.month_filter_reset:
            st.session_state.month_filter_reset = False
            
        if st.session_state.package_filter_reset:
            st.session_state.package_filter_reset = False
        
        # Warning for no selections
        if not selected_months or not selected_packages:
            st.warning('Please select at least one option for each filter')
        
        # Filter data based on selections
        filtered_df = current_year_df[
            (current_year_df['Month'].isin(selected_months)) &
            (current_year_df['Subscription Package'].isin(selected_packages))
        ]

# Main content
if st.session_state.solo_data is not None:
    df = st.session_state.solo_data
    
    # Calculate metrics using filtered data
    curr_sales = filtered_df['Amount (GHS)'].sum()
    prev_sales = prev_year_df[
        (prev_year_df['Month'].isin(selected_months)) & 
        (prev_year_df['Subscription Package'].isin(selected_packages))
    ]['Amount (GHS)'].sum()
    
    sales_growth = ((curr_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
    
    curr_subs = filtered_df['Number of Subscriptions'].sum()
    prev_subs = prev_year_df[
        (prev_year_df['Month'].isin(selected_months)) & 
        (prev_year_df['Subscription Package'].isin(selected_packages))
    ]['Number of Subscriptions'].sum()
    
    subs_growth = ((curr_subs - prev_subs) / prev_subs * 100) if prev_subs > 0 else 0
    
    avg_value = curr_sales / curr_subs if curr_subs > 0 else 0
    prev_avg = prev_sales / prev_subs if prev_subs > 0 else 0
    avg_growth = ((avg_value - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
    
    # Display metrics
    m1, m2, m3, m4 = st.columns(4)
    
    metrics = [
        (m1, "Total Revenue", f"GHS {curr_sales:,.2f}", sales_growth),
        (m2, "Subscriptions", f"{curr_subs:,}", subs_growth),
        (m3, "Average Value", f"GHS {avg_value:,.2f}", avg_growth),
        (m4, "YoY Growth", f"{sales_growth:+.1f}%", None)
    ]
    
    for col, label, value, change in metrics:
        with col:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    {f'<div class="metric-delta {("positive" if change > 0 else "negative")}">{change:+.1f}%</div>' if change is not None else ''}
                </div>
            """, unsafe_allow_html=True)
    
    # Add after the metrics section and before the columns split
    
    # Create two columns for the layout
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        # Monthly Revenue Trend
        st.markdown("### Monthly Revenue Trend")
        
        # Prepare monthly data
        monthly_data = df[df['Year'].isin([selected_year-1, selected_year])].copy()
        monthly_data['Month'] = pd.Categorical(monthly_data['Month'], 
                                             categories=MONTH_ORDER, 
                                             ordered=True)
        
        # Aggregate monthly data
        monthly_revenue = monthly_data.groupby(['Year', 'Month'], 
                                             as_index=False)['Amount (GHS)'].sum()
        
        # Convert Year to string for Altair
        monthly_revenue['Year'] = monthly_revenue['Year'].astype(str)
        
        # Create revenue chart
        revenue_chart = alt.Chart(monthly_revenue).mark_line(
            point=True,
            strokeWidth=3
        ).encode(
            x=alt.X('Month:N', 
                   sort=MONTH_ORDER,
                   axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Amount (GHS):Q',
                   title='Revenue (GH₵)',
                   axis=alt.Axis(format=',.0f')),
            color=alt.Color('Year:N',
                          scale=alt.Scale(domain=[str(selected_year-1), str(selected_year)],
                                        range=['#94a3b8', '#22c55e'])),
            tooltip=[
                alt.Tooltip('Month:N'),
                alt.Tooltip('Year:N'),
                alt.Tooltip('Amount (GHS):Q', format=',.2f', title='Revenue (GH₵)')
            ]
        ).properties(height=300)
        
        # Display the chart
        st.altair_chart(revenue_chart, use_container_width=True)
        
        # Subscription Trends
        st.markdown("### Subscription Trends")
        
        # Prepare subscription data
        monthly_subs = df[df['Year'].isin([selected_year-1, selected_year])].copy()
        monthly_subs['Month'] = pd.Categorical(monthly_subs['Month'], 
                                             categories=MONTH_ORDER, 
                                             ordered=True)
        
        # Aggregate subscription data
        monthly_subs = monthly_subs.groupby(['Year', 'Month'], 
                                          as_index=False)['Number of Subscriptions'].sum()
        
        # Convert Year to string for Altair
        monthly_subs['Year'] = monthly_subs['Year'].astype(str)
        
        # Create subscription chart
        subs_chart = alt.Chart(monthly_subs).mark_bar().encode(
            x=alt.X('Month:N', 
                   sort=MONTH_ORDER,
                   axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Number of Subscriptions:Q'),
            color=alt.Color('Year:N',
                          scale=alt.Scale(domain=[str(selected_year-1), str(selected_year)],
                                        range=['#94a3b8', '#22c55e'])),
            tooltip=['Month', 'Year', 'Number of Subscriptions']
        ).properties(height=300)
        
        # Display the chart
        st.altair_chart(subs_chart, use_container_width=True)
        
        # Average Sale Value Trend
        st.markdown("### Average Sale Value Trend")
        
        # Calculate average sale value per month
        avg_value_data = df[df['Year'].isin([selected_year-1, selected_year])].copy()
        avg_value_data['Month'] = pd.Categorical(avg_value_data['Month'], 
                                               categories=MONTH_ORDER, 
                                               ordered=True)
        
        # Calculate average value
        avg_value_data = avg_value_data.groupby(['Year', 'Month'], as_index=False).agg({
            'Amount (GHS)': 'sum',
            'Number of Subscriptions': 'sum'
        })
        avg_value_data['Average Value'] = avg_value_data['Amount (GHS)'] / avg_value_data['Number of Subscriptions']
        
        # Convert Year to string for Altair
        avg_value_data['Year'] = avg_value_data['Year'].astype(str)
        
        # Create average value chart
        avg_value_chart = alt.Chart(avg_value_data).mark_line(
            point=True,
            strokeWidth=3
        ).encode(
            x=alt.X('Month:N', sort=MONTH_ORDER),
            y=alt.Y('Average Value:Q',
                   title='Average Sale Value (GH₵)',
                   axis=alt.Axis(format=',.2f')),
            color=alt.Color('Year:N',
                          scale=alt.Scale(domain=[str(selected_year-1), str(selected_year)],
                                        range=['#94a3b8', '#22c55e'])),
            tooltip=[
                alt.Tooltip('Month:N'),
                alt.Tooltip('Year:N'),
                alt.Tooltip('Average Value:Q', format=',.2f', title='Avg Value (GH₵)'),
                alt.Tooltip('Number of Subscriptions:Q', title='Total Subscriptions')
            ]
        ).properties(height=300)
        
        # Display the chart
        st.altair_chart(avg_value_chart, use_container_width=True)
        
        # Inside the right_col from earlier
        with right_col:
            # Package Growth Analysis
            st.markdown("### Package Growth Analysis")
            
            # Calculate package performance for current and previous year
            def get_package_revenue(df):
                return df.groupby('Subscription Package')['Amount (GHS)'].sum().reset_index()
            
            # Get revenue for both years
            current_package = get_package_revenue(current_year_df)
            prev_package = get_package_revenue(prev_year_df)
            
            # Merge and calculate growth
            package_growth = current_package.merge(
                prev_package, 
                on='Subscription Package', 
                suffixes=('_current', '_prev')
            )
            
            # Calculate growth percentage
            package_growth['Growth'] = ((package_growth['Amount (GHS)_current'] - 
                                       package_growth['Amount (GHS)_prev']) / 
                                      package_growth['Amount (GHS)_prev'] * 100)
            
            # Sort by growth rate
            package_growth = package_growth.sort_values('Growth', ascending=True)
            
            # Create horizontal bar chart
            growth_chart = alt.Chart(package_growth).mark_bar().encode(
                y=alt.Y('Subscription Package:N', 
                       title='Package',
                       sort=alt.EncodingSortField(field='Growth', order='ascending')),
                x=alt.X('Growth:Q', 
                       title='Growth Rate (%)',
                       axis=alt.Axis(format='+.1f')),
                color=alt.condition(
                    alt.datum.Growth > 0,
                    alt.value('#22c55e'),  # Green for positive
                    alt.value('#ef4444')   # Red for negative
                ),
                tooltip=[
                    alt.Tooltip('Subscription Package:N', title='Package'),
                    alt.Tooltip('Growth:Q', format='+.1f', title='Growth Rate (%)'),
                    alt.Tooltip('Amount (GHS)_current:Q', format=',.2f', title='Current Revenue (GH₵)'),
                    alt.Tooltip('Amount (GHS)_prev:Q', format=',.2f', title='Previous Revenue (GH₵)')
                ]
            ).properties(height=300)
            
            # Display the chart
            st.altair_chart(growth_chart, use_container_width=True)
            
            # Revenue Distribution
            st.markdown("### Revenue Distribution")
            
            # Prepare data for pie chart
            package_distribution = current_year_df.groupby('Subscription Package').agg({
                'Amount (GHS)': 'sum'
            }).reset_index()
            
            # Calculate percentages
            total_revenue = package_distribution['Amount (GHS)'].sum()
            package_distribution['Percentage'] = (package_distribution['Amount (GHS)'] / total_revenue * 100)
            
            # Create pie chart
            pie = alt.Chart(package_distribution).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field='Amount (GHS)', type='quantitative'),
                color=alt.Color('Subscription Package:N', 
                               scale=alt.Scale(scheme='greens')),
                tooltip=[
                    alt.Tooltip('Subscription Package', title='Package'),
                    alt.Tooltip('Amount (GHS)', title='Revenue (GHS)', format=','),
                    alt.Tooltip('Percentage', title='Percentage', format='.1f')
                ]
            ).properties(height=300)
            
            # Display the chart
            st.altair_chart(pie, use_container_width=True)
            
            # Revenue Distribution Bar Chart
            st.markdown("### Revenue by Package")
            
            # Sort packages by revenue
            package_distribution = package_distribution.sort_values('Amount (GHS)', ascending=True)
            
            # Create bar chart
            revenue_dist_chart = alt.Chart(package_distribution).mark_bar().encode(
                y=alt.Y('Subscription Package:N',
                       title='Package',
                       sort=alt.EncodingSortField(field='Amount (GHS)', order='ascending')),
                x=alt.X('Amount (GHS):Q',
                       title='Revenue (GH₵)'),
                color=alt.Color('Subscription Package:N',
                              scale=alt.Scale(scheme='greens'),
                              legend=None),
                tooltip=[
                    alt.Tooltip('Subscription Package:N', title='Package'),
                    alt.Tooltip('Amount (GHS):Q', title='Revenue (GH₵)', format=',.2f'),
                    alt.Tooltip('Percentage:Q', title='% of Total', format='.1f')
                ]
            ).properties(height=300)
            
            # Display the chart
            st.altair_chart(revenue_dist_chart, use_container_width=True)

    # Key Insights Section
    st.markdown("### Key Insights")
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        st.markdown("""
            <div class="metric-card" style="padding: 1rem;">
                <h4 style="color: #334155; margin-bottom: 1rem;">Monthly Performance</h4>
        """, unsafe_allow_html=True)
        
        # Get top performing months
        monthly_performance = current_year_df.groupby('Month').agg({
            'Amount (GHS)': 'sum'
        }).reset_index()
        
        monthly_performance['Month'] = pd.Categorical(
            monthly_performance['Month'], 
            categories=MONTH_ORDER, 
            ordered=True
        )
        
        top_months = monthly_performance.nlargest(3, 'Amount (GHS)')
        
        for _, month_data in top_months.iterrows():
            st.markdown(f"""
                <div style="margin: 10px 0; padding: 10px; background: #f8fafc; border-radius: 4px;">
                    <div style="color: #0f172a; font-weight: 500;">{month_data['Month']}</div>
                    <div style="color: #22c55e; font-size: 18px; font-weight: 600;">
                        GHS {month_data['Amount (GHS)']:,.2f}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with insight_col2:
        st.markdown("""
            <div class="metric-card" style="padding: 1rem;">
                <h4 style="color: #334155; margin-bottom: 1rem;">Package Performance</h4>
        """, unsafe_allow_html=True)
        
        # Calculate package metrics
        package_metrics = current_year_df.groupby('Subscription Package').agg({
            'Amount (GHS)': 'sum',
            'Number of Subscriptions': 'sum'
        }).reset_index()
        
        package_metrics['Average Value'] = package_metrics['Amount (GHS)'] / package_metrics['Number of Subscriptions']
        top_package = package_metrics.nlargest(1, 'Amount (GHS)').iloc[0]
        best_value = package_metrics.nlargest(1, 'Average Value').iloc[0]
        
        st.markdown(f"""
            <div style="margin: 10px 0; padding: 10px; background: #f8fafc; border-radius: 4px;">
                <div style="color: #64748b;">Highest Revenue Package</div>
                <div style="color: #0f172a; font-weight: 500;">{top_package['Subscription Package']}</div>
                <div style="color: #22c55e; font-size: 18px; font-weight: 600;">
                    GHS {top_package['Amount (GHS)']:,.2f}
                </div>
            </div>
            <div style="margin: 10px 0; padding: 10px; background: #f8fafc; border-radius: 4px;">
                <div style="color: #64748b;">Best Value Package</div>
                <div style="color: #0f172a; font-weight: 500;">{best_value['Subscription Package']}</div>
                <div style="color: #22c55e; font-size: 18px; font-weight: 600;">
                    GHS {best_value['Average Value']:,.2f} / subscription
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with insight_col3:
        st.markdown("""
            <div class="metric-card" style="padding: 1rem;">
                <h4 style="color: #334155; margin-bottom: 1rem;">Growth Analysis</h4>
        """, unsafe_allow_html=True)
        
        # Calculate growth metrics
        current_quarter = (MONTH_ORDER.index(current_year_df['Month'].max()) // 3) + 1
        quarter_months = MONTH_ORDER[(current_quarter-1)*3:current_quarter*3]
        
        current_quarter_data = current_year_df[current_year_df['Month'].isin(quarter_months)]
        prev_quarter_data = prev_year_df[prev_year_df['Month'].isin(quarter_months)]
        
        quarter_growth = ((current_quarter_data['Amount (GHS)'].sum() - 
                         prev_quarter_data['Amount (GHS)'].sum()) / 
                        prev_quarter_data['Amount (GHS)'].sum() * 100) if prev_quarter_data['Amount (GHS)'].sum() > 0 else 0
        
        st.markdown(f"""
            <div style="margin: 10px 0; padding: 10px; background: #f8fafc; border-radius: 4px;">
                <div style="color: #64748b;">Q{current_quarter} Performance</div>
                <div style="color: #0f172a; font-weight: 500;">Quarter-over-Quarter Growth</div>
                <div class="metric-delta {'positive' if quarter_growth > 0 else 'negative'}" 
                     style="margin-top: 5px;">
                    {quarter_growth:+.1f}%
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Add YTD comparison
        ytd_months = current_year_df['Month'].unique()
        current_ytd = current_year_df['Amount (GHS)'].sum()
        prev_ytd = prev_year_df[prev_year_df['Month'].isin(ytd_months)]['Amount (GHS)'].sum()
        ytd_growth = ((current_ytd - prev_ytd) / prev_ytd * 100) if prev_ytd > 0 else 0
        
        st.markdown(f"""
            <div style="margin: 10px 0; padding: 10px; background: #f8fafc; border-radius: 4px;">
                <div style="color: #64748b;">Year-to-Date Comparison</div>
                <div style="color: #0f172a; font-weight: 500;">YTD Growth</div>
                <div class="metric-delta {'positive' if ytd_growth > 0 else 'negative'}" 
                     style="margin-top: 5px;">
                    {ytd_growth:+.1f}%
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Expandable sections for Glossary and Raw Data
    st.markdown("---")

    # Create two columns for Glossary and Raw Data
    info_col1, info_col2 = st.columns(2)

    with info_col1:
        with st.expander("📖 Glossary"):
            st.markdown("""
                ### Metrics Explanation
                
                **Revenue Metrics:**
                - **Total Revenue**: Total earnings from all subscriptions
                - **YoY Growth**: Year-over-Year percentage change in revenue
                - **Average Value**: Revenue earned per subscription
                
                **Subscription Metrics:**
                - **Number of Subscriptions**: Total subscriptions sold
                - **Best Value Package**: Package with highest revenue per subscription
                - **Package Growth**: Year-over-Year growth rate for each package
                
                **Growth Metrics:**
                - **Quarter Growth**: Current quarter vs same quarter last year
                - **YTD Growth**: Year-to-Date comparison with previous year
                
                **Charts:**
                - **Monthly Trend**: Revenue pattern over months
                - **Package Distribution**: Revenue share by package
                - **Growth Analysis**: Package performance comparison
            """)

    with info_col2:
        with st.expander("📊 View Raw Data"):
            if st.session_state.solo_data is not None:
                df = st.session_state.solo_data
                
                # Add data filters
                st.markdown("### Data Filters")
                
                # Year filter
                year_filter = st.multiselect(
                    "Select Years",
                    options=sorted(df['Year'].unique()),
                    default=sorted(df['Year'].unique())
                )
                
                # Month filter
                month_filter = st.multiselect(
                    "Select Months",
                    options=MONTH_ORDER,
                    default=MONTH_ORDER
                )
                
                # Package filter
                package_filter = st.multiselect(
                    "Select Packages",
                    options=sorted(df['Subscription Package'].unique()),
                    default=sorted(df['Subscription Package'].unique())
                )
                
                # Filter the dataframe
                filtered_raw_df = df[
                    (df['Year'].isin(year_filter)) &
                    (df['Month'].isin(month_filter)) &
                    (df['Subscription Package'].isin(package_filter))
                ]
                
                # Show filtered data
                st.markdown("### Filtered Data")
                st.dataframe(
                    filtered_raw_df.style.format({
                        'Amount (GHS)': '{:,.2f}',
                        'Number of Subscriptions': '{:,}'
                    }),
                    height=300
                )
                
                # Add download button
                csv = filtered_raw_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download Filtered Data",
                    csv,
                    "solo_sales_data.csv",
                    "text/csv",
                    key='download-csv'
                )
                
                # Show summary statistics
                st.markdown("### Summary Statistics")
                
                # Calculate summary statistics
                summary = {
                    'Total Revenue': filtered_raw_df['Amount (GHS)'].sum(),
                    'Average Revenue per Month': filtered_raw_df.groupby(['Year', 'Month'])['Amount (GHS)'].sum().mean(),
                    'Total Subscriptions': filtered_raw_df['Number of Subscriptions'].sum(),
                    'Average Subscriptions per Month': filtered_raw_df.groupby(['Year', 'Month'])['Number of Subscriptions'].sum().mean(),
                    'Highest Monthly Revenue': filtered_raw_df.groupby(['Year', 'Month'])['Amount (GHS)'].sum().max(),
                    'Lowest Monthly Revenue': filtered_raw_df.groupby(['Year', 'Month'])['Amount (GHS)'].sum().min(),
                    'Average Revenue per Subscription': filtered_raw_df['Amount (GHS)'].sum() / filtered_raw_df['Number of Subscriptions'].sum()
                }
                
                # Create a formatted dataframe
                summary_df = pd.DataFrame.from_dict(summary, orient='index', columns=['Value'])
                
                # Format the values
                summary_df['Value'] = summary_df['Value'].apply(lambda x: f"GHS {x:,.2f}" if 'Revenue' in summary_df.index[summary_df['Value'] == x][0] 
                                                              else f"{x:,.0f}" if 'Subscriptions' in summary_df.index[summary_df['Value'] == x][0]
                                                              else f"GHS {x:,.2f}")
                
                # Display the summary
                st.dataframe(summary_df, use_container_width=True)
            else:
                st.info("Upload data to view raw data and statistics")
else:
    st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h2>👋 Welcome to the Solo Sales Analysis Dashboard!</h2>
            <p style="font-size: 18px;">Upload your sales data file using the sidebar to get started</p>
            <p>Required columns: Month, Year, Subscription Package, Number of Subscriptions, Amount (GHS)</p>
        </div>
    """, unsafe_allow_html=True)
