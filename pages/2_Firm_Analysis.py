import streamlit as st
import pandas as pd
import altair as alt
from utils import StateManager, MONTH_ORDER

# Initialize session state first
StateManager.init_session_state()

# Page Configuration
st.set_page_config(page_title="Firm Sales Analysis", page_icon="🏢", layout="wide")

# Custom CSS (keep your existing CSS)
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
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1e293b;
        margin: 10px 0;
    }
    .metric-label {
        color: #475569;
        font-size: 14px;
        font-weight: 500;
    }
    .metric-delta {
        font-size: 14px;
        padding: 4px 8px;
        border-radius: 4px;
        display: inline-block;
    }
    .positive {
        background-color: #dcfce7;
        color: #166534;
    }
    .negative {
        background-color: #fee2e2;
        color: #991b1b;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    if not st.session_state.firm_data_loaded:
        uploaded_file = st.file_uploader("Upload Firm Data", type=['csv', 'xlsx'])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Store in session state
                st.session_state.firm_data = df
                st.session_state.firm_data_loaded = True
                
                # Initialize year filter with the latest year
                years = sorted(df['Year'].unique())
                st.session_state.firm_year_filter = years[-1]  # Set to latest year
                st.session_state.firm_month_filter = ['All']
                st.session_state.firm_package_filter = ['All']
                
                st.success("Data loaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    else:
        if st.button("Clear Data", key='clear_firm_data'):
            st.session_state.firm_data = None
            st.session_state.firm_data_loaded = False
            st.session_state.firm_year_filter = None
            st.session_state.firm_month_filter = ['All']
            st.session_state.firm_package_filter = ['All']
            st.rerun()

# Main content
if st.session_state.firm_data_loaded and st.session_state.firm_data is not None:
    try:
        # Get data from session state
        df = st.session_state.firm_data
        
        # Calculate derived metrics
        df['Users per Firm'] = df['Number of Users'] / df['Number of Firms'].where(df['Number of Firms'] > 0, 1)
        df['Revenue per User'] = df['Amount (GHS)'] / df['Number of Users'].where(df['Number of Users'] > 0, 1)
        df['Revenue per Firm'] = df['Amount (GHS)'] / df['Number of Firms'].where(df['Number of Firms'] > 0, 1)
        
        # Filters in Sidebar
        with st.sidebar:
            st.subheader("Filters")
            
            # Year filter
            years = sorted(df['Year'].unique())
            if st.session_state.firm_year_filter is None:
                st.session_state.firm_year_filter = years[-1]
            year_index = years.index(st.session_state.firm_year_filter)
            selected_year = st.selectbox('Year', years, 
                                       index=year_index,
                                       key='firm_year_filter')
            
            st.markdown("---")
            
            # Month filter section
            # Sort months according to MONTH_ORDER
            available_months = df['Month'].unique().tolist()
            all_months = [month for month in MONTH_ORDER if month in available_months]
            
            # Reset months button
            if st.button('↺ Reset months', key='reset_firm_months', type='secondary', use_container_width=True):
                st.session_state.firm_month_filter = ['All']
                st.rerun()
            
            # Get previous selection without 'All' if other months are selected
            prev_month_selection = st.session_state.firm_month_filter
            if 'All' in prev_month_selection and len(prev_month_selection) > 1:
                prev_month_selection = [m for m in prev_month_selection if m != 'All']
            
            # Month selector
            selected_months = st.multiselect('Select Months', 
                                           options=['All'] + all_months,
                                           default=prev_month_selection,
                                           key='firm_month_filter')
            
            # Handle 'All' selection for months
            new_month_selection = selected_months
            if 'All' in selected_months and len(selected_months) > 1:
                new_month_selection = [m for m in selected_months if m != 'All']
            elif len(selected_months) == 0:
                new_month_selection = ['All']
                
            if new_month_selection != selected_months:
                st.session_state.firm_month_filter = new_month_selection
                st.rerun()
            
            st.markdown("---")
            
            # Package filter section
            all_packages = sorted(df['Subscription Package'].unique())
            
            # Reset packages button
            if st.button('↺ Reset packages', key='reset_firm_packages', type='secondary', use_container_width=True):
                st.session_state.firm_package_filter = ['All']
                st.rerun()
            
            # Get previous selection without 'All' if other packages are selected
            prev_package_selection = st.session_state.firm_package_filter
            if 'All' in prev_package_selection and len(prev_package_selection) > 1:
                prev_package_selection = [p for p in prev_package_selection if p != 'All']
            
            # Package selector
            selected_packages = st.multiselect('Select Packages', 
                                             options=['All'] + all_packages,
                                             default=prev_package_selection,
                                             key='firm_package_filter')
            
            # Handle 'All' selection for packages
            new_package_selection = selected_packages
            if 'All' in selected_packages and len(selected_packages) > 1:
                new_package_selection = [p for p in selected_packages if p != 'All']
            elif len(selected_packages) == 0:
                new_package_selection = ['All']
                
            if new_package_selection != selected_packages:
                st.session_state.firm_package_filter = new_package_selection
                st.rerun()

        # Apply filters
        filtered_df = df.copy()
        if 'All' not in selected_months:
            filtered_df = filtered_df[filtered_df['Month'].isin(selected_months)]
        if 'All' not in selected_packages:
            filtered_df = filtered_df[filtered_df['Subscription Package'].isin(selected_packages)]
            
        # Get current year data
        current_year_df = filtered_df[filtered_df['Year'] == selected_year].copy()
        
        # Get previous year data safely
        prev_year = selected_year - 1
        prev_year_df = filtered_df[filtered_df['Year'] == prev_year] if prev_year in years else pd.DataFrame()
        
        # Calculate metrics with safe handling of previous year
        total_firms = current_year_df['Number of Firms'].sum()
        prev_firms = prev_year_df['Number of Firms'].sum() if not prev_year_df.empty else 0
        firms_growth = ((total_firms - prev_firms) / prev_firms * 100) if prev_firms > 0 else 0
        
        total_users = current_year_df['Number of Users'].sum()
        prev_users = prev_year_df['Number of Users'].sum() if not prev_year_df.empty else 0
        users_growth = ((total_users - prev_users) / prev_users * 100) if prev_users > 0 else 0
        
        avg_users_per_firm = total_users / total_firms if total_firms > 0 else 0
        prev_avg = (prev_users / prev_firms) if prev_firms > 0 else 0
        avg_growth = ((avg_users_per_firm - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
        
        total_revenue = current_year_df['Amount (GHS)'].sum()
        prev_revenue = prev_year_df['Amount (GHS)'].sum() if not prev_year_df.empty else 0
        revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        # Dashboard Title
        st.title(f"Firm Analysis ({selected_year})")
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Display metrics
        metrics = [
            (col1, "Total Firms", f"{total_firms:,}", firms_growth),
            (col2, "Total Users", f"{total_users:,}", users_growth),
            (col3, "Avg Users/Firm", f"{avg_users_per_firm:.1f}", avg_growth),
            (col4, "Total Revenue", f"GH₵{total_revenue:,.2f}", revenue_growth)
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
                
        # After metrics section, add visualizations
        
        # Main content layout
        left_col, right_col = st.columns([2, 1])
        
        with left_col:
            # Monthly Firms Trend
            st.markdown("### Monthly Firms Trend")
            
            # Prepare monthly firms trend data
            monthly_firms = filtered_df[
                df['Year'].isin([selected_year-1, selected_year])
            ].groupby(['Year', 'Month'], as_index=False)['Number of Firms'].sum()
            
            # Ensure proper month ordering
            monthly_firms['Month'] = pd.Categorical(monthly_firms['Month'], 
                                                  categories=MONTH_ORDER, 
                                                  ordered=True)
            monthly_firms = monthly_firms.sort_values(['Year', 'Month'])
            monthly_firms['Year'] = monthly_firms['Year'].astype(str)
            
            # Create firms trend chart
            firms_chart = alt.Chart(monthly_firms).mark_line(
                point=True,
                strokeWidth=3
            ).encode(
                x=alt.X('Month:N', 
                       sort=MONTH_ORDER, 
                       title=None),
                y=alt.Y('Number of Firms:Q', 
                       title='Number of Firms'),
                color=alt.Color('Year:N',
                              scale=alt.Scale(domain=[str(selected_year-1), str(selected_year)],
                                            range=['#94a3b8', '#22c55e']),
                              legend=alt.Legend(title="Year", orient="top")),
                tooltip=[
                    alt.Tooltip('Month:N'),
                    alt.Tooltip('Year:N'),
                    alt.Tooltip('Number of Firms:Q', title='Firms')
                ]
            ).properties(height=300)
            
            st.altair_chart(firms_chart, use_container_width=True)
            
            # Monthly Users Trend
            st.markdown("### Monthly Users Trend")
            
            # Prepare monthly users trend data
            monthly_users = filtered_df[
                df['Year'].isin([selected_year-1, selected_year])
            ].groupby(['Year', 'Month'], as_index=False)['Number of Users'].sum()
            
            # Ensure proper month ordering
            monthly_users['Month'] = pd.Categorical(monthly_users['Month'], 
                                                  categories=MONTH_ORDER, 
                                                  ordered=True)
            monthly_users = monthly_users.sort_values(['Year', 'Month'])
            monthly_users['Year'] = monthly_users['Year'].astype(str)
            
            # Create users trend chart
            users_chart = alt.Chart(monthly_users).mark_line(
                point=True,
                strokeWidth=3
            ).encode(
                x=alt.X('Month:N', 
                       sort=MONTH_ORDER, 
                       title=None),
                y=alt.Y('Number of Users:Q', 
                       title='Number of Users'),
                color=alt.Color('Year:N',
                              scale=alt.Scale(domain=[str(selected_year-1), str(selected_year)],
                                            range=['#94a3b8', '#3b82f6']),
                              legend=alt.Legend(title="Year", orient="top")),
                tooltip=[
                    alt.Tooltip('Month:N'),
                    alt.Tooltip('Year:N'),
                    alt.Tooltip('Number of Users:Q', title='Users')
                ]
            ).properties(height=300)
            
            st.altair_chart(users_chart, use_container_width=True)
            
            # Prepare monthly growth data
            monthly_growth = filtered_df.groupby(['Year', 'Month']).agg({
                'Number of Firms': 'sum',
                'Number of Users': 'sum',
                'Amount (GHS)': 'sum'
            }).reset_index()
            
            # Ensure proper month ordering
            monthly_growth['Month'] = pd.Categorical(monthly_growth['Month'], 
                                                   categories=MONTH_ORDER, 
                                                   ordered=True)
            monthly_growth = monthly_growth.sort_values(['Year', 'Month'])
            
            # Calculate YoY growth rates
            current_year_data = monthly_growth[monthly_growth['Year'] == selected_year]
            prev_year_data = monthly_growth[monthly_growth['Year'] == selected_year - 1]
            
            if not current_year_data.empty and not prev_year_data.empty:
                firms_growth = ((current_year_data['Number of Firms'].sum() - prev_year_data['Number of Firms'].sum()) / 
                                prev_year_data['Number of Firms'].sum() * 100) if prev_year_data['Number of Firms'].sum() > 0 else float('nan')
                users_growth = ((current_year_data['Number of Users'].sum() - prev_year_data['Number of Users'].sum()) / 
                                prev_year_data['Number of Users'].sum() * 100) if prev_year_data['Number of Users'].sum() > 0 else float('nan')
                revenue_growth = ((current_year_data['Amount (GHS)'].sum() - prev_year_data['Amount (GHS)'].sum()) / 
                                prev_year_data['Amount (GHS)'].sum() * 100) if prev_year_data['Amount (GHS)'].sum() > 0 else float('nan')
            else:
                firms_growth = float('nan')
                users_growth = float('nan')
                revenue_growth = float('nan')
            
            # Growth Analysis Section
            st.markdown("""
                ### Growth Analysis
                <span title="Compares current period with previous period to show growth trends">
                    ℹ️
                </span>
            """, unsafe_allow_html=True)
            
            # Create three columns for growth metrics
            g1, g2, g3 = st.columns(3)
            
            # Helper function to determine growth color
            def get_growth_color(value):
                if pd.isna(value):
                    return "#6b7280"  # Gray for NaN
                return "#22c55e" if value > 0 else "#ef4444"  # Green for positive, Red for negative
            
            with g1:
                st.markdown(f"""
                    <div class="metric-card" style="padding: 1rem; text-align: center;">
                        <div title="Year-over-Year growth in number of firms">
                            <div class="metric-label" style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.5rem;">
                                Firms Growth (YoY)
                            </div>
                            <div class="metric-value" style="font-size: 1.5rem; font-weight: 600; color: {get_growth_color(firms_growth)};">
                                {f"{firms_growth:+.1f}%" if not pd.isna(firms_growth) else "NaN"}
                            </div>
                            <div class="metric-trend" style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">
                                vs Previous Year
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
            with g2:
                st.markdown(f"""
                    <div class="metric-card" style="padding: 1rem; text-align: center;">
                        <div title="Year-over-Year growth in number of users">
                            <div class="metric-label" style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.5rem;">
                                Users Growth (YoY)
                            </div>
                            <div class="metric-value" style="font-size: 1.5rem; font-weight: 600; color: {get_growth_color(users_growth)};">
                                {f"{users_growth:+.1f}%" if not pd.isna(users_growth) else "NaN"}
                            </div>
                            <div class="metric-trend" style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">
                                vs Previous Year
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
            with g3:
                st.markdown(f"""
                    <div class="metric-card" style="padding: 1rem; text-align: center;">
                        <div title="Year-over-Year growth in revenue">
                            <div class="metric-label" style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.5rem;">
                                Revenue Growth (YoY)
                            </div>
                            <div class="metric-value" style="font-size: 1.5rem; font-weight: 600; color: {get_growth_color(revenue_growth)};">
                                {f"{revenue_growth:+.1f}%" if not pd.isna(revenue_growth) else "NaN"}
                            </div>
                            <div class="metric-trend" style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">
                                vs Previous Year
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Monthly Revenue Trend
            st.markdown("### Monthly Revenue Trend")
            
            if not current_year_data.empty:
                growth_chart = alt.Chart(current_year_data).mark_area(
                    opacity=0.4,
                    color='#22c55e'
                ).encode(
                    x=alt.X('Month:N', sort=MONTH_ORDER),
                    y=alt.Y('Amount (GHS):Q', 
                           axis=alt.Axis(format=',.0f'),
                           title='Monthly Revenue (GH₵)'),
                    tooltip=[
                        alt.Tooltip('Month:N'),
                        alt.Tooltip('Amount (GHS):Q', format=',.2f', title='Revenue (GH₵)'),
                        alt.Tooltip('Number of Firms:Q', title='Firms'),
                        alt.Tooltip('Number of Users:Q', title='Users')
                    ]
                ).properties(height=300)
                
                # Add trend line
                trend_line = alt.Chart(current_year_data).mark_line(
                    color='#15803d',
                    strokeWidth=3
                ).encode(
                    x=alt.X('Month:N', sort=MONTH_ORDER),
                    y=alt.Y('Amount (GHS):Q')
                )
                
                # Combine area and trend line
                final_chart = (growth_chart + trend_line).properties(
                    title=alt.Title(
                        text='Monthly Revenue with Trend',
                        subtitle='Area shows revenue distribution across months'
                    )
                )
                
                st.altair_chart(final_chart, use_container_width=True)
            else:
                st.info("No revenue data available for the selected period.")
        
        with right_col:
            # Package Metrics Overview
            st.markdown("### Package Metrics")
            
            # Get data for current year and respect filters
            package_dist = filtered_df[filtered_df['Year'] == selected_year].groupby('Subscription Package').agg({
                'Number of Firms': 'sum',
                'Number of Users': 'sum',
                'Amount (GHS)': 'sum'
            }).reset_index()
            
            # Calculate totals (use 0 if no data)
            total_firms = package_dist['Number of Firms'].sum() if not package_dist.empty else 0
            total_users = package_dist['Number of Users'].sum() if not package_dist.empty else 0
            total_revenue = package_dist['Amount (GHS)'].sum() if not package_dist.empty else 0
            
            # Calculate metrics (use NaN for undefined ratios)
            users_per_firm = total_users / total_firms if total_firms > 0 else float('nan')
            revenue_per_user = total_revenue / total_users if total_users > 0 else float('nan')
            
            # Format metrics with proper handling of NaN
            users_per_firm_display = f"{users_per_firm:.1f}" if not pd.isna(users_per_firm) else "NaN"
            revenue_per_user_display = f"GH₵{revenue_per_user:,.2f}" if not pd.isna(revenue_per_user) else "NaN"
            
            # Create dynamic card title based on selected packages
            if not package_dist.empty and len(package_dist) == 1:
                card_title = package_dist['Subscription Package'].iloc[0]
            else:
                card_title = "All Packages"
            
            st.markdown(f"""
                <div class="metric-card" style="margin-bottom: 20px;">
                    <div style="font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 15px;">
                        {card_title}
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div title="Total number of firms subscribed to this package">
                            <div class="metric-label">Firms</div>
                            <div class="metric-value" style="font-size: 18px;">
                                {total_firms if total_firms > 0 else 'NaN'}
                            </div>
                        </div>
                        <div title="Total number of users across all subscribed firms">
                            <div class="metric-label">Users</div>
                            <div class="metric-value" style="font-size: 18px;">
                                {total_users if total_users > 0 else 'NaN'}
                            </div>
                        </div>
                        <div title="Average number of users per subscribed firm">
                            <div class="metric-label">Users/Firm</div>
                            <div class="metric-value" style="font-size: 18px;">
                                {users_per_firm_display}
                            </div>
                        </div>
                        <div title="Average revenue generated per user (Total Revenue ÷ Total Users)">
                            <div class="metric-label">Revenue/User</div>
                            <div class="metric-value" style="font-size: 18px;">
                                {revenue_per_user_display}
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Add a divider
            st.markdown("<hr style='margin: 30px 0'>", unsafe_allow_html=True)
            
            # Package Distribution (Donut Chart)
            st.markdown("### Package Distribution")
            
            # Create donut chart with tooltips
            donut = alt.Chart(package_dist).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field='Number of Firms', type='quantitative'),
                color=alt.Color('Subscription Package:N', 
                              scale=alt.Scale(scheme='greens')),
                tooltip=[
                    alt.Tooltip('Subscription Package:N', title='Package'),
                    alt.Tooltip('Number of Firms:Q', title='Total Firms'),
                    alt.Tooltip('Number of Users:Q', title='Total Users'),
                    alt.Tooltip('Amount (GHS):Q', format=',.2f', title='Total Revenue (GH₵)'),
                    alt.Tooltip('Percentage:Q', format='.1f', title='% of Total Firms')
                ]
            ).properties(height=250)
            
            st.altair_chart(donut, use_container_width=True)
            
            # Revenue per User by Package
            st.markdown("### Revenue per User")
            
            revenue_per_user_chart = alt.Chart(package_dist).mark_bar().encode(
                y=alt.Y('Subscription Package:N', 
                       sort='-x',
                       title=None),
                x=alt.X('Amount (GHS):Q',
                       title='Revenue (GH₵)'),
                color=alt.Color('Subscription Package:N',
                              scale=alt.Scale(scheme='greens'),
                              legend=None),
                tooltip=[
                    alt.Tooltip('Subscription Package:N', title='Package'),
                    alt.Tooltip('Amount (GHS):Q', format=',.2f', title='Total Revenue (GH₵)'),
                    alt.Tooltip('Number of Users:Q', title='Total Users'),
                    alt.Tooltip('Revenue per User:Q', format=',.2f', 
                              title='Revenue per User (GH₵)')
                ]
            ).properties(height=200)
            
            st.altair_chart(revenue_per_user_chart, use_container_width=True)

        # After all visualizations, add a divider
        st.markdown("---")
        
        # Create two columns for Glossary and Data View
        bottom_left, bottom_right = st.columns([1, 1])
        
        with bottom_left:
            with st.expander("📚 Glossary"):
                st.markdown("""
                    ### Metrics Explained
                    
                    #### Basic Metrics
                    - **Firms**: Number of companies subscribed to the package
                    - **Users**: Total number of user accounts across all firms
                    - **Users/Firm**: Average number of users per subscribed firm
                    - **Revenue/User**: Average revenue generated per user
                    
                    #### Growth Metrics
                    - **YoY Growth**: Year-over-Year percentage change
                    - **Monthly Trend**: Month-by-month progression of metrics
                    
                    #### Package Distribution
                    - Shows how firms are distributed across different subscription packages
                    - Includes percentage of total firms for each package
                    
                    #### Calculations
                    - Users/Firm = Total Users ÷ Total Firms
                    - Revenue/User = Total Revenue ÷ Total Users
                    - Growth % = ((Current - Previous) ÷ Previous) × 100
                """)
        
        with bottom_right:
            with st.expander("🔍 View Raw Data"):
                # Add data filters
                col1, col2 = st.columns(2)
                with col1:
                    view_year = st.selectbox("Select Year", 
                                           options=sorted(filtered_df['Year'].unique()),
                                           key='data_year')
                with col2:
                    view_package = st.multiselect("Select Package(s)",
                                                options=filtered_df['Subscription Package'].unique(),
                                                default=filtered_df['Subscription Package'].unique(),
                                                key='data_package')
                
                # Filter data based on selection
                view_data = filtered_df[
                    (filtered_df['Year'] == view_year) & 
                    (filtered_df['Subscription Package'].isin(view_package))
                ]
                
                # Show filtered data
                st.dataframe(
                    view_data,
                    column_config={
                        "Amount (GHS)": st.column_config.NumberColumn(
                            "Amount (GHS)",
                            format="GH₵%.2f"
                        )
                    },
                    hide_index=True
                )
                
                # Add download button
                csv = view_data.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download Data",
                    csv,
                    "firm_analysis.csv",
                    "text/csv",
                    key='download-csv'
                )

        # Optional: Add footer with timestamp
        st.markdown("---")
        st.markdown(f"""
            <div style="text-align: center; color: #6b7280; font-size: 0.875rem;">
                Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
else:
    # Welcome message
    st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h2>👋 Welcome to the Firm Analysis Dashboard!</h2>
            <p style="font-size: 18px;">Upload your firm data file using the sidebar to get started</p>
            <p>Required columns: Month, Year, Subscription Package, Number of Users, Number of Firms, Amount (GHS)</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Features section
    st.markdown("### 📊 What You Can Analyze")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <h4>📈 Firm Growth Trends</h4>
                <p>Track the number of firms and their growth over time</p>
            </div>
            
            <div class="feature-card">
                <h4>💰 Revenue Metrics</h4>
                <p>Monitor revenue per firm and per user</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class="feature-card">
                <h4>👥 User Distribution</h4>
                <p>Analyze user counts across different firms and packages</p>
            </div>
            
            <div class="feature-card">
                <h4>📦 Package Analysis</h4>
                <p>Compare performance across different subscription packages</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Getting Started section
    st.markdown("### 🎯 Quick Start Guide")
    
    st.info("""
        1. Prepare your firm data file (CSV or Excel format)
        2. Use the sidebar uploader to import your data
        3. Apply filters to focus on specific time periods or packages
        4. Explore the interactive visualizations and insights
    """)
    
    # Additional tips
    st.markdown("### 💡 Tips")
    tips_col1, tips_col2 = st.columns(2)
    
    with tips_col1:
        st.info("""
            **Analysis Tips:**
            - Compare year-over-year performance
            - Track monthly firm growth
            - Identify popular packages
            - Monitor user distribution
        """)
    
    with tips_col2:
        st.info("""
            **Best Practices:**
            - Regularly update your data
            - Use filters to focus on specific periods
            - Export insights for reporting
            - Check the glossary for metric definitions
        """)