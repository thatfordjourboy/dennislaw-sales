import streamlit as st
import pandas as pd
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime

# Constants
MONTH_ORDER = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

@dataclass
class FilterState:
    """Class to handle filter state management"""
    year: Optional[int] = None
    months: List[str] = field(default_factory=list)
    packages: List[str] = field(default_factory=list)

class StateManager:
    """Class to manage application state"""
    
    @staticmethod
    def init_session_state():
        """Initialize all session state variables"""
        defaults = {
            'solo_data': None,
            'filter_state': FilterState(),
            'month_filter_reset': False,
            'package_filter_reset': False,
            'last_upload_time': None,
            'data_loaded': False
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

    @staticmethod
    def reset_filters():
        """Reset all filters to default state"""
        st.session_state.filter_state = FilterState()
        st.session_state.month_filter_reset = True
        st.session_state.package_filter_reset = True

    @staticmethod
    def update_filter_state(year: Optional[int] = None, 
                            months: Optional[List[str]] = None,
                            packages: Optional[List[str]] = None):
        """Update filter state with new values"""
        if year is not None:
            st.session_state.filter_state.year = year
        if months is not None:
            st.session_state.filter_state.months = months
        if packages is not None:
            st.session_state.filter_state.packages = packages

    @staticmethod
    def get_filtered_data() -> pd.DataFrame:
        """Get data filtered according to current filter state"""
        if st.session_state.solo_data is None:
            return pd.DataFrame()

        df = st.session_state.solo_data
        filter_state = st.session_state.filter_state

        if filter_state.year:
            df = df[df['Year'] == filter_state.year]
        if filter_state.months:
            df = df[df['Month'].isin(filter_state.months)]
        if filter_state.packages:
            df = df[df['Subscription Package'].isin(filter_state.packages)]

        return df if not df.empty else pd.DataFrame(columns=df.columns)

    @staticmethod
    def load_data(uploaded_file) -> bool:
        """Load and validate uploaded data"""
        try:
            # Load the file based on its extension
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Validate required columns
            required_columns = [
                'Month', 'Year', 'Subscription Package',
                'Number of Subscriptions', 'Amount (GHS)'
            ]
            if not all(col in df.columns for col in required_columns):
                st.error("Missing required columns in the uploaded file")
                return False

            # Ensure correct data types for key columns
            if not pd.api.types.is_integer_dtype(df['Year']):
                st.error("Year column must contain integers")
                return False
            if not pd.api.types.is_numeric_dtype(df['Amount (GHS)']):
                st.error("Amount (GHS) column must contain numeric values")
                return False

            # Ensure Month values match MONTH_ORDER
            if not set(df['Month']).issubset(MONTH_ORDER):
                st.error("Invalid month names in data. Please ensure they match standard month names.")
                return False

            # Save data to session state
            st.session_state.solo_data = df
            st.session_state.data_loaded = True
            st.session_state.last_upload_time = datetime.now()
            return True

        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return False

    @staticmethod
    def clear_data():
        """Clear all data and reset state"""
        st.session_state.solo_data = None
        st.session_state.data_loaded = False
        st.session_state.filter_state = FilterState()
        st.session_state.last_upload_time = None

    @staticmethod
    def get_available_filters() -> Dict[str, List[Any]]:
        """Get available filter options based on current data"""
        if st.session_state.solo_data is None:
            return {
                'years': [],
                'months': [],
                'packages': []
            }

        df = st.session_state.solo_data
        return {
            'years': sorted(df['Year'].unique()) if 'Year' in df.columns else [],
            'months': sorted(df['Month'].unique(), key=lambda x: MONTH_ORDER.index(x)) if 'Month' in df.columns else [],
            'packages': sorted(df['Subscription Package'].unique()) if 'Subscription Package' in df.columns else []
        }

    @staticmethod
    def get_comparison_data(current_year: int) -> Dict[str, pd.DataFrame]:
        """Get current and previous year data for comparison"""
        if st.session_state.solo_data is None:
            return {'current': pd.DataFrame(), 'previous': pd.DataFrame()}

        df = st.session_state.solo_data
        return {
            'current': df[df['Year'] == current_year],
            'previous': df[df['Year'] == current_year - 1]
        }

def with_state_management(func):
    """Decorator to ensure state is initialized before running a component"""
    def wrapper(*args, **kwargs):
        try:
            StateManager.init_session_state()
        except Exception as e:
            st.error(f"State initialization failed: {str(e)}")
        return func(*args, **kwargs)
    return wrapper

# Create a convenience function for direct import
def init_session_state():
    """Convenience function to initialize session state"""
    StateManager.init_session_state()
