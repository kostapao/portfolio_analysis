import streamlit as st
import pandas as pd
from io import StringIO
import numpy as np
from bokeh.plotting import figure
from bokeh.models import NumeralTickFormatter
from bokeh.models import HoverTool

### Functions ###

def potential_loss_project(mvalue_loss,mvalue,loan_nom,senior_loan, security = 0, incl_security_proj = False): #data, 
    """ 
    return potential loss depending on market value loss on project basis
    
    :param mvalue_loss float: market value loss, value from 0 to 1
    :param mvalue float: current market value of the property being financed
    :param loan_nom float: subordinated loan coming from company
    :param senior_loan float: loan that is preferred over subordinated loans in the event of the borrower’s insolvency
    :param bool security: security amount that is deposited as security and can be claimed by the lender in the event of a default
    :param bool incl_security_port: If set to True, security amount included in analysis
    """
    mvalue_loss_abs = mvalue * mvalue_loss
    equity = mvalue - loan_nom - senior_loan
    if equity >= mvalue_loss_abs:
        #equity covers all the losses
        return 0
    elif equity + loan_nom <= mvalue_loss_abs:
        if incl_security_proj:
            #we loose the loan but get te security amount so loss = loan - security amount
            return loan_nom - security
        else:
            #total loss of loan
            return loan_nom
        #total equity loss and more
    else:
        if incl_security_proj:
            #In case loss loan loss is smaller than security, loss is 0
            return max([0,(mvalue_loss_abs - equity) - security])
        else:
            return mvalue_loss_abs - equity
        

def potential_loss_portfolio(df_input, incl_security_port = False):
    """
    Calculate total portfolio loss for different market value loss scenarios
    
    :param DataFrame df: Raw data to perform risk analysis on
    :param bool incl_security_port: If set to True, security amount included in analysis

    """
    df_input = df_input.iloc[:,1:]
    df_input = df_input.reset_index(drop = True)
    df_input.columns = [col.lower() for col in df_input.columns]
    
    #Add potential loss columns
    add_cols = [str(round(mv_loss,2)) for mv_loss in np.arange(0, 1.05, 0.05)]
    for col_name in add_cols:
        df_input = df_input.assign(**{col_name: ''})
    no_projects = len(df_input)-1

    #For each project calculate potential loss for every .05 step
    for project in range(0,no_projects+1):
        mvalue = df_input.loc[project,'marketvalue']
        loan_nom = df_input.loc[project,'loannominal'] 
        senior_loan = df_input.loc[project,'seniorloan']
        security_amount = df_input.loc[project,'securityamount']
        if incl_security_port:
            for mv_loss in np.arange(0, 1.05, 0.05):
                df_input.loc[project,str(round(mv_loss,2))] = potential_loss_project(round(mv_loss,2),mvalue,loan_nom,senior_loan,security_amount,incl_security_proj = True)
        else:
            for mv_loss in np.arange(0, 1.05, 0.05):
                df_input.loc[project,str(round(mv_loss,2))] = potential_loss_project(round(mv_loss,2),mvalue,loan_nom,senior_loan)
    return df_input


def filter_ltv_x(df,x):
    """
    filter df on any x

    :param DataFrame df: Dataframe containing losses per finance project in long format
    :param int x: value to filter on ltv
    """
    df = df[df['ltv'] <= x]
    return df

def potential_total_loss_portfolio(df,ltv_x_value = 100):
    """
    sum up losses to get total loss per market_value loss for the total portfolio, option to filter
    
    :param DataFrame df: Dataframe containing losses per finance project in long format
    :param int ltv_x_value: Filter to apply in case ltv_x set to True

    """
    df = filter_ltv_x(df,ltv_x_value)
    df = df.loc[:, ~df.columns.isin(['projektnumber',	'ltv',	'marketvalue',	'loannominal',	'seniorloan',	'securityamount'])]
    df_total = pd.DataFrame(df.sum()).reset_index(drop=False)
    df_total = df_total.rename(columns={'index':'mv_loss',0:'potential_loss'})
    df_total['potential_loss'] =df_total['potential_loss'].astype(float).round(0)
    df_total['mv_loss'] =df_total['mv_loss'].astype(float)
    return df_total




### Bokeh Charts###

def bookeh_no_compare_line(df,y_max = 2500000000):
    hover = HoverTool(
    tooltips=[
        ("mv_loss", "@x"),
        ("potential_loss", "@y{0,0}"),
    ]
)
    p = figure(
    title='Potential Loss vs Market Value Loss',
    x_axis_label='Market Value Loss',
    y_axis_label='Potential Loss')
    #Thousand ticks
    p.yaxis.formatter = NumeralTickFormatter(format='0,0')
    p.add_tools(hover)
    p.line(df.mv_loss, df.potential_loss, legend_label='Pot Loss', line_width=2)
    p.y_range.start = 0
    p.y_range.end = y_max
    p.x_range.start = 0
    p.x_range.end = 1
    st.bokeh_chart(p, use_container_width=True)

def bookeh_compare_line(df1,df2,y_max = 2500000000):
    hover = HoverTool(
    tooltips=[
        ("mv_loss", "@x"),
        ("potential_loss", "@y{0,0}"),
    ]
)
    p = figure(
    title='Potential Loss vs Market Value Loss',
    x_axis_label='Market Value Loss',
    y_axis_label='Potential Loss')
    #Thousand ticks
    p.yaxis.formatter = NumeralTickFormatter(format='0,0')
    p.add_tools(hover)
    p.line(df1.mv_loss, df1.potential_loss, legend_label='Pot Loss', line_width=2)
    p.line(df2.mv_loss, df2.potential_loss, legend_label='Pot Loss Compare', line_width=5, line_color='red', line_dash='dotted')
    p.y_range.start = 0
    p.y_range.end = y_max
    p.x_range.start = 0
    p.x_range.end = 1
    st.bokeh_chart(p, use_container_width=True)

def bookeh_no_compare_line_project(df):
    hover_1 = HoverTool(
    tooltips=[
        ("mv_loss", "@x"),
        ("potential_loss", "@y{0,0}"),
    ]
)
    p = figure(
    title='Potential Loss vs Market Value Loss',
    x_axis_label='Market Value Loss',
    y_axis_label='Potential Loss')
    #Thousand ticks
    p.yaxis.formatter = NumeralTickFormatter(format='0,0')
    p.add_tools(hover_1)
    p.line(df.mv_loss, df.potential_loss, legend_label='Pot Loss', line_width=2,line_color='green' )
    p.y_range.start = 0
    p.x_range.start = 0
    p.x_range.end = 1
    st.bokeh_chart(p, use_container_width=True)



################################ Streamlit APP ################################

##Sidebar

#General Text
st.title("Portfolio Risk Analysis")
st.sidebar.header('Filters: Potential Loss Total')

#Portfolio
st.sidebar.subheader('Portfolio')

ltv_slider_val = st.sidebar.slider('LTV', 0, 100, 100)

comparison_include = st.sidebar.checkbox('Include Comparison Portfolio')

#Comparison Portfolio
if comparison_include:
    st.sidebar.subheader('Comparison Portfolio')

    ltv_80_check = st.sidebar.checkbox('max(LTV Compare) <= 80')
    if ltv_80_check:
        ltv_compare_slider_val = st.sidebar.slider('LTV Compare', 0, 80, 80)
    else:
        ltv_compare_slider_val = st.sidebar.slider('LTV Compare', 0, 100, 100)

#Security Amount
st.sidebar.subheader('Security Amount')
security_check = st.sidebar.checkbox('Include Security Amount')


#Upload File
uploaded_file = st.file_uploader("Upload CSV with market data")
if uploaded_file is not None:
    # Can be used wherever a "file-like" object is accepted:
    df = pd.read_csv(uploaded_file)
    #df = df.iloc[:,1:]

    #Calculate the dataframes we will work with

    #Portfolio
    df_loss = potential_loss_portfolio(df,incl_security_port = False)
    df_loss_security = potential_loss_portfolio(df,incl_security_port = True)

    #Comparison Portfolio
    df_loss_comp = df_loss.copy()
    df_loss_comp_security = df_loss_security.copy()

    st.write("#")

    st.subheader('Potential Loss Total Portfolio')
    st.write("#")
    st.write("#")


    ################ Graph 1: Potential Loss Total Portfolio ################

    #Show Graph
    if not security_check:

        if comparison_include:
            df_final = potential_total_loss_portfolio(df_loss, ltv_x_value = ltv_slider_val)
            df_final_comp = potential_total_loss_portfolio(df_loss_comp, ltv_x_value = ltv_compare_slider_val)
            bookeh_compare_line(df_final,df_final_comp)

        else:
            df_final = potential_total_loss_portfolio(df_loss, ltv_x_value = ltv_slider_val)
            bookeh_no_compare_line(df_final)

    else:
        
        if comparison_include:
            df_final = potential_total_loss_portfolio(df_loss_security, ltv_x_value = ltv_slider_val)
            df_final_comp = potential_total_loss_portfolio(df_loss_comp_security, ltv_x_value = ltv_compare_slider_val)
            bookeh_compare_line(df_final,df_final_comp,y_max = 1500000000)


        else:
            df_final = potential_total_loss_portfolio(df_loss_security, ltv_x_value = ltv_slider_val)
            bookeh_no_compare_line(df_final,y_max = 1500000000)


    st.write("#")

    ################ Graph 2:  Potential Loss Per Project ################


    st.subheader('Potential Loss Per Project')
    st.write("#")

    df_loss_project = df_loss.copy()
    df_loss_project_security = df_loss_comp_security.copy()


    # Selection Box For Projects
    projects = df_loss.projektnumber.values

    project_selected = st.selectbox(
    'Choose Project For Analysis, **Sidebar filters do not apply**',
    projects)


    # Checkbok for security amount
    security_check_project = st.checkbox('Include Security Amount for Project')

    #Show Graph

    if not security_check_project:
        df_project = df_loss_project[df_loss_project['projektnumber'] == project_selected]
        st.write(df_project[['ltv','marketvalue','loannominal','seniorloan','securityamount']])
        df_project_final = potential_total_loss_portfolio(df_project)

        bookeh_no_compare_line_project(df_project_final)

    else:
        df_project = df_loss_project_security[df_loss_project_security['projektnumber'] == project_selected]
        st.write(df_project[['ltv','marketvalue','loannominal','seniorloan','securityamount']])
        df_project_final = potential_total_loss_portfolio(df_project)

        bookeh_no_compare_line_project(df_project_final)

    st.write("#")
    


    ################ Option to Download Data ################


    st.subheader('Download Data')
    st.write("#")


    def convert_df(df):
        return df.to_csv(index=True).encode('utf-8')


    csv_ex_sec_per_fin = convert_df(df_loss)

    st.download_button(
        "Download Potential Loss Data (excl. Security) per Financing",
        csv_ex_sec_per_fin,
        "file.csv",
        "text/csv",
        key='download-ex_sec_per_fin'
    )

    csv_inc_sec_per_fin = convert_df(df_loss_security)

    st.download_button(
        "Download Potential Loss Data (incl. Security) per Financing",
        csv_inc_sec_per_fin,
        "file.csv",
        "text/csv",
        key='download-inc_sec_per_fin'
    )

    df_no_ltv_total = potential_total_loss_portfolio(df_loss)
    csv_ex_sec_total = convert_df(df_no_ltv_total)

    st.download_button(
        "Download Potential Loss Data (excl. Security) Total",
        csv_ex_sec_total,
        "file.csv",
        "text/csv",
        key='download-ex_sec_total'
    )

    df_no_ltv_total = potential_total_loss_portfolio(df_loss_security)
    csv_inc_sec_total = convert_df(df)

    st.download_button(
        "Download Potential Loss Data (incl. Security) Total",
        csv_inc_sec_total,
        "file.csv",
        "text/csv",
        key='download-inc_sec_total'
    )