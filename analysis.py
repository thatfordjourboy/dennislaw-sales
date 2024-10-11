import streamlit as st
import pandas as pd
import altair as alt

# Streamlit configuration
st.set_page_config(page_title="Dennislaw Sales Dashboard (2023-2024)", page_icon="📉", layout="wide")
st.title("Dennislaw Sales Analysis - 2023-2024")

# File upload prompts for solo and firm data
st.sidebar.header("Upload Data Files")
solo_file = st.sidebar.file_uploader("Upload Solo Data File", type=["xlsx"])

def colored_metric(label, value, delta=None, background_color="lightgray", text_color="black"):
    delta_str = f'<span style="color: {text_color}; font-size: 1.2rem;">{delta}</span>' if delta else ""
    st.markdown(
        f"""
        <div style="
            background-color: {background_color}; 
            padding: 10px; 
            border-radius: 8px; 
            display: inline-block;
            color: {text_color};
            font-size: 1.5rem;">
            {label} <strong>{value}</strong> {delta_str}
        </div>
        """,
        unsafe_allow_html=True
    )

# Load data only if solo data file is uploaded
if solo_file:
    try:
        # Read the uploaded Excel files into DataFrames
        solo_data = pd.read_excel(solo_file)
        # firm_data = pd.read_excel(firm_file)
        
        # Correct column name typo and fill missing values with 0
        solo_data.rename(columns={"2023 Subsciptions": "2023 Subscriptions"}, inplace=True)
        solo_data.fillna(0, inplace=True)
        
        # Clean up column names to remove any leading/trailing spaces
        solo_data.columns = solo_data.columns.str.strip()
        
        # Ensure the 'Month' column is in the correct chronological order
        months_order = [
            'January', 'February', 'March', 'April', 'May', 'June', 
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        solo_data['Month'] = pd.Categorical(solo_data['Month'], categories=months_order, ordered=True)
        
        # Sort data by 'Month'
        solo_data = solo_data.sort_values('Month')
        
        sum_2023 = float(solo_data['2023 Sales'].sum())
        sum_2024 = float(solo_data['2024 Sales'].sum())

        # Sidebar filters for user input
        st.sidebar.header("Filters")
        subscription_type = st.sidebar.selectbox("Select Subscription Type:", ["Individual", "Firm"])
        subscription_package = st.sidebar.selectbox(
            "Select Subscription Package:", 
            solo_data['Subscription Package'].unique() if subscription_type == "Individual" else print("That's all folks!")
            # solo_data['Subscription Package'].unique() if subscription_type == "Individual" else firm_data['Subscription Package'].unique()
        )
        
        # Add "All" option for month selection
        selected_months = st.sidebar.multiselect(
            "Select Months:", 
            options=["All"] + months_order, 
            default=["All"]
        )
        
        # Filter data based on subscription package and selected months
        if "All" in selected_months or not selected_months:
            # Use all months if "All" is selected
            filtered_data = (solo_data[solo_data['Subscription Package'] == subscription_package]
                             if subscription_type == "Individual"
                             else firm_data[firm_data['Subscription Package'] == subscription_package])
        else:
            # Filter data for the selected months
            filtered_data = (solo_data[solo_data['Month'].isin(selected_months) & 
                                       (solo_data['Subscription Package'] == subscription_package)]
                             if subscription_type == "Individual"
                             else firm_data[firm_data['Month'].isin(selected_months) & 
                                            (firm_data['Subscription Package'] == subscription_package)])
        
        # Calculate metrics for 2023 and 2024 by summing the filtered values
        total_revenue_2023 = filtered_data['2023 Sales'].sum()
        total_revenue_2024 = filtered_data['2024 Sales'].sum()
        total_subscriptions_2023 = int(filtered_data['2023 Subscriptions'].sum())
        total_subscriptions_2024 = int(filtered_data['2024 Subscriptions'].sum())
        
        # Calculate growth for revenue and subscriptions from 2023 to 2024
        revenue_growth = ((total_revenue_2024 - total_revenue_2023) / total_revenue_2023 * 100) if total_revenue_2023 else 0
        subscription_growth = ((total_subscriptions_2024 - total_subscriptions_2023) / total_subscriptions_2023 * 100) if total_subscriptions_2023 else 0
        
        # Main content layout
        col1, col2 = st.columns([2, 1])

        # Display Key Metrics & KPIs
        with col1:
            st.subheader("Key Metrics & KPIs")
            
            # display total sales for 2023 and 2024
            col1a, col1b = st.columns(2)

            with col1a:
                 colored_metric("Total Revenue for 2023\n\n", 
                                f"GHS {sum_2023}", 
                                background_color="#FF4B4B", 
                                text_color="#FFFFFF")
            with col1b:
                 colored_metric("Total Revenue for 2024\n\n", 
                                f"GHS {sum_2024}", 
                                background_color="#FF4B4B", 
                                text_color="#FFFFFF")
           

            col1a.metric(f"Total Revenue for {subscription_package} - 2023", 
                        f"GHS {total_revenue_2023:,.2f}")
            col1b.metric(f"Total {subscription_package} Subscriptions in 2023", 
                        f"{total_subscriptions_2023:,}")

            # Display metrics for 2024 with growth indicators
            col1a, col1b = st.columns(2)
            col1a.metric(f"Total Revenue for {subscription_package} 2024", 
                f"GHS {total_revenue_2024:,.2f}", 
                delta=f"{revenue_growth:.2f}%" if revenue_growth != 0 else "No Change"
            )
            col1b.metric(
                f"Total {subscription_package} Subscriptions in 2024", 
                f"{total_subscriptions_2024:,}", 
                delta=f"{subscription_growth:.2f}%" if subscription_growth != 0 else "No Change"
            )

            # Determine chart type based on the number of selected months
            if len(selected_months) == 1 and "All" not in selected_months:
                # Use bar charts if only one month is selected
                st.subheader("Revenue for Selected Month")
                revenue_chart = alt.Chart(filtered_data).transform_fold(
                    ['2023 Sales', '2024 Sales'],
                    as_=['Year', 'Sales']
                ).mark_bar().encode(
                    x='Year:N',
                    y=alt.Y('Sales:Q', title='Sales (GHS)'),
                    color='Year:N'
                ).properties(title=f'Revenue for {selected_months[0]}')
                st.altair_chart(revenue_chart, use_container_width=True)

                st.subheader("Subscriptions for Selected Month")
                subscription_chart = alt.Chart(filtered_data).transform_fold(
                    ['2023 Subscriptions', '2024 Subscriptions'],
                    as_=['Year', 'Subscriptions']
                ).mark_bar().encode(
                    x='Year:N',
                    y=alt.Y('Subscriptions:Q', title='Subscriptions'),
                    color='Year:N'
                ).properties(title=f'Subscriptions for {selected_months[0]}')
                st.altair_chart(subscription_chart, use_container_width=True)
            else:
                # Use line charts for multiple months or all months
                st.subheader("Revenue Comparison")
                revenue_comparison_chart = alt.Chart(filtered_data).transform_fold(
                    ['2023 Sales', '2024 Sales'],
                    as_=['Year', 'Sales']
                ).mark_line().encode(
                    x='Month',
                    y=alt.Y('Sales:Q', title='Sales (GHS)'),
                    color='Year:N'
                ).properties(title='Revenue Comparison: 2023 vs 2024')
                st.altair_chart(revenue_comparison_chart, use_container_width=True)

                st.subheader("Subscription Comparison")
                subscription_comparison_chart = alt.Chart(filtered_data).transform_fold(
                    ['2023 Subscriptions', '2024 Subscriptions'],
                    as_=['Year', 'Subscriptions']
                ).mark_line().encode(
                    x='Month',
                    y=alt.Y('Subscriptions:Q', title='Subscriptions'),
                    color='Year:N'
                ).properties(title='Subscription Comparison: 2023 vs 2024')
                st.altair_chart(subscription_comparison_chart, use_container_width=True)

        # Display Revenue Breakdown in the second column (1/3 of the width)
        with col2:
            st.subheader("Revenue Breakdown")
            revenue_breakdown = alt.Chart(filtered_data).transform_fold(
                ['2023 Sales', '2024 Sales'],
                as_=['Year', 'Sales']
            ).mark_bar().encode(
                x='Month',
                y='Sales:Q',
                color='Year:N'
            ).properties(title='Monthly Revenue Breakdown')
            st.altair_chart(revenue_breakdown, use_container_width=True)

        # Detailed Data Table (Full-width below the charts)
        st.subheader("Detailed Data Table")
        st.dataframe(filtered_data)

        # Footer
        st.write("Last Updated: October 2024")

    except Exception as e:
        st.error(f"Relax, ano reach there yet!")
else:
    st.info("Please upload the file for Solo revenue to proceed. Expected format is .xlsx")
