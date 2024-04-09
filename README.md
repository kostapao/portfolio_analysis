# portfolio_analysis

Files:
* risk_analysis.ipynb: Jupyter notebook containing functions to process the market data
* risk_analysis_app.py: Streamlit application


## Streamlit Application

To use the streamlit app dashboard navigate to the "portfolio_analysis" directory that contains the dockerfile and run the following in your terminal:

1. docker build -t portfolio_analysis . 
2. docker run -p 8501:8501 portfolio_analysis

App will be running on http://0.0.0.0:8501


Upload the market data file (not shared on github) "CaseStudy_Data.csv".

The sidebar contains filter options for the total portfolio under "Portfolio"

* Slider for LTV
* In case you would like to add a comparison portfolio check the box "Include Comparison Portfolio".
  
The comparison portfolio has two filter options, either directly check max(LTV Compare) <= 80 OR the slider where x can be between 0 and 100.

In case you would like to include the security amount in the analysis check the "Include Security Amount" checkbock. The portfolio AND the comparison portfolio will include the security amount.

Additions not mentioned in the task but seemed useful to me:

1. Ability to visualize individual projects under "Potential Loss Per Project"
2. Ability to Download the processed data

![image](https://github.com/kostapao/portfolio_analysis/assets/20754526/2d463d98-b9a6-4f4f-990f-ecf71910296a)


