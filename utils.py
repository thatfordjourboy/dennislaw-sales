import streamlit as st
import pandas as pd
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from functools import wraps

# Constants
MONTH_ORDER = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

def with_state_management(func):
    """Decorator to ensure session state is initialized"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        StateManager.init_session_state()
        return func(*args, **kwargs)
    return wrapper

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
            'firm_data': None,
            'solo_data_loaded': False,
            'firm_data_loaded': False,
            'month_filter': ['All'],
            'package_filter': ['All'],
            'prev_month_selection': ['All'],
            'prev_package_selection': ['All'],
            'firm_year_filter': None,
            'firm_month_filter': ['All'],
            'firm_package_filter': ['All']
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

    @staticmethod
    def load_data(uploaded_file, data_type='solo'):
        """Load data from uploaded file"""
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            required_columns = ['Month', 'Year', 'Subscription Package', 
                              'Number of Subscriptions', 'Amount (GHS)']
            
            if all(col in df.columns for col in required_columns):
                if data_type == 'solo':
                    st.session_state.solo_data = df
                    st.session_state.solo_data_loaded = True
                else:
                    st.session_state.firm_data = df
                    st.session_state.firm_data_loaded = True
                return True
            else:
                st.error("Upload failed: Missing required columns")
                return False
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return False

    @staticmethod
    def clear_data(data_type='solo'):
        """Clear data from session state"""
        if data_type == 'solo':
            st.session_state.solo_data = None
            st.session_state.solo_data_loaded = False
        else:
            st.session_state.firm_data = None
            st.session_state.firm_data_loaded = False
