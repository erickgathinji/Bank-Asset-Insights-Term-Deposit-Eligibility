import streamlit as st
import base64
import os
import pandas as pd
import streamlit.components.v1 as components
from render_css import *
from bank_app_logic import *
from PIL import Image

favicon = Image.open("bank_web_app/static/eryx-favicon.png")

# App Name
st.set_page_config(
    page_title="Erick | Bank Asset Insights AI Model",
    page_icon=favicon,
    layout="centered"
)

apply_css()    

# configure link
if "model" not in st.query_params:
    st.query_params["model"] = "bank-asset-insights"

# Session State for Navigation
if "step" not in st.session_state:
    st.session_state.step = 1

if "max_step" not in st.session_state:
    st.session_state.max_step = 1

# Update max_step when move forward
if st.session_state.step > st.session_state.max_step:
    st.session_state.max_step = st.session_state.step
    

def next_step():
    st.session_state.step += 1
    # Update max_step to "unlock" the current page for jumping back
    if st.session_state.step > st.session_state.max_step:
        st.session_state.max_step = st.session_state.step

def prev_step():
    st.session_state.step -= 1

def go_to_step(step_index):
    st.session_state.step = step_index

def pagination():
    # Run validation
    valid = is_current_page_valid()
        
    st.markdown("""
            <style>
                
                /* Prevent the main content from being hidden behind the bar */
                .main .block-container {
                    padding-bottom: 120px !important;
                }
        """, unsafe_allow_html=True)
       
    
    # Columns: Back | Progress Numbers | Next
    nav_col1, nav_spacer, nav_col2 = st.columns([1, 2, 1])

    with nav_col1:
        if st.session_state.step > 1:
            st.button("◄ Back", on_click=prev_step, use_container_width=True)

    with nav_spacer:
        # Instead of buttons, use a simple text indicator that works on any screen
        st.markdown(f"", unsafe_allow_html=True)
    with nav_col2:
        if st.session_state.step < 6:
            
            if st.session_state.step == 1:
                label = "Start ►"
            elif st.session_state.step == 5:
                label = "Submit"
            else:
                label = "Next ►"
            
            # Disable the button if the current page isn't valid
            st.button(label, on_click=next_step, type="primary", 
                        use_container_width=True, disabled=not valid)
 
    # Styling to ensure the buttons align nicely
    st.markdown("""
        <style>
        div[data-testid="column"]:nth-of-type(1) button { text-align: left; }
        div[data-testid="column"]:nth-of-type(3) button { text-align: right; }
        </style>
        """, unsafe_allow_html=True)
    
# Header/Title
st.title("Bank Asset Insights: Term Deposit Eligibility",  anchor=False)
progress_text = f"Step {st.session_state.step} of 6"

# min() ensures the value never exceeds 1.0 (100%)
st.progress(min(st.session_state.step / 6, 1.0))
st.write(f"**{progress_text}**")

# home view
if st.session_state.step == 1:   
    # load img
    static_folder_path = "bank_web_app/static"
    hero_image_name = "bank_deposit.webp"

    # locate the hero image
    # check if strings are actually provided
    img_tag = ""

    try:
        if static_folder_path and hero_image_name:
            image_path = os.path.join(static_folder_path, hero_image_name)
            
            if os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    data = base64.b64encode(f.read()).decode()
                
                # Create the HTML tag
                img_tag = f'<img src="data:image/webp;base64,{data}" class="hero-img" style="width:100%;">'
                
                # render
                st.markdown(img_tag, unsafe_allow_html=True)
            else:
                st.error(f"File not found: {image_path}")
    except Exception as e:
        st.error(f"Error: {e}")

    # Description
    st.markdown("""        
        This web app predicts the likelihood of a client subscribing to a bank term deposit based on demographic, financial, and historical context dimensions. 
        """)
    with st.expander("About The Bank Assets Insights Model"):
        st.write("""
            This AI model aims to empower financial institutions to prioritize high-potential leads with scientific accuracy.
        
            It can be integrated directly into existing **CRM systems**, **Mobile Banking Apps**, or **Customer Portals** to provide real-time, reliable eligibility scores at the point of contact.
        """)
    st.markdown("""
        Bulk score up to 1,000 profiles simultaneously and download results efficiently.
    """)
    
    st.caption("Detailed feature definitions and dataset source can be found [here](https://www.kaggle.com/datasets/sushant097/bank-marketing-dataset-full).")
    
    footer()

# COLLECTING DATA
# Values derived from model training data - means and modes
FALLBACK_DEFAULTS = {
    'age': 41,
    'job': 'management',
    'marital': 'married',
    'education': 'secondary',
    'balance': 1204,
    'housing': 'yes',
    'loan': 'no',
    'default': 'no',
    'contact': 'cellular',
    'month': 'may',
    'day': 16,
    'duration': 256,
    'campaign': 3,
    'poutcome': 'unknown',
    'pdays': 22,
    'previous': 0
}


feature_keys = [
    'age', 'job', 'marital', 'education', 'balance', 'loan', 
    'housing', 'default', 'contact', 'day', 'month', 
    'duration', 'campaign', 'poutcome', 'pdays', 'previous'
]

categorical = ['job', 'marital', 'education', 'loan', 'housing', 'default', 'contact', 'month', 'poutcome']

for key in feature_keys:
    # Use val_ prefix to match sync and validation logic
    master_key = f"val_{key}"
    if master_key not in st.session_state:
        if key in categorical:
            st.session_state[master_key] = "Select..."
        else:
            st.session_state[master_key] = None
    
    if f"unsure_{key}" not in st.session_state:
        st.session_state[f"unsure_{key}"] = False

# batch initialization section
if "val_unlock_batch" not in st.session_state:
    st.session_state.val_unlock_batch = False

# for the persistent dataframe itself
if "persistent_batch_df" not in st.session_state:
    st.session_state.persistent_batch_df = None


# This saves the widget's temporary data into "val_" master keys
def sync_state(key, is_checkbox=False):
    if is_checkbox:
        # Save the checkbox state to the unsure_ permanent key
        st.session_state[f"unsure_{key}"] = st.session_state[f"temp_unsure_{key}"]
    else:
        # Check if this is the batch toggle
        if key == "unlock_batch":
            st.session_state[f"val_{key}"] = st.session_state[f"temp_{key}"]
        else:
            # Standard logic for age, job, etc.
            st.session_state[f"val_{key}"] = st.session_state[key]
    
    

# ensure data is filled
def is_current_page_valid():
    fields_per_step = {
        1: [],
        2: ["age", "job", "marital", "education"],
        3: ["balance", "loan", "housing", "default"],
        4: ["contact", "day", "month", "duration", "campaign"],
        5: ["poutcome", "pdays", "previous"],
        6: []
    }
    
    current_fields = fields_per_step.get(st.session_state.step, [])
    
    for f in current_fields:
        # Check the permanent master storage
        val = st.session_state.get(f"val_{f}") 
        is_unsure = st.session_state.get(f"unsure_{f}", False)
        
        if not is_unsure:
            if val is None or val == "Select...":
                return False
    return True

# Personal Profile ---
if st.session_state.step == 2:
    st.subheader("Personal Information", anchor=False)
    st.markdown("Please complete all fields or select 'Not sure' to proceed.")
    
    # Row 1 - age and job
    r1_col1, r1_col2 = st.columns(2)

    with r1_col1:
        input_c, check_c = st.columns([3, 2]) 
                
        is_unsure_age = check_c.checkbox(
            "Not sure", 
            value=st.session_state.unsure_age, 
            key="temp_unsure_age",             
            on_change=sync_state, 
            args=("age", True)                 
        )
        
        input_c.number_input(
            "Age", 18, 100, 
            value=st.session_state.val_age, 
            placeholder="Enter...", 
            key="age", 
            on_change=sync_state, 
            args=("age",), 
            disabled=is_unsure_age
        )
        # check_c.markdown("###")          
        
    with r1_col2:
        input_c, check_c = st.columns([3, 2])
        
        is_unsure_job = check_c.checkbox(
                            "Not sure", 
                            value=st.session_state.unsure_job, 
                            key="temp_unsure_job",             
                            on_change=sync_state, 
                            args=("job", True)                 
                        )
        
        job_opts = ["Select...", 'admin', 'blue-collar', 'entrepreneur', 'housemaid', 'management', 'retired', 'self-employed', 'services', 'student', 'technician', 'unemployed', 'unknown']

        job_idx = job_opts.index(st.session_state.val_job) if st.session_state.val_job in job_opts else 0

        input_c.selectbox(
            "Occupation", job_opts, 
            index=job_idx, 
            key="job", 
            on_change=sync_state, 
            args=("job",),
            disabled=is_unsure_job
        )
        # check_c.markdown("###")  
        
    # Row 2 - Marital Status and Education
    r2_col1, r2_col2 = st.columns(2)

    with r2_col1:
        input_c, check_c = st.columns([3, 2])
                
        is_unsure_marital = check_c.checkbox(
                        "Not sure", 
                        value=st.session_state.unsure_marital, 
                        key="temp_unsure_marital",             
                        on_change=sync_state, 
                        args=("marital", True)                 
                    )
        
        marital_opts = ["Select...", "married", "single", "divorced"]
        
        marital_idx = marital_opts.index(st.session_state.val_marital) if st.session_state.val_marital in marital_opts else 0
        
        input_c.selectbox(
            "Marital Status", marital_opts, 
            index=marital_idx, 
            key="marital", 
            on_change=sync_state, 
            args=("marital",),
            disabled=is_unsure_marital
        )
        # check_c.markdown("###")  

    with r2_col2:  
        input_c, check_c = st.columns([3, 2])
                
        is_unsure_education = check_c.checkbox(
                    "Not sure", 
                    value=st.session_state.unsure_education, 
                    key="temp_unsure_education",             
                    on_change=sync_state, 
                    args=("education", True)                 
                )
                
        edu_opts = ["Select...", "primary", "secondary", "tertiary", "unknown"]
        
        curr_edu_idx = edu_opts.index(st.session_state.val_education) if st.session_state.val_education in edu_opts else 0
        
        input_c.selectbox(
            "Highest Education Level", edu_opts, 
            index=curr_edu_idx, 
            key="education", 
            on_change=sync_state, 
            args=("education",),
            disabled=is_unsure_education
        )
        # check_c.markdown("###")  
     
   
# Financial Situation
elif st.session_state.step == 3:
    st.subheader("Financial Profile", anchor=False)
    st.markdown("Please complete all fields or select 'Not sure' to proceed.")
    
    # Row 1 - balance and loan
    r1_col1, r1_col2 = st.columns(2)
    with r1_col1:
        input_c, check_c = st.columns([3,2])
        
        is_unsure_balance = check_c.checkbox(
            "Not sure", 
            value=st.session_state.unsure_balance,
            key="temp_unsure_balance",
            on_change = sync_state,
            args=("balance", True)
        )
        
        input_c.number_input(
            "Average Yearly Balance", -8100, 100000, 
            value=st.session_state.val_balance, 
            placeholder="Enter...", 
            key="balance",
            on_change = sync_state,
            args=("balance",),
            help="Based on user's bank profile/statements in (€).",
            disabled = is_unsure_balance
            )
        # check_c.markdown("###")  
        
    with r1_col2:
        input_c, check_c = st.columns([3,2])
        
        is_unsure_loan = check_c.checkbox(
            "Not sure", 
            value = st.session_state.unsure_loan,
            key = "temp_unsure_loan",
            on_change = sync_state,
            args = ("loan", True)            
        )
        
        loan_opts = ["Select...", "yes", "no"]
        
        loan_idx = loan_opts.index(st.session_state.val_loan) if st.session_state.val_loan in loan_opts else 0
        
        input_c.selectbox(
            "Have a Personal Loan?", loan_opts,
            index = loan_idx,
            key="loan",
            on_change = sync_state,
            args = ("loan",),
            disabled = is_unsure_loan
        )    
        # check_c.markdown("###")  
      
    # Row 2 - housing and default
    r2_col1, r2_col2 = st.columns(2)

    with r2_col1:
        input_c, check_c = st.columns([3, 2])
        is_unsure_housing = check_c.checkbox(
            "Not sure",
            value = st.session_state.unsure_housing,
            key="temp_unsure_housing",
            on_change = sync_state,
            args = ("housing", True)
        )
        
        housing_opts = ["Select...", "yes", "no"]
        housing_idx = housing_opts.index(st.session_state.val_housing) if st.session_state.val_housing in housing_opts else 0
                
        input_c.selectbox(
            "Have a Housing Loan?", housing_opts, 
            index=housing_idx,
            key="housing",
            on_change = sync_state,
            args = ("housing",),
            disabled = is_unsure_housing
        )
        # check_c.markdown("###")  
    
    with r2_col2:
        input_c, check_c = st.columns([3,2])
        is_unsure_default = check_c.checkbox(
            "Not sure",
            value = st.session_state.unsure_default,
            key = "temp_unsure_default",
            on_change = sync_state,
            args = ("default", True)
        )
        
        default_opts = ["Select...", "yes", "no"]
        
        default_idx = default_opts.index(st.session_state.val_default) if st.session_state.val_default in default_opts else 0
        
        input_c.selectbox(
            "Any Credit in Default?", default_opts, 
            index = default_idx,
            key="default",
            on_change = sync_state,
            args = ("default",),
            help="Any past default history or unpaid loans? CRB check.",
            disabled = is_unsure_default
        )
        
        # check_c.markdown("###")  
   

# Communication info
elif st.session_state.step == 4:
    st.subheader("Most Recent Contact Details", anchor=False)
    st.markdown("Please complete all fields or select 'Not sure' to proceed.")  
    
    # Row 1 - contact    
    input_c, check_c = st.columns([3,2])
    
    is_unsure_contact = check_c.checkbox(
        "Not sure", 
        value=st.session_state.unsure_contact,
        key="temp_unsure_contact",
        on_change = sync_state,
        args=("contact", True)
    )
    
    contact_opts = ["Select...", "cellular", "telephone", "unknown"]
    
    contact_idx = contact_opts.index(st.session_state.val_contact) if st.session_state.val_contact in contact_opts else 0
    
    input_c.selectbox(
        "Contact Method", contact_opts, 
        index = contact_idx,
        key="contact",
        on_change = sync_state,
        args = ("contact",),
        help="type of communication contact",
        disabled = is_unsure_contact
    )
    
    # check_c.markdown("###")  

    # validate number of days
    # Map month abbreviations to their respective day counts
    days_map = {
        "Jan": 31, "Feb": 29, "Mar": 31, "Apr": 30, "May": 31, "Jun": 30,
        "Jul": 31, "Aug": 31, "Sep": 30, "Oct": 31, "Nov": 30, "Dec": 31
    }

    # Determine the limit based on the user's current session state selection
    # Defaults to 31 if "Select..." is picked or before initialization
    max_val = days_map.get(st.session_state.get("month"), 31)
   
    # Row 2 -  month and day
    r2_col1, r2_col2 = st.columns(2)
    with r2_col1:
        input_c, check_c = st.columns([3,2])
        
        is_unsure_month = check_c.checkbox(
            "Not sure", 
            value=st.session_state.unsure_month,
            key="temp_unsure_month",
            on_change = sync_state,
            args=("month", True)
        )        
        
        month_opts = ["Select...", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        month_idx = month_opts.index(st.session_state.val_month) if st.session_state.val_month in month_opts else 0
        
        input_c.selectbox(
            "Month", month_opts, 
            index = month_idx,
            key="month",
            on_change = sync_state,
            args = ("month",),
            help= "Last contact month of the year",
            disabled = is_unsure_month
        )        

        # check_c.markdown("###")  
        
    with r2_col2:
        input_c, check_c = st.columns([3,2])
        
        is_unsure_day = check_c.checkbox(
            "Not sure", 
            value = st.session_state.unsure_day,
            key = "temp_unsure_day",
            on_change = sync_state,
            args = ("day", True)            
        )
        
        input_c.number_input(
            "Day of Month", 1, max_val, 
            value=st.session_state.val_day, 
            placeholder="Enter...", 
            key="day", 
            on_change=sync_state, 
            args=("day",), 
            disabled=is_unsure_day,
            help=f"Last contact day of the month. Day 1-{max_val}", 
        )      
        
        # check_c.markdown("###")  
       
    # Row 3 - duration and campaign
    r3_col1, r3_col2 = st.columns(2)
    with r3_col1:
        input_c, check_c = st.columns([3,2])
        
        is_unsure_duration = check_c.checkbox(
            "Not sure", 
            value=st.session_state.unsure_duration,
            key="temp_unsure_duration",
            on_change = sync_state,
            args=("duration", True)
        )            
            
        input_c.number_input(
            "Call Duration (seconds)", 1, 5000, 
            value=st.session_state.val_duration, 
            placeholder="Enter...", 
            key="duration", 
            on_change=sync_state, 
            args=("duration",), 
            disabled=is_unsure_duration,
            help="Last contact duration in seconds"
        ) 
  
        # check_c.markdown("###")  
        
    with r3_col2:
        input_c, check_c = st.columns([3,2])
        
        is_unsure_campaign = check_c.checkbox(
            "Not sure", 
            value = st.session_state.unsure_campaign,
            key = "temp_unsure_campaign",
            on_change = sync_state,
            args = ("campaign", True)            
        )

        input_c.number_input(
            "Day of Month", 1, 80, 
            value=st.session_state.val_campaign, 
            placeholder="Enter...", 
            key="campaign", 
            on_change=sync_state, 
            args=("campaign",), 
            disabled=is_unsure_campaign,
            help="Number of contacts performed during this campaign" 
        )      
        
        # check_c.markdown("###")  
      

# Marketing/Outreach History
elif st.session_state.step == 5:
    st.subheader("Previous Campaign/Outreach History", anchor=False)
    st.markdown("Please complete all fields or select 'Not sure' to proceed.")   
    
    # Row 1 - poutcome    
    input_c, check_c = st.columns([3,2])
    
    is_unsure_poutcome = check_c.checkbox(
        "Not sure", 
        value=st.session_state.unsure_poutcome,
        key="temp_unsure_poutcome",
        on_change = sync_state,
        args=("poutcome", True)
    )
    
    poutcome_opts = ["Select...", "unknown", "failure", "other", "success"]
    
    poutcome_idx = poutcome_opts.index(st.session_state.val_poutcome) if st.session_state.val_poutcome in poutcome_opts else 0
    
    input_c.selectbox(
        "Previous Outcome", poutcome_opts, 
        index = poutcome_idx,
        key="poutcome",
        on_change = sync_state,
        args = ("poutcome",),
        help="Outcome of the previous marketing campaign",
        disabled = is_unsure_poutcome
    )
        
    # check_c.markdown("###")  

    # Row 2 -  pdays and previous
    r2_col1, r2_col2 = st.columns(2)
    with r2_col1:
        input_c, check_c = st.columns([3,2])
        
        is_unsure_pdays = check_c.checkbox(
            "Not sure", 
            value=st.session_state.unsure_pdays,
            key="temp_unsure_pdays",
            on_change = sync_state,
            args=("pdays", True)
        )        
        
        input_c.number_input(
            "Days since last contact (-1 if never)", -1, 900, 
            value=st.session_state.val_pdays, 
            placeholder="Enter...", 
            key="pdays", 
            on_change=sync_state, 
            args=("pdays",), 
            disabled=is_unsure_pdays,
            help="Number of days since the client was last contacted from a previous campaign (numeric; -1 means the client was not previously contacted)"
        )  

        # check_c.markdown("###")  
        
    with r2_col2:
        input_c, check_c = st.columns([3,2])
        
        is_unsure_previous = check_c.checkbox(
            "Not sure", 
            value = st.session_state.unsure_previous,
            key = "temp_unsure_previous",
            on_change = sync_state,
            args = ("previous", True)            
        )
                
        input_c.number_input(
            "Previous contacts", 0, 210, 
            value=st.session_state.val_previous, 
            placeholder="Enter...", 
            key="previous", 
            on_change=sync_state, 
            args=("previous",), 
            disabled=is_unsure_previous,
            help="Number of contacts performed before this campaign" 
        )      
        
        # check_c.markdown("###")  
    
    st.markdown("Press the '**Submit**' button to analyze this profile and generate Term Deposit Eligibility.")


# predict
elif st.session_state.step == 6:
    st.subheader("Client Profile Review and Prediction", anchor=False)
    
    
    final_input_data = {}

    for key in feature_keys:
        is_unsure = st.session_state.get(f"unsure_{key}", False)
        
        if is_unsure:
            # use the default value; ignore whatever is in st.session_state[f"val_{key}"]
            final_input_data[key] = FALLBACK_DEFAULTS.get(key)
        else:
            # Only use the user's input if they did not check unsure
            final_input_data[key] = st.session_state.get(f"val_{key}")

    # final data for model input  
    # convert to a vertical DataFrame for better readability
    input_df = pd.DataFrame(list(final_input_data.items()), columns=["Field", "Value"])
    
    model_input_df = pd.DataFrame(final_input_data, columns=feature_keys, index=[0])
    
    # Check if batch mode is active
    
    is_batch = st.checkbox(
        "Analyze multiple clients instead?", 
        value=st.session_state.val_unlock_batch, 
        key="temp_unlock_batch",                 
        on_change=sync_state,                    
        args=("unlock_batch",)                   
    )
    
    # expander - display single profile data
    if not is_batch:    
        # expander
        with st.expander("A summary of the single profile details"):
            st.write("Confirm details and make changes where necessary.")
            # display 
            st.dataframe(
                input_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Field": st.column_config.TextColumn("Attribute", help="Client metadata"),
                    "Value": st.column_config.TextColumn("Details"),
                }
            )
        
    # File Uploader - Batch prediction
    if is_batch:
        # Change this line:
        st.caption(f"***Only the first 1000 rows will be processed. Ensure the .csv dataset has these 16 features: {', '.join(feature_keys)}.***")      
        
        csv_path = os.path.join("sample_input_data", "sample_input_data.csv")
        
        
        # 2. Check if file exists and provide download button
        if os.path.exists(csv_path):
            with open(csv_path, "rb") as file:
                st.download_button(
                    label="Download Sample CSV",
                    data=file,
                    file_name="sample_input_data.csv",
                    mime="text/csv",
                    key="sample_download"
                )
        else:
            st.error(f"Sample file not found at {csv_path}")

        
        # Using a key in file_uploader helps maintain state
        uploaded_file = st.file_uploader("Choose CSV file", type="csv", key="batch_uploader")
        
        if uploaded_file:
            # overwrite the state only if a new file is actually uploaded
            st.session_state.persistent_batch_df = pd.read_csv(uploaded_file).head(1000)
            
            if st.session_state.persistent_batch_df.isnull().values.any():
                st.session_state.persistent_batch_df.fillna(FALLBACK_DEFAULTS, inplace=True)
                st.caption("Missing values detected and filled with default averages.")
                        
            # Reset the complete flag if a new file is uploaded
            if "last_uploaded_name" not in st.session_state or st.session_state.last_uploaded_name != uploaded_file.name:
                st.session_state.batch_run_complete = False
                st.session_state.last_uploaded_name = uploaded_file.name
                 
        if "persistent_batch_df" in st.session_state:
            df = st.session_state.persistent_batch_df
          
            if df is not None:
                # Validate Columns (checks if all feature_keys exist, regardless of order)
                missing_cols = [col for col in feature_keys if col not in df.columns]
                
                if not missing_cols:
                        # Now check if the data INSIDE those columns is valid
                    is_valid, error_msg = validate_batch_data(df)
                    
                    if is_valid:
                        st.write(f"Previewing {len(df)} rows of data for analysis and prediction rows:")
                        st.dataframe(df[feature_keys], use_container_width=True)
                        
                        # Predict Button for Batch
                        if st.button("Run Batch Prediction", type="primary"):
                            # Ensure columns are in the exact order the model expects before passing to logic
                            results = render_batch_prediction_logic(df[feature_keys])                      
                            
                            # dataframe for results 
                            results_df = df[feature_keys].copy()
                            results_df['Term Deposit Legibility'] = ["Legible" if r == 1 else "Not Legible" for r in results]
                            
                            # Save the results to session state
                            st.session_state.persistent_batch_results = results_df
                            st.session_state.batch_run_complete = True
                            st.rerun()
                            
                        if st.session_state.get("batch_run_complete"):
                            st.divider()
                            st.subheader(f"Batch Prediction Results - {len(st.session_state.persistent_batch_results)} rows", anchor=False)
                            st.markdown("The predictions are available in the last column.")
                            
                            st.caption("The Bank Asset Insights Model was validated with a 0.94654 ROC AUC score on unseen bank data. The system would pick the right client/lead 95 times out of 100. These top insights work reliably for all types of clients across the bank.")
                            st.dataframe(st.session_state.persistent_batch_results, use_container_width=True)
                            
                            # Option to clear results
                            if st.button("Clear Results"):
                                st.session_state.batch_run_complete = False
                                if "persistent_batch_results" in st.session_state:
                                    del st.session_state.persistent_batch_results
                                st.rerun()                    
                    
                    else:
                        st.error(error_msg)
                            
                else:
                    st.error(f"""
                        **Error:** The uploaded dataset is missing required features: 
                        `{', '.join(missing_cols)}`. 
                        Please ensure the CSV contains all 16 valid bank asset columns.
                    """)
            else:
                # This shows if the key exists but the file hasn't been uploaded yet
                st.info("Please upload a CSV file to begin batch analysis.")

    # single prediction
    if not is_batch:
        if st.button("Predict Profile", type="primary", disabled=not is_current_page_valid() or st.session_state.get('unlock_batch') == True): 
            # model logic   
            prediction = render_single_prediction_logic(model_input_df)
            # Assuming 'prediction' is 1 for 'yes' (will subscribe) and 0 for 'no'
            if prediction == 1:    
                st.success("Prediction: ****Legible and Likely to Subscribe****. There is a 95% chance that this client is a **high-potential candidate** for a term deposit.")
                
                st.caption("The Bank Asset Insights Model was validated with a 0.94654 ROC AUC score on unseen bank data. The system would pick the right client/lead 95 times out of 100. These top insights work reliably for all types of clients across the bank.")
                
        
            else:
                st.error("Prediction: **Not Legible and Unlikely to Subscribe**. There is a 95% chance that this client has a **lower probability** of opening a term deposit at this time.")
                
                st.caption("The Bank Asset Insights Model was validated with a 0.94654 ROC AUC score on unseen bank data. The system would pick the right client/lead 95 times out of 100. These top insights work reliably for all types of clients across the bank.")
    

    footer()
       
pagination()

