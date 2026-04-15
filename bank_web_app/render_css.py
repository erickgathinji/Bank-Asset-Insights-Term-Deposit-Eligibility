import streamlit as st 
import datetime

# footer url - linkedin and portfolio
profile_url = "https://ericgathinji.pythonanywhere.com/"
linkedin_url = "https://www.linkedin.com/in/erick-gathinji/"
title = 'Finance and Data Professional'


def apply_css():
    st.markdown("""
    <style>
    
    /* import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&family=Source+Sans+3:ital,wght@0,200..900;1,200..900&display=swap');
    
    /* Remove default Streamlit header */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Main background */
    .stApp {
        background: #000D21;
        color: #dfdede !important;
        scroll-behavior: auto !important;
    }
     
    /*set font*/ 
    p, h1, h2, h3, h4, input label {
       font-family: 'Montserrat', sans-serif !important;
       color:  #dfdede !important;
    }
    
            
    /* Buttons */
    /* Target the Submit Button inside the form */
    div.stButton > button, div.stButton > button:active, 
    div.stButton > button:focus {
        background: linear-gradient(135deg, #4834d4, #0097a7) !important;
        color: #0f172a !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        border: none !important;    
        transition: none !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /*btn hover*/   
    div.stButton > button:hover{
        background: linear-gradient(135deg, rgba(72, 52, 212, 0.8), rgba(0, 151, 167, 0.8))  !important;
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    div.stButton > button p {
        font-weight: 600 !important;
    }
    
    .stDownloadButton button{
        background: rgba(45, 56, 76, 0.3) !important;
        padding: 2px 15px;
    }

    .stDownloadButton button:hover{
        background: rgba(45, 56, 76, 0.6) !important;
    }
    
    .stFileUploader button{
        background: linear-gradient(135deg, #4834d4, #0097a7); !important;
    }
    .stFileUploader button:hover {
            background: linear-gradient(135deg, rgba(72, 52, 212, 0.9), rgba(0, 151, 167, 0.9)); !important;
        }

    /* error and success messages */
    /*hide original bg*/
    [data-testid="stAlertContainer"] {
        background-color: transparent !important;
        border: none !important;
    }
    
    [data-testid="stAlertContentError"] {
        background-color: #fef2f2 !important; 
        border: 1px solid #ef4444 !important; 
        border-left: 5px solid #ef4444 !important;
        border-radius: 8px !important;
        padding: 15px !important;
    }
    
    [data-testid="stAlertContentError"] p {
        color: #991b1b !important; 
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* success alerts */
    [data-testid="stAlertContentSuccess"] {
        background-color: #f0fdf4 !important; 
        border: 1px solid #22c55e !important; 
        border-left: 5px solid #22c55e !important;
        border-radius: 8px !important;
        padding: 15px !important;
    }

    [data-testid="stAlertContentSuccess"] p {
        color: #166534 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
    }
    

    /* Footer */
    .custom-footer {
        margin-top: 20px;
        margin-bottom: -350px !important;
        padding: 20px 20px;
        text-align: center;
        color: #94a3b8;
        font-size: 14px;
        font-family: 'Montserrat', sans-serif !important;
    }

    .footer-name {
        color: #38bdf8;
        font-weight: 600;        
    }
    
    .footer-name:hover {
           opacity: 0.9;
    }
    
    /*advanced form*/
    .st-emotion-cache-1w723zb{
        padding: 30px !important;
    }
    
    /*hide default input instructions/placeholders*/
    [data-testid="InputInstructions"] {
        display: none !important;
        opacity: 0.0 !important;
    }
    
    div[data-testid="InputInstructions"] > span:nth-child(1) {
        display: none !important;
        opacity: 0.0 !important;
        transition: None !important;
        transform: None !important;
        box-shadow : None !important;
    }
    
    
    /* Fix label visibility */
    .stSelectbox label,
    .stNumberInput label,
    .stTextInput label,
    .stSlider label {
        color: #dfdede !important;
        font-weight: 500 !important;
        font-size: 15px;
        letter-spacing: 0.3px;
        margin-top: 5px !important;
    }

   
    
    

          
    [data-testid="stExpander"] {
        border-radius: 10px;
        margin-top: 15px !important;
        margin-bottom: 5px !important;
    }

    /* Target the clickable header */
    [data-testid="stExpander"] details summary {
        background-color: rgba(45, 56, 76, 0.2) !important;
        color: #01e1ff;
        font-weight: bold;
    }    
    
    /* Style the expander header (the part always visible) */
    .streamlit-expanderHeader {
        background-color: #f0f2f6;
        color: #31333f;
        font-weight: bold;
        border-radius: 5px;
    }
    
    [data-testid="stExpander"] details summary:hover{
        background: rgba(161, 184, 199, 0.1) !important;
    }
    
    /* Style the content inside the expander */
    .streamlit-expanderContent {
        background-color: white;
        border: 1px solid #f0f2f6;
        border-top: none;
    }
    
    div[data-baseweb="select"]:focus-within > div {
        border: 1px solid #5EC5F5 !important;       
    }
    
   
    div[data-testid="stSelectbox"], 
    div[data-testid="stSelectbox"] * {
        cursor: pointer !important;
    }
            
    svg {
        stroke : #dfdede !important;
    }   
    
    
    [data-testid="stHorizontalBlock"] {
        align-items: flex-end !important;
    } 
    
        
    /*help text */
    @media (max-width: 372px) {
    div[data-baseweb="tooltip"], 
    .stTooltip {
            max-width: 300px !important;
            margin-left: 15px !important;
            margin-right: 15px !important; 
                       
        }
    }   
    
    .hero-img {
        width: auto;
        height: auto;
        scale: 0.99;
        border-radius: 3px;
        object-fit: cover !important;
        display: block;

        margin-top: 0px;
        margin-bottom: 25px;
        
    }    
    
    .instruction-card {
        background-color: rgba(30, 41, 59, 0.2);                        padding: 20px;
        margin-left: auto;
        margin-right: auto;                 
        margin-bottom: 25px;
        width: 98%;
        font-family: 'Montserrat', sans-serif !important;
    }
    
    .step-number {
        background: linear-gradient(135deg, #4834d4, #0097a7);
        color: inherit;
        border-radius: 50%;
        width: 25px;
        height: 25px;
        min-width: 25px;
        min-height: 25px;
        flex-shrink: 0;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        font-weight: bold;
        margin-right: 12px;
        scale: 0.9;
    }
    
    .step-container {
        font-size: 0.9rem; 
        display: flex; 
        align-items: center; 
        margin-bottom: 10px;
    }
    
    .step-text { 
        font-family: 'Montserrat', sans-serif;
        color: #cbd5e1; 
    }
    
    .instruction-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f1f5f9;
        display: flex;
        align-items: center;
        justify-content: center;
        letter-spacing: 1px;
    }
    
    .prediction-text {
        font-family: 'Montserrat', sans-serif;
        font-size: 14px;
        color: #A1B8C7;
        padding: 10px;
        /* border-left: 5px solid #0097a7;*/
        /*background-color: rgba(161, 184, 199, 0.1);*/      
        border-radius: 5px;
        margin-bottom: 20px;
    }
    
    
    [data-testid="stNumberInputContainer"]:focus-within    {
        border: 1px solid #5EC5F5 !important; 
        
    }
    
    /* number input btns*/
    [data-testid="stNumberInputContainer"] button:hover {
        background: #5EC5F5 !important;
    }

    [data-testid="stNumberInputContainer"] button:active,
    [data-testid="stNumberInputContainer"] button:focus {
        background: #5EC5F5 !important;
        outline: none !important;
        box-shadow: none !important;
    }
       
    div[data-testid="stTooltipContent"] p {
    color: #0566f7  !important;
    }
     
    div[data-testid="stCheckbox"]:has(input[aria-label="Not sure"]:checked) span,  div[data-testid="stCheckbox"]:has(input[aria-label="Analyze multiple clients instead?"]:checked) span {
    background-color: green !important;
    border-color: green !important;}
    
    
    /* prevent page transitions */
    [data-testid="stVerticalBlock"] > div {
        animation: none !important;
    }
    
    .main .block-container {
        transition: none !important;
    }
    /* prevent page transitions */
    
    .st-emotion-cache-1gjnins button {
        background: #05769c !important;
        color: white;
    }
    .st-emotion-cache-1gjnins button:hover {
        background: #c2cdd8 !important;
        border: 0.5px solid #05769c !important;
        
    }
            
    </style>
    """, unsafe_allow_html=True)


def footer():
    st.markdown(f"""   
    <div class="custom-footer">
        <div style="margin-top: 30px; padding-top: 30px; ">
            <hr>
            © {datetime.datetime.now().year} by 
            <a href="{profile_url}" target="_blank" style="text-decoration:none;">
                <span class="footer-name">Erick Gathinji</span>
            </a><br>
            {title}<br>
            <a href="{linkedin_url}" target="_blank" style="text-decoration:none;">
                <span class="footer-name">Let's connect on LinkedIn!</span>
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

