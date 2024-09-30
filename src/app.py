from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import re
import pathlib
import dash_auth

external_style = ['https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css']

app = Dash(__name__, suppress_callback_exceptions=True,external_stylesheets=[dbc.themes.COSMO,external_style])
app.title = 'Center for Impact Case Study'
server = app.server

# auth = dash_auth.BasicAuth(
#     app,
#     {'nimagna': 'uclacfi',
#      'nimagna2':'uclacfi2'}
# )

pd.options.mode.chained_assignment = None

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

df=pd.read_excel(DATA_PATH.joinpath('2024.02.28_Updated Transp. Index 2023 FC.xlsx'),sheet_name='Full Dataset_Board', nrows=500)
dfnz2 = pd.read_excel(DATA_PATH.joinpath('2024.04.04-NZ for Descriptive Testing_not full QC w sectors.xlsx'),sheet_name='Dissertation Net Zero & Governa', nrows=496)

#dfpivot = pd.read_csv(DATA_PATH.joinpath('Pivoted_master_data.csv'))

def company_list(sector):
    dfcs = df.loc[df['GICS.Sector'] == sector,['Company.Name','Revenue']]
    dfcs.rename(columns={"Company.Name": "Company"},inplace=True)
    #,"CM7a.GHG.Emissions.": "GHG Scope 1 Emission", "CM7b.GHG.Emissions.": "GHG Scope 2 Emission","CM7c.GHG.Emissions.": "GHG Scope 3 Emission", "TCFD New": "TCFD", "CM9.Land.use.and.eco": "Biodiversity", "Water amount Index": "Water Disclosure","water stress index": "Water Stress Disclosure","Revenue": "Revenue"},inplace=True)
    
    dfcs = dfcs.sort_values(by=['Revenue'], ascending=False)
    
    companies = dfcs['Company'].tolist()
    top_companies = dfcs.head(10)['Company'].tolist()
    
    return sorted(companies), sorted(top_companies)

def company_list_from_sector(sector):
    company_list = []
    dfk = df[df['GICS.Sector'].isin([sector])]
    company_list = dfk['Company.Name'].tolist()
    return company_list



def trafficlight(sector,company_list):
    dfcs = df.loc[df['GICS.Sector'] == sector,['Company.Name','CM7a.GHG.Emissions.','CM7b.GHG.Emissions.','CM7c.GHG.Emissions.','CM9.Land.use.and.eco','Water amount Index','water stress index']]
    
    dfcs.rename(columns={"Company.Name": "Company","CM7a.GHG.Emissions.": "GHG Scope 1 Emission", "CM7b.GHG.Emissions.": "GHG Scope 2 Emission",
                     "CM7c.GHG.Emissions.": "GHG Scope 3 Emission", "TCFD New": "TCFD",
                     "CM9.Land.use.and.eco": "Biodiversity", "Water amount Index": "Water Disclosure",
                     "water stress index": "Water Stress Disclosure",
                     "Revenue": "Revenue"},inplace=True)
    
    mask = dfcs['Company'].isin(company_list)
    
    dfcs_melted = dfcs[mask].melt(id_vars=['Company'], var_name='Metric', value_name='Status')
    

    dfcs_melted['Status'].astype('string')
    categorical_mapping = {1.0: 'Full Disclosure', 0.5: 'Partial Disclosure', 0.0: 'No Disclosure'}
    dfcs_melted['Status'] = dfcs_melted['Status'].map(categorical_mapping)
    
    color_mapping = {'Full Disclosure': '#4E7E6B',
                     'Partial Disclosure': '#FFD100',
                     'No Disclosure': '#F43A00'}
    
#     fig = px.scatter(dfcs_melted, y="Company", x="Metric", color="Status",
#                      color_discrete_map=color_mapping,
#                      #width = 2000, 
#                      height = 1000, 
#                      #title='Disclosure Status for Consumer Staples Environmental Metrics'
#                     )
#     fig.update_traces(marker_size=25)
#     fig.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica",
#                       title_x=0.5,xaxis=dict(side="top"),
#                       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None))
#     fig.update_yaxes(categoryorder='category descending', title=None)
#     wrapped_labels = [label[:[m.start() for m in re.finditer(r' ', label)][0]] + '<br>' + label[[m.start() for m in re.finditer(r' ', label)][0]:] if label.find(' ')>=2 else label for label in dfcs_melted['Metric'].unique().tolist()]
#     fig.update_xaxes(tickmode='array', tickvals=list(range(len(dfcs_melted['Metric'].unique().tolist()))), ticktext=wrapped_labels)
    
#     fig.update_xaxes(title=None)
#     fig.add_shape(
#         type="line",
#         x0=0,
#         y0=1,
#         x1=1,
#         y1=1,
#         line=dict(
#             color="black",
#             width=1,
#         ),
#         xref="paper",
#         yref="paper"
#    )
    xaxis_order = ['GHG Scope 1 Emission','GHG Scope 2 Emission','GHG Scope 3 Emission','Water Disclosure','Water Stress Disclosure','Biodiversity']
    
    dfcs_melted['Company '] = dfcs_melted['Company'].apply(lambda x: x[:x.find(' ', x.find(' ') + 1)] + '<br>' + x[x.find(' ', x.find(' ') + 1) + 1:] if x.count(' ') >= 2 else x)

    fig = px.scatter(dfcs_melted, y="Company ", x="Metric", color="Status",
                 color_discrete_map=color_mapping,
                 height = 1000, title='Environmental Metrics Disclosure')
    fig.update_traces(marker_size=34)
    fig.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica", title_x=0.5,
                 legend=dict( yanchor="bottom",orientation="h",  xanchor="right", x=1, title=None), font=dict(size=15),
                 margin=dict(t=190),title_font_size=30,xaxis_tickformat='wrap',
                 xaxis=dict(side="top",categoryorder='array', categoryarray= xaxis_order))
    fig.update_yaxes(categoryorder='category descending', title=None)
    fig.update_xaxes(title=None, tickformat='wrap')

    max_label_length = 7
    wrapped_labels = [label[:label.find(' ')] + '<br>' + label[label.find(' '):] if label.find(' ')>0 else label for label in xaxis_order]
    fig.update_xaxes(tickmode='array', tickvals=list(range(len(xaxis_order))), ticktext=wrapped_labels)

    fig.add_shape(
        type="line",
        x0=0,
        y0=1,
        x1=1,
        y1=1,
        line=dict(
            color="black",
            width=1,
        ),
        xref="paper",
        yref="paper"
    )
    
    return fig


def tghg1(sector,company_list):
    tghg1 = dfnz2.loc[:,['Enter the full company name', 'What is the company\'s current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)']]
    tghg1.rename(columns={"Enter the full company name": "Company",
                     "What is the company's current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)": "Total GHG1"},inplace=True)
    
    masknz1 = tghg1['Company'].isin(company_list)
    tghg1_sel10 = tghg1[masknz1].sort_values(by='Total GHG1', axis=0, ascending=False)
    tghg1_sel10['Total GHG1'] = tghg1_sel10['Total GHG1']/1000
    
    fontsize = 150/tghg1_sel10.shape[0]
    if (fontsize > 15):
        fontsize = 15
    
    fig22 = px.bar(tghg1_sel10, x='Company', y='Total GHG1', text='Total GHG1', color_discrete_sequence=['#2774AE'], height=780)
    fig22.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica", font=dict(size=fontsize))
    fig22.update_xaxes(title=None)
    fig22.update_yaxes(title=None)
    fig22.update_layout(
    title=go.layout.Title(
        text="Total GHG Scope 1 Emissions<br><sup>(in thousand metric tons)</sup>",
        #xref="paper",
        x=0.5,
        font_size=30
    ))
    fig22.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in tghg1_sel10['Company'].unique().tolist()]
    fig22.update_xaxes(tickmode='array', tickvals=list(range(len(tghg1_sel10['Company'].unique().tolist()))), ticktext=wrapped_labels)
    
    return fig22


def nghg1(sector,company_list):
    tghg1 = dfnz2.loc[:,['Enter the full company name', 'What is the company\'s current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)']]
    tghg1.rename(columns={"Enter the full company name": "Company",
                     "What is the company's current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)": "Total GHG1"},inplace=True)
    
    masknz1 = tghg1['Company'].isin(company_list)
    tghg1_sel10 = tghg1[masknz1].sort_values(by='Total GHG1', axis=0, ascending=False)
    tghg1_sel10['Total GHG1'] = tghg1_sel10['Total GHG1']/1000
    tnghg1 = df.loc[:,['Company.Name','Revenue']]
    tnghg1 = tnghg1.rename(columns={"Company.Name":"Company"})
    masknz11 = tnghg1['Company'].isin(company_list)
    tnghg1 = tnghg1[masknz11]
    
    tnghg1_merged = tnghg1.merge(tghg1_sel10,on='Company')
    tnghg1_merged['Normalised GHG1'] = tnghg1_merged['Total GHG1']*1000/tnghg1_merged['Revenue']
    tnghg1_merged['Normalised GHG1 Rounded'] = pd.to_numeric(tnghg1_merged['Normalised GHG1']).round(2)
    tnghg1_merged = tnghg1_merged.sort_values(by='Normalised GHG1', ascending=False)

    fontsize = 150/tnghg1_merged.shape[0]
    if (fontsize > 15):
        fontsize = 15
    
    fig2 = px.bar(tnghg1_merged, x='Company', y='Normalised GHG1',text='Normalised GHG1 Rounded',color_discrete_sequence=['#2774AE'],height = 780)
    fig2.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica",font=dict(size=fontsize))
    fig2.update_xaxes(title=None)
    fig2.update_yaxes(title=None)
    fig2.update_layout(
    title=go.layout.Title(
        text="Normalised GHG Scope 1 Emissions<br><sup>(in metric tons per $M revenue)</sup>",
        #xref="paper",
        x=0.5,
        font_size=30
    ))
    fig2.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in tnghg1_merged['Company'].unique().tolist()]
    fig2.update_xaxes(tickmode='array', tickvals=list(range(len(tnghg1_merged['Company'].unique().tolist()))), ticktext=wrapped_labels)

    
    return fig2

def tghg2(sector,company_list):
    tghg2 = dfnz2.loc[:,['Enter the full company name', 'Enter the company\'s Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)',
                     'Enter the company\'s Scope 2 location based emissions in metric tons CO2e. (Enter NA if the company does not report a location-based figure.)',
                     'Enter the company\'s uncategorized Scope 2 emissions in metric tons CO2e. (Enter NA if the company does not report an uncategorized figure.)' ]]
    tghg2.rename(columns={"Enter the full company name": "Company",
                     "Enter the company\'s Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)": "Total market-based GHG2",
                     "Enter the company\'s Scope 2 location based emissions in metric tons CO2e. (Enter NA if the company does not report a location-based figure.)":"Total location-based GHG 2",
                     "Enter the company\'s uncategorized Scope 2 emissions in metric tons CO2e. (Enter NA if the company does not report an uncategorized figure.)":"Total uncategorised GHG 2"},inplace=True)

    
    masknz2 = tghg2['Company'].isin(company_list)
    tghg2 = tghg2[masknz2]
    tghg2_melted = pd.melt(tghg2, id_vars='Company')
    #tghg2_melted[['Scope 2 type']] = re.search(r'Total(.*?)GHG', tghg2_melted['variable'])
    tghg2_melted['Scope 2 Category'] = tghg2_melted['variable'].apply(lambda x: re.search(r'Total(.*?)GHG', x).group(1).strip() if re.search(r'Total(.*?)GHG', x) else None)
    tghg2_melted['value'] = pd.to_numeric(tghg2_melted['value']/1000, errors='coerce')
    tghg2_melted['value_rounded'] = (tghg2_melted['value']).round(2).astype(str).str.replace('nan', 'NR')

    tghg2_melted = tghg2_melted.sort_values(by='value', axis=0, ascending=False)
    
    color_mapping = {'uncategorised': '#F47C30',
                     'market-based': '#2774AE',
                     'location-based': '#FFB81C'}
    
    fontsize = 450/tghg2_melted.shape[0]
    if (fontsize > 15):
        fontsize = 15
    
    fig32 = px.bar(tghg2_melted, x="Company", y="value", color="Scope 2 Category", barmode="group", text='value_rounded', color_discrete_map=color_mapping, height = 780)
    
    fig32.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica",
                  font=dict(size=fontsize), uniformtext_mode='hide',
                  legend=dict(
                      yanchor="top",
                      y=0.99,
                      xanchor="left",
                      x=0.85                      
                  ),
                  xaxis=dict(categoryorder='array', categoryarray= tghg2_melted["Company"].unique()))

    fig32.update_xaxes(title=None)
    fig32.update_yaxes(title=None)
    fig32.update_layout(
    title=go.layout.Title(
        text="Total GHG Scope 2 Emissions<br><sup>(in thousand metric tons)</sup>",
        #xref="paper",
        x=0.5,
        font_size = 30
    ))
    fig32.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in tghg2_melted['Company'].unique().tolist()]

    fig32.update_xaxes(tickmode='array', tickvals=list(range(len(tghg2_melted['Company'].unique().tolist()))), ticktext=wrapped_labels)
    
    return fig32


def nghg2(sector,company_list):
    tghg2 = dfnz2.loc[:,['Enter the full company name', 'Enter the company\'s Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)',
                     'Enter the company\'s Scope 2 location based emissions in metric tons CO2e. (Enter NA if the company does not report a location-based figure.)',
                     'Enter the company\'s uncategorized Scope 2 emissions in metric tons CO2e. (Enter NA if the company does not report an uncategorized figure.)' ]]
    tghg2.rename(columns={"Enter the full company name": "Company",
                     "Enter the company\'s Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)": "Total market-based GHG2",
                     "Enter the company\'s Scope 2 location based emissions in metric tons CO2e. (Enter NA if the company does not report a location-based figure.)":"Total location-based GHG 2",
                     "Enter the company\'s uncategorized Scope 2 emissions in metric tons CO2e. (Enter NA if the company does not report an uncategorized figure.)":"Total uncategorised GHG 2"},inplace=True)

    
    masknz2 = tghg2['Company'].isin(company_list)
    tghg2 = tghg2[masknz2]
    
    tnghg2 = df.loc[:,['Company.Name','Revenue']]
    tnghg2 = tnghg2.rename(columns={"Company.Name":"Company"})
    masknz22 = tnghg2['Company'].isin(company_list)
    tnghg2 = tnghg2[masknz22]
    
    tnghg2_merged = tnghg2.merge(tghg2,on='Company')
    tnghg2_merged['Normalised market-based GHG2'] = tnghg2_merged['Total market-based GHG2']/tnghg2_merged['Revenue']
    tnghg2_merged['Normalised location-based GHG2'] = tnghg2_merged['Total location-based GHG 2']/tnghg2_merged['Revenue']
    tnghg2_merged['Normalised uncategorised GHG2'] = tnghg2_merged['Total uncategorised GHG 2']/tnghg2_merged['Revenue']
    tnghg2_merged.drop(labels=['Revenue','Total market-based GHG2','Total location-based GHG 2','Total uncategorised GHG 2'], axis=1, inplace=True)
    
    tnghg2_melted = pd.melt(tnghg2_merged, id_vars='Company')
#tghg2_melted[['Scope 2 type']] = re.search(r'Total(.*?)GHG', tghg2_melted['variable'])
    tnghg2_melted['Scope 2 Category'] = tnghg2_melted['variable'].apply(lambda x: re.search(r'Normalised(.*?)GHG', x).group(1).strip() if re.search(r'Normalised(.*?)GHG', x) else None)
    tnghg2_melted['value'] = pd.to_numeric(tnghg2_melted['value'], errors='coerce')
    tnghg2_melted['value_rounded'] = (tnghg2_melted['value']).round(2).astype(str).str.replace('nan', 'NR')

    tnghg2_melted = tnghg2_melted.sort_values(by='value', axis=0, ascending=False)

    color_mapping = {'uncategorised': '#F47C30',
                     'market-based': '#2774AE',
                     'location-based': '#FFB81C'}
    
    fontsize = 450/tnghg2_melted.shape[0]
    if (fontsize > 15):
        fontsize = 15
    
    fig322 = px.bar(tnghg2_melted, x="Company", y="value",
                    color="Scope 2 Category", barmode="group",text='value_rounded',color_discrete_map=color_mapping,height = 780)
    fig322.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica",
                  font=dict(size=fontsize), uniformtext_mode='hide',
                  legend=dict(
                      yanchor="top",
                      y=0.99,
                      xanchor="left",
                      x=0.85                      
                  ),
                  xaxis=dict(categoryorder='array', categoryarray= tnghg2_melted["Company"].unique()))

    fig322.update_xaxes(title=None)
    fig322.update_yaxes(title=None)
    fig322.update_layout(
    title=go.layout.Title(
        text="Normalised GHG Scope 2 Emissions<br><sup>(in metric tons per $M revenue)</sup>",
        #xref="paper",
        x=0.5,
        font_size = 30
    ))
    fig322.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in tnghg2_melted['Company'].unique().tolist()]
# a = wrapped_labels[6]
# wrapped_labels[6] = wrapped_labels[7]

    fig322.update_xaxes(tickmode='array', tickvals=list(range(len(tnghg2_melted['Company'].unique().tolist()))), ticktext=wrapped_labels)
    return fig322

def category_label(row):
    column_numbers = row['Company']
    
    for i in range(7- column_numbers.count(' ') - column_numbers.count('-')):
        column_numbers = column_numbers + '<br>'
    
    column_numbers = column_numbers + '<b><i>Categories Included: </i></b>'
    
    column_numbers_all = column_numbers
    
    # Iterate over the columns from Category 1 to Category 15
    sp = 0
    tv = 0
    for i in range(1, 16):
        column_name = f'Category {i}'
        if row[column_name] == 'Yes':
            column_numbers = column_numbers + str(i) + ","
            sp = sp + len(str(i)) + 2
            tv = tv + 1
        if (sp >= 8):
            column_numbers = column_numbers + "<br>"
            sp = 0
            
    if (tv == 0):
        column_numbers = column_numbers + 'Categories not identified'
    elif (tv == 15):
        column_numbers = column_numbers_all + 'All'
    else:
        column_numbers = column_numbers[:column_numbers.rfind(',')]
    # Return the list of column numbers as a string
    return column_numbers



def tnghg3(sector,company_list,k1,pp):
    k2 = k1 + " Rounded"
    if (pp==1):
        k3 = k1[:-1] + " Scope 3 Emissions<br><sup>(in metric tons per $M revenue)</sup>"
    else:
        k3 = k1[:-1] + " Scope 3 Emissions<br><sup>(in thousand metric tons)</sup>"
    tghg3 = dfnz2.loc[:,['Enter the full company name', 'Enter the company\'s Scope 3 emissions in metric tons of CO2e.',
                  'Does the company report Category 1 (purchased goods and services) emissions?',
                  'Does the company report Category 2 (capital goods) emissions?',
                  'Does the company report Category 3 (fuel and energy related activities) emissions?',
                  'Does the company report Category 4 (upstream transportation and distribution) emissions?',
                  'Does the company report Category 5 (waste generated in operations) emissions?',
                  'Does the company report Category 6 (business travel) emissions?',
                  'Does the company report Category 7 (employee commuting) emissions?',
                  'Does the company report Category 8 (upstream leased assets) emissions?',
                  'Does the company report Category 9 (downstream transportation and distribution) emissions?',
                  'Does the company report Category 10 (processing of sold products) emissions?',
                  'Does the company report Category 11 (use of sold products) emissions?',
                  'Does the company report Category 12 (end-of-life treatment of sold products) emissions?',
                  'Does the company report Category 13 (downstream leased assets) emissions?',
                  'Does the company report Category 14 (franchises) emissions?',
                  'Does the company report Category 15 (investments) emissions?']]
    tghg3.rename(columns={'Enter the full company name': 'Company',
                     'Enter the company\'s Scope 3 emissions in metric tons of CO2e.':'Total GHG3',
                  'Does the company report Category 1 (purchased goods and services) emissions?':'Category 1',
                  'Does the company report Category 2 (capital goods) emissions?':'Category 2',
                  'Does the company report Category 3 (fuel and energy related activities) emissions?':'Category 3',
                  'Does the company report Category 4 (upstream transportation and distribution) emissions?':'Category 4',
                  'Does the company report Category 5 (waste generated in operations) emissions?':'Category 5',
                  'Does the company report Category 6 (business travel) emissions?':'Category 6',
                  'Does the company report Category 7 (employee commuting) emissions?':'Category 7',
                  'Does the company report Category 8 (upstream leased assets) emissions?':'Category 8',
                  'Does the company report Category 9 (downstream transportation and distribution) emissions?':'Category 9',
                  'Does the company report Category 10 (processing of sold products) emissions?':'Category 10',
                  'Does the company report Category 11 (use of sold products) emissions?':'Category 11',
                  'Does the company report Category 12 (end-of-life treatment of sold products) emissions?':'Category 12',
                  'Does the company report Category 13 (downstream leased assets) emissions?':'Category 13',
                  'Does the company report Category 14 (franchises) emissions?':'Category 14',
                  'Does the company report Category 15 (investments) emissions?':'Category 15'},inplace=True)

    
    masknz3 = tghg3['Company'].isin(company_list)
    tghg3_sel10 = tghg3[masknz3].sort_values(by='Total GHG3', axis=0, ascending=False)
    tghg3_sel10['Total GHG3'] = tghg3_sel10['Total GHG3']/1000
    tghg3_sel10['Total GHG3 Rounded'] = tghg3_sel10['Total GHG3'].round(2)


    masknan = (tghg3_sel10['Company'] == 'The Hershey Company') | (tghg3_sel10['Company'] == 'PepsiCo, Inc.')
    tghg3_sel10.loc[masknan]=tghg3_sel10.loc[masknan].fillna('Yes')
    #tghg3_sel10 = tghg3_sel10.fillna(0)

    tnghg3 = df.loc[:,['Company.Name','Revenue']]
    tnghg3 = tnghg3.rename(columns={"Company.Name":"Company"})
    masknz33 = tnghg3['Company'].isin(company_list)
    tnghg3 = tnghg3[masknz33]
    
    tnghg33_merged = tghg3_sel10.merge(tnghg3, on='Company')
    tnghg33_merged['Normalised GHG3'] = (tnghg33_merged['Total GHG3']*1000)/tnghg33_merged['Revenue']
    tnghg33_merged['Normalised GHG3 Rounded'] = tnghg33_merged['Normalised GHG3'].round(2)
    
    tnghg33_merged = tnghg33_merged.sort_values(by=['Total GHG3','Company'], axis = 0, ascending=False)

    # Apply the function to each row of the DataFrame
    tnghg33_merged['Modified Labels'] = tnghg33_merged.apply(category_label, axis=1)


    tnghg33_merged = tnghg33_merged.sort_values(by=[k1,'Company'], axis = 0, ascending=False)
    
    fontsize = 150/tnghg33_merged.shape[0]
    if (fontsize > 15):
        fontsize = 15
    
    fig2 = px.bar(tnghg33_merged, x='Modified Labels', y=k1,text=k2 ,color_discrete_sequence=['#2774AE'], height = 1000)
    
    fig2.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica",font=dict(size=fontsize))
    fig2.update_xaxes(title=None)
    fig2.update_yaxes(title=None)
    fig2.update_layout(
    title=go.layout.Title(
        text=k3,
        #xref="paper",
        x=0.5,
        font_size=30
    ))
    fig2.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in tnghg33_merged['Modified Labels'].unique().tolist()]
    fig2.update_xaxes(tickmode='array', tickvals=list(range(len(tnghg33_merged['Modified Labels'].unique().tolist()))), ticktext=wrapped_labels)


    return fig2



def water_util(sector,company_list):
    
    dfwwc = df.loc[:,['GICS.Sector','Company.Name','Revenue','CM10a.Response','CM10c.Response']]
    dfwwc = dfwwc.rename(columns={"Company.Name":"CompanyName","CM10a.Response":"Water Withdrawal","CM10c.Response":"Water Consumption"})
    dfwwc['Withdrawal'] = dfwwc['Water Withdrawal']/dfwwc['Revenue']
    dfwwc['Consumption'] = dfwwc['Water Consumption']/dfwwc['Revenue']
    
    dfwwc = dfwwc.loc[dfwwc['GICS.Sector'] == sector,['CompanyName','Withdrawal','Consumption']]
    dfwwc_melted = pd.melt(dfwwc, id_vars='CompanyName')
    dfwwc_melted['value_rounded'] = dfwwc_melted['value'].round(2).astype(str).str.replace('nan', 'NR')
    
    mask12 = dfwwc_melted['CompanyName'].isin(company_list)
    dfwwc_prev10 = dfwwc_melted[mask12].sort_values(by='value', axis=0, ascending=False)
    
    color_mapping = {'Withdrawal': '#2774AE',
                     'Consumption': '#F47C30'}
    
    fontsize = 300/dfwwc_prev10.shape[0]
    if (fontsize > 15):
        fontsize = 15
    
    fig8 = px.bar(dfwwc_prev10, x='CompanyName', y='value',color='variable',text='value_rounded',color_discrete_map=color_mapping,height = 780, barmode='group')
    fig8.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica", font=dict(size=fontsize), legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.85))
    fig8.update_xaxes(title=None)
    fig8.update_yaxes(title=None)
    fig8.update_layout(
        title=go.layout.Title(
            text="Water Utilization<br><sup>(in mega litres per $M revenue)</sup>",
            #xref="paper",
            x=0.5,
            font_size=30
        ))
    fig8.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in dfwwc_prev10['CompanyName'].unique().tolist()]
    fig8.update_xaxes(tickmode='array', tickvals=list(range(len(dfwwc_prev10['CompanyName'].unique().tolist()))), ticktext=wrapped_labels)

    return fig8


def biodiver(sector,company_list):
    dfbi = df.loc[:,['GICS.Sector','Company.Name','Revenue','CM9.Area.in.hectares']]
    dfbi = dfbi.rename(columns={"Company.Name":"CompanyName","CM9.Area.in.hectares":"Biodiversity Areas"})
    dfbi['Normalised Biodiversity Areas'] = dfbi['Biodiversity Areas']/dfbi['Revenue']
    
    dfbi = dfbi.loc[dfbi['GICS.Sector'] == sector]
    dfbi['value_rounded'] = dfbi['Normalised Biodiversity Areas'].round(2).astype(str).str.replace('nan', 'NR')
    #dfbi_sorted = dfbi.sort_values(by='value_rounded', axis=0, ascending=False).head(10)
    
    mask7 = dfbi['CompanyName'].isin(company_list)
    dfbi_prev10 = dfbi[mask7].sort_values(by='Normalised Biodiversity Areas', axis=0, ascending=False)

    fontsize = 150/dfbi_prev10.shape[0]
    if (fontsize > 15):
        fontsize = 15
    
    fig7 = px.bar(dfbi_prev10, x="CompanyName", y="Normalised Biodiversity Areas",text='value_rounded', color_discrete_sequence=['#2774AE','#FFB81C','#F47C30'],barmode="group", height = 780)
    fig7.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica",
                  font=dict(size=fontsize))


    fig7.update_xaxes(title=None)
    fig7.update_yaxes(title=None)
    fig7.update_layout(
    title=go.layout.Title(
        text="Biodiversity Areas<br><sup>(in hectares per $M revenue)</sup>",
        #xref="paper",
        x=0.5,
        font_size = 30
    ))
    fig7.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in dfbi_prev10['CompanyName'].unique().tolist()]
    fig7.update_xaxes(tickmode='array', tickvals=list(range(len(dfbi_prev10['CompanyName'].unique().tolist()))), ticktext=wrapped_labels)

    return fig7


def enviromentalgovernacemetrics(sector,company_list):
    emg1 = df.loc[:,['Company.Name', 'Audited.Report','TCFD New']]
    emg1.rename(columns={"Company.Name": "Company",
                     "Audited.Report": "GHG Assurance",
                     "TCFD New":"TCFD Disclosure"},inplace=True)

    mask = emg1['Company'].isin(company_list)
    emg1 = emg1[mask]

    categorical_mapping = {1.0: 'Yes', 0.5: 'Partial', 0.0: 'No'}
    emg1['GHG Assurance'] = emg1['GHG Assurance'].map(categorical_mapping)
    emg1['TCFD Disclosure'] = emg1['TCFD Disclosure'].map(categorical_mapping)
    
    emg2 = dfnz2.loc[:,['Enter the full company name','Does the company identify an environmental skill as a key board competency (i.e. included chart with all board members and their skills)?', 'Is Executive Compensation tied to any ESG milestones?']]
    emg2.rename(columns={"Enter the full company name": "Company",
                     "Does the company identify an environmental skill as a key board competency (i.e. included chart with all board members and their skills)?": "Environmental Skill as key board competency",
                     "Is Executive Compensation tied to any ESG milestones?":"Executive Compensation tied to ESG milestones"},inplace=True)

    mask = emg2['Company'].isin(company_list)
    emg2 = emg2[mask]
    
    emg = emg1.merge(emg2, on='Company')
    
    emg_melted = emg.melt(id_vars = 'Company', var_name='Metric', value_name='Status')
    emg_melted = emg_melted.sort_values(by=['Metric','Company'])
    
    color_mapping = {'Yes': '#4E7E6B',
                     'No': '#F43A00',
                     'Partial': '#FFD100'}
    
    emg_melted['Company '] = emg_melted['Company'].apply(lambda x: x[:x.find(' ', x.find(' ') + 1)] + '<br>' + x[x.find(' ', x.find(' ') + 1) + 1:] if x.count(' ') >= 2 else x)

    
    fig = px.scatter(emg_melted, y="Company ", x="Metric", color="Status",
                 color_discrete_map=color_mapping,height = 920, 
                 title='Environmental Metrics Governance')
    fig.update_traces(marker_size=34)
    fig.update_layout(plot_bgcolor="white", font=dict(family="Verdana",size=15), title_font_family="Helvetica", title_x=0.5,
                 legend=dict( yanchor="bottom",orientation="h",  xanchor="right", x=1, title=None),
                 margin=dict(t=190),title_font_size=30,xaxis_tickformat='wrap',
                 xaxis=dict(side="top",categoryorder='array', categoryarray= emg_melted["Company"].unique()))
    fig.update_yaxes(title=None)
    fig.update_xaxes(categoryorder='category ascending',title=None, tickformat='wrap')

    max_label_length = 20
    wrapped_labels = [label[:[m.start() for m in re.finditer(r' ', label)][2]] + '<br>' + label[[m.start() for m in re.finditer(r' ', label)][2]:] if label.find(' ')>5 else label for label in emg_melted['Metric'].unique().tolist()]
    fig.update_xaxes(tickmode='array', tickvals=list(range(len(emg_melted['Metric'].unique().tolist()))), ticktext=wrapped_labels)

    fig.add_shape(
        type="line",
        x0=0,
        y0=1,
        x1=1,
        y1=1,
        line=dict(
            color="black",
            width=1,
        ),
        xref="paper",
        yref="paper"
    )
    
    return fig,emg


def tcfdpercentage(sector,company_list):
    tcfd = df.loc[:,['Company.Name','TCFD average']]
    tcfd.rename(columns={"Company.Name": "Company"},inplace=True)

    tcfd['TCFD average'] = tcfd['TCFD average']*100
    tcfd['label'] = tcfd['TCFD average'].astype(int).astype(str) + '%'

    mask = tcfd['Company'].isin(company_list)
    tcfd = tcfd[mask].sort_values(by=['TCFD average','Company'],ascending=False)
    
    fontsize = 150/tcfd.shape[0]
    if (fontsize > 15):
        fontsize = 15
    
    fig7 = px.bar(tcfd, x='Company', y='TCFD average',text='label',
              color_discrete_sequence=['#003B5C'],barmode="group")
    fig7.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica")
    fig7.update_xaxes(title=None)
    fig7.update_yaxes(title=None)
    fig7.update_layout(
        title=go.layout.Title(
            text="TCFD Disclosure Percentage<br><sup></sup>",
            #xref="paper",
            x=0.5
        ))
    fig7.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in tcfd['Company'].unique().tolist()]
    fig7.update_xaxes(tickmode='array', tickvals=list(range(len(tcfd['Company'].unique().tolist()))), ticktext=wrapped_labels)

    fig7.update_layout(height = 780,font_family='Helvetica', title_font_family="Helvetica",font=dict(size=fontsize))
    
    return fig7


def boardmember(sector,company_list):
    
    pobm = dfnz2.loc[:,['Enter the full company name','Percent of board with enviro skill']]
    pobm.rename(columns={"Enter the full company name": "Company",
                    "Percent of board with enviro skill":"pobm"},inplace=True)

    pobm['pobm'] = pobm['pobm']*100
    pobm['label'] = pobm['pobm'].astype(int).astype(str) + '%'

    mask = pobm['Company'].isin(company_list)
    pobm = pobm[mask].sort_values(by=['pobm','Company'],ascending=False)
    
    fontsize = 150/pobm.shape[0]
    if (fontsize > 15):
        fontsize = 15
    
    fig8 = px.bar(pobm, x='Company', y='pobm',text='label',
              color_discrete_sequence=['#003B5C'],barmode="group")
    fig8.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica")
    fig8.update_xaxes(title=None)
    fig8.update_yaxes(title=None)
    fig8.update_layout(
        title=go.layout.Title(
            text="Percentage of Board Members with Environmental/Sustainability Capabilities<br><sup></sup>",
            #xref="paper",
            x=0.5
        ))
    fig8.update_traces(textposition='outside', selector=dict(type='bar'))

    wrapped_labels = [label.replace(' ', '<br>').replace('-', '<br>') for label in pobm['Company'].unique().tolist()]
    fig8.update_xaxes(tickmode='array', tickvals=list(range(len(pobm['Company'].unique().tolist()))), ticktext=wrapped_labels)

    fig8.update_layout(height = 780,font_family='Helvetica', title_font_family="Helvetica",font=dict(size=fontsize))
    
    return fig8


def environmentalgoals(sector,company_list):
    egoal = dfnz2.loc[:,['Enter the full company name',
                     'Does the company have a Net Zero/carbon neutrality goal?',
                     'Does the Net Zero goal cover Scope 1 emissions?',
                     'Does the Net Zero goal cover Scope 2 emissions?',
                     'Does the Net Zero goal cover all of Scope 3 emissions?',
                     'Is the company on the Science Based Targets Institute as working with them to develop or track it\'s Net Zero Goal?',
                     'What is the status of the company\'s goal with the Science Based Target Institute?',
                     'Does the company have an interim goal on the way to Net Zero?',
                     'Does the proxy statement mention "Net Zero" or "Carbon neutral" targets?']]
    egoal.rename(columns={"Enter the full company name": "Company",
                     "Does the company have a Net Zero/carbon neutrality goal?": "Has a Net Zero Goal (NZG)",
                     "Does the Net Zero goal cover Scope 1 emissions?":"NZG covers Scope 1 emissions",
                     "Does the Net Zero goal cover Scope 2 emissions?":"NZG covers Scope 2 emissions",
                     "Does the Net Zero goal cover all of Scope 3 emissions?":"NZG covers all of Scope 3 emissions",
                     "Is the company on the Science Based Targets Institute as working with them to develop or track it's Net Zero Goal?":"Working with the SBTI ",
                     "What is the status of the company's goal with the Science Based Target Institute?":"Status of the goal with SBTI",
                     "Does the company have an interim goal on the way to Net Zero?":"Has an interim goal on the way to Net Zero",
                     "Does the proxy statement mention \"Net Zero\" or \"Carbon neutral\" targets?":"\"Net Zero\" or \"Carbon neutral\" mentioned in Proxy Statement"},inplace=True)

    mask = egoal['Company'].isin(company_list)
    egoal = egoal[mask].fillna('Not Applicable')

    #egoal.loc[222,'"Net Zero" or "Carbon neutral" mentioned in Proxy Statement'] = 'Not Applicable'

    egoal.sort_values(by='Company')
    
    
    egoal_melted = egoal.melt(id_vars = 'Company', var_name='Metric', value_name='Status')
    egoal_melted = egoal_melted.sort_values(by=['Metric','Company'])
    
    column_order = ['Has a Net Zero Goal (NZG)',
                'NZG covers Scope 1 emissions',
                'NZG covers Scope 2 emissions',
                'NZG covers all of Scope 3 emissions',
                'Working with the SBTI ',
                'Status of the goal with SBTI',
                'Has an interim goal on the way to Net Zero',
                '"Net Zero" or "Carbon neutral" mentioned in Proxy Statement']
    
    color_mapping = {'Yes': '#4E7E6B',
                     'No': '#F43A00',
                     'Not Applicable': '#313339',
                     'Validated': '#2774AE',
                     'Committed': '#FFD100'}
    
    #egoal_melted['Company']=egoal_melted['Company'].astype('str')
    
    egoal_melted['Company '] = egoal_melted['Company'].apply(lambda x: x[:x.find(' ', x.find(' ') + 1)] + '<br>' + x[x.find(' ', x.find(' ') + 1) + 1:] if x.count(' ') >= 2 else x)

    
    fig9 = px.scatter(egoal_melted, y="Company ", x="Metric", color="Status",
                 color_discrete_map=color_mapping,height = 920, 
                 title='Environmental Goals')
    fig9.update_traces(marker_size=34)
    fig9.update_layout(plot_bgcolor="white", font=dict(family="Verdana",size=11), title_font_family="Helvetica", title_x=0.5,
                 legend=dict( yanchor="bottom",orientation="h",  xanchor="right", x=1, title=None),
                 margin=dict(t=190),title_font_size=30,xaxis_tickformat='wrap',
                 xaxis=dict(side="top",categoryorder='array', categoryarray= column_order))
    fig9.update_yaxes(title=None)
    fig9.update_xaxes(title=None, tickformat='wrap')

    max_label_length = 20
    wrapped_labels = [label[:[m.start() for m in re.finditer(r' ', label)][1]] + '<br>' + label[[m.start() for m in re.finditer(r' ', label)][1]:] if label.find(' ')>0 else label for label in column_order]
    wrapped_labels = [label[:[m.start() for m in re.finditer(r' ', label)][3]] + '<br>' + label[[m.start() for m in re.finditer(r' ', label)][3]:] if label.find(' ')>0 else label for label in wrapped_labels]
    q = wrapped_labels[6]
    wrapped_labels[6] = [q[:[m.start() for m in re.finditer(r' ', q)][6]] + '<br>' + q[[m.start() for m in re.finditer(r' ', q)][6]:]]
    p = wrapped_labels[7]
    wrapped_labels[7] = [p[:[m.start() for m in re.finditer(r' ', p)][5]] + '<br>' + p[[m.start() for m in re.finditer(r' ', p)][5]:]]
# p = wrapped_labels[7]
# wrapped_labels[7] = [p[:[m.start() for m in re.finditer(r' ', p)][4]] + '<br>' + p[[m.start() for m in re.finditer(r' ', p)][4]:]]
    fig9.update_xaxes(tickmode='array', tickvals=list(range(len(egoal_melted['Metric'].unique().tolist()))), ticktext=wrapped_labels)

    fig9.add_shape(
        type="line",
        x0=0,
        y0=1,
        x1=1,
        y1=1,
        line=dict(
            color="black",
            width=1,
        ),
        xref="paper",
        yref="paper"
    )
    
    return fig9,egoal

def netzerotarget(sector,company_list):
    dfty2 = dfnz2.loc[:,['Enter the full company name',
                     'Average NZ Target Year']].fillna(2015)
    dfty2.loc[311,'Average NZ Target Year'] = 2050



    dfty2['Average NZ Target Year'] = dfty2['Average NZ Target Year'].astype(int)
    dfty2['barlabel'] = dfty2['Average NZ Target Year'].astype(str).str.replace('2015', 'No NZ Goal')

    mask = dfty2['Enter the full company name'].isin(company_list)
    dfty2 = dfty2[mask].sort_values(by=['Average NZ Target Year','Enter the full company name'])

    dfty2['Enter the full company name'] = dfty2['Enter the full company name'].apply(lambda x: x + '   ')
    
    fig29 = px.bar(dfty2, y='Enter the full company name', x='Average NZ Target Year',text='barlabel',color_discrete_sequence=['#003B5C'],barmode="group")
    fig29.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica")
    fig29.update_xaxes(title=None,range=[2014.99, 2062], showgrid=True, gridcolor='lightgrey')
    fig29.update_yaxes(title=None)
    fig29.update_layout(
        title=go.layout.Title(
            text="Net Zero Target<br><sup></sup>",
            #xref="paper",
            x=0.5
        ))
    fig29.update_traces(textposition='outside', selector=dict(type='bar'))

    fig29.update_layout( height = 780,font_family='Helvetica', title_font_family="Helvetica",font=dict(size=22))
    
    return fig29

def index_calculator(sector, company_list, governance_weight, goals_weight, performance_weight, firm_ind, new_firm_perf, new_firm_gov, new_firm_goal):
    
    emg1 = df.loc[:,['Company.Name', 'Audited.Report','TCFD New']]
    emg1.rename(columns={"Company.Name": "Company",
                     "Audited.Report": "GHG Assurance",
                     "TCFD New":"TCFD Disclosure"},inplace=True)

    mask = emg1['Company'].isin(company_list)
    emg1 = emg1[mask]

    categorical_mapping = {1.0: 'Yes', 0.5: 'Partial', 0.0: 'No'}
    emg1['GHG Assurance'] = emg1['GHG Assurance'].map(categorical_mapping)
    emg1['TCFD Disclosure'] = emg1['TCFD Disclosure'].map(categorical_mapping)
    
    emg2 = dfnz2.loc[:,['Enter the full company name','Does the company identify an environmental skill as a key board competency (i.e. included chart with all board members and their skills)?', 'Is Executive Compensation tied to any ESG milestones?']]
    emg2.rename(columns={"Enter the full company name": "Company",
                     "Does the company identify an environmental skill as a key board competency (i.e. included chart with all board members and their skills)?": "Environmental Skill as key board competency",
                     "Is Executive Compensation tied to any ESG milestones?":"Executive Compensation tied to ESG milestones"},inplace=True)

    mask = emg2['Company'].isin(company_list)
    emg2 = emg2[mask]
    
    emg = emg1.merge(emg2, on='Company')
    
    
    #emg = enviromentalgovernacemetrics(sector,company_list)[1]
    emg22 = emg.copy()
    
    #encoding all the categorical variables with the mapping 1.0: 'Yes', 0.5: 'Partial', 0.0: 'No'
    categorical_mapping = {'Yes': 1.0, 'Partial':0.5, 'No': 0.0}
    emg22['GHG Assurance'] = emg['GHG Assurance'].map(categorical_mapping)
    emg22['TCFD Disclosure'] = emg['TCFD Disclosure'].map(categorical_mapping)
    emg22['Environmental Skill as key board competency'] = emg['Environmental Skill as key board competency'].map(categorical_mapping)
    emg22['Executive Compensation tied to ESG milestones'] = emg['Executive Compensation tied to ESG milestones'].map(categorical_mapping)
    
    #########Additional company
    #firm_ind = 0
    if (firm_ind == 1):
        emg22.loc[len(emg22)] = new_firm_gov
        
    #################################
    
    
    
    #Creating a new column 'index' having the average of all the categorical variables
    emg22['index'] = emg22[['GHG Assurance','TCFD Disclosure','Environmental Skill as key board competency','Executive Compensation tied to ESG milestones']].mean(axis=1)
    emg22 = emg22.sort_values(by='index',ascending=False)
    
    single_gov_score = emg22.loc[emg22['Company']==new_firm_gov[0],'index'].values[0].round(2)
    
    
    egoal = dfnz2.loc[:,['Enter the full company name',
                     'Does the company have a Net Zero/carbon neutrality goal?',
                     'Does the Net Zero goal cover Scope 1 emissions?',
                     'Does the Net Zero goal cover Scope 2 emissions?',
                     'Does the Net Zero goal cover all of Scope 3 emissions?',
                     'Is the company on the Science Based Targets Institute as working with them to develop or track it\'s Net Zero Goal?',
                     'What is the status of the company\'s goal with the Science Based Target Institute?',
                     'Does the company have an interim goal on the way to Net Zero?',
                     'Does the proxy statement mention "Net Zero" or "Carbon neutral" targets?']]
    egoal.rename(columns={"Enter the full company name": "Company",
                     "Does the company have a Net Zero/carbon neutrality goal?": "Has a Net Zero Goal (NZG)",
                     "Does the Net Zero goal cover Scope 1 emissions?":"NZG covers Scope 1 emissions",
                     "Does the Net Zero goal cover Scope 2 emissions?":"NZG covers Scope 2 emissions",
                     "Does the Net Zero goal cover all of Scope 3 emissions?":"NZG covers all of Scope 3 emissions",
                     "Is the company on the Science Based Targets Institute as working with them to develop or track it's Net Zero Goal?":"Working with the SBTI ",
                     "What is the status of the company's goal with the Science Based Target Institute?":"Status of the goal with SBTI",
                     "Does the company have an interim goal on the way to Net Zero?":"Has an interim goal on the way to Net Zero",
                     "Does the proxy statement mention \"Net Zero\" or \"Carbon neutral\" targets?":"\"Net Zero\" or \"Carbon neutral\" mentioned in Proxy Statement"},inplace=True)

    mask = egoal['Company'].isin(company_list)
    egoal = egoal[mask].fillna('Not Applicable')

    #egoal.loc[222,'"Net Zero" or "Carbon neutral" mentioned in Proxy Statement'] = 'Not Applicable'
    
    #egoal = environmentalgoals(sector,company_list)[1]
    egoal22 = egoal.copy()
    categorical_mapping2 = {'Yes': 1.0, 'Committed':1.0, 'No': 0.0, 'Not Applicable': 0.0, 'Validated': 0.5}
    egoal22['Has a Net Zero Goal (NZG)'] = egoal['Has a Net Zero Goal (NZG)'].map(categorical_mapping2)
    egoal22['NZG covers Scope 1 emissions'] = egoal['NZG covers Scope 1 emissions'].map(categorical_mapping2)
    egoal22['NZG covers Scope 2 emissions'] = egoal['NZG covers Scope 2 emissions'].map(categorical_mapping2)
    egoal22['NZG covers all of Scope 3 emissions'] = egoal['NZG covers all of Scope 3 emissions'].map(categorical_mapping2)
    egoal22['Working with the SBTI '] = egoal['Working with the SBTI '].map(categorical_mapping2)
    egoal22['Status of the goal with SBTI'] = egoal['Status of the goal with SBTI'].map(categorical_mapping2)
    egoal22['Has an interim goal on the way to Net Zero'] = egoal['Has an interim goal on the way to Net Zero'].map(categorical_mapping2)
    egoal22['"Net Zero" or "Carbon neutral" mentioned in Proxy Statement'] = egoal['"Net Zero" or "Carbon neutral" mentioned in Proxy Statement'].map(categorical_mapping2)
    
    #########Additional company
    #firm_ind = 0
    if (firm_ind == 1):
        egoal22.loc[len(egoal22)] = new_firm_goal
        
    #################################
    
    egoal22['index'] = egoal22[['Has a Net Zero Goal (NZG)',
                                'NZG covers Scope 1 emissions',
                                'NZG covers Scope 2 emissions',
                                'NZG covers all of Scope 3 emissions',
                                'Working with the SBTI ',
                                'Status of the goal with SBTI',
                                'Has an interim goal on the way to Net Zero',
                                '"Net Zero" or "Carbon neutral" mentioned in Proxy Statement']].mean(axis=1)
    egoal22 = egoal22.sort_values(by='index',ascending=False)
    
    single_goal_score = egoal22.loc[egoal22['Company']==new_firm_gov[0],'index'].values[0].round(2)
    
    envperf = dfnz2.loc[:,['Enter the full company name', 'What is the company\'s current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)',
                       'Enter the company\'s Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)',
                       'Enter the company\'s Scope 3 emissions in metric tons of CO2e.',
                       ]]
    envperf.rename(columns={"Enter the full company name": "Company",
                     "What is the company's current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)": "Total GHG1",
                     "Enter the company\'s Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)": "Total market-based GHG2",
                     "Enter the company\'s Scope 3 emissions in metric tons of CO2e.":"Total GHG3",
},inplace=True)

    envperf2 = df.loc[:,['GICS.Sector','Company.Name','Revenue','CM10c.Response','CM10a.Response','CM9.Area.in.hectares']]
    envperf2 = envperf2.rename(columns={"Company.Name":"Company","CM10c.Response":"Water Consumption"
                                    ,"CM10a.Response":"Water Withdrawal","CM9.Area.in.hectares":"Biodiversity Areas"})


    envperf_merged = envperf.merge(envperf2,on='Company', how='right')
    envperf_merged.loc[envperf_merged['Company'] == 'Yum! Brands, Inc.','Total GHG1'] = 4291918
    
    mask8 = envperf_merged['Company'].isin(company_list)
    envperf_merged = envperf_merged[mask8]
    
    
    #########Additional company
    #firm_ind = 0
    if (firm_ind == 1):
        envperf_merged.loc[len(envperf_merged)] = new_firm_perf
        
    #################################
        
    
    envperf_merged['Normalised GHG1'] = pd.to_numeric(envperf_merged['Total GHG1'])/envperf_merged['Revenue']
    envperf_merged['Normalised GHG2'] = envperf_merged['Total market-based GHG2']/envperf_merged['Revenue']
    envperf_merged['Normalised GHG3'] = envperf_merged['Total GHG3']/envperf_merged['Revenue']
    envperf_merged['Normalised Water Consumption'] = envperf_merged['Water Consumption']/envperf_merged['Revenue']
    envperf_merged['Normalised Water Withdrawal'] = envperf_merged['Water Withdrawal']/envperf_merged['Revenue']
    envperf_merged['Normalised Biodiversity Areas'] = envperf_merged['Biodiversity Areas']/envperf_merged['Revenue']
    
    envperf_prev10 = envperf_merged

#     mask8 = envperf_merged['Company'].isin(company_list)
#     envperf_prev10 = envperf_merged[mask8]
    
    envperf_prev10['GHG1 Percentile Rank'] = (1-envperf_prev10['Normalised GHG1'].rank(pct=True)).fillna(0)
    envperf_prev10['GHG2 Percentile Rank'] = (1-envperf_prev10['Normalised GHG2'].rank(pct=True)).fillna(0)
    envperf_prev10['GHG3 Percentile Rank'] = (1-envperf_prev10['Normalised GHG3'].rank(pct=True)).fillna(0)
    envperf_prev10['Water Consumption Percentile Rank'] = (1-envperf_prev10['Normalised Water Consumption'].rank(pct=True)).fillna(0)
    envperf_prev10['Water Withdrawal Percentile Rank'] = (1-envperf_prev10['Normalised Water Withdrawal'].rank(pct=True)).fillna(0)
    envperf_prev10['Biodiversity Areas Percentile Rank'] = (envperf_prev10['Normalised Biodiversity Areas'].rank(pct=True)).fillna(0)
    
    envperf_prev10['envperfscore'] = envperf_prev10[['GHG1 Percentile Rank','GHG2 Percentile Rank','GHG3 Percentile Rank','Water Consumption Percentile Rank','Water Withdrawal Percentile Rank','Biodiversity Areas Percentile Rank']].mean(axis=1)
    envperf_prev10 = envperf_prev10.sort_values(by='envperfscore', axis=0, ascending=False)
    perfscore = envperf_prev10[['Company','envperfscore']]
    
    single_perf_score = envperf_prev10.loc[envperf_prev10['Company']==new_firm_perf[0],'envperfscore'].values[0].round(2)
    
    #joining the two dataframes emg22 and egoal22 on the column 'Company'
    
    emg22 = emg22.rename(columns={'index':'Environmental Governance Index'})
    egoal22 = egoal22.rename(columns={'index':'Environmental Goals Index'})
    
    perfscore = perfscore.set_index('Company')
    emg22 = emg22.set_index('Company')
    egoal22 = egoal22.set_index('Company')
    emg22 = emg22.join(egoal22, on='Company')
    emg22 = emg22.join(perfscore, on='Company')
    
    emg22 = emg22.reset_index()

    #Assigning weights to the two indexes
#     goals_weight = 0.4
#     governance_weight = 0.6

    #Calculating the overall index using the weights
    weight_sum = governance_weight + goals_weight + performance_weight
    
    emg22['Overall index'] = emg22['Environmental Governance Index']*(governance_weight/weight_sum) + emg22['Environmental Goals Index']*(goals_weight/weight_sum) + emg22['envperfscore']*(performance_weight/weight_sum)
    emg22 = emg22.sort_values(by='Overall index',ascending=True)
    
#     print(emg22.loc[emg22['Company']==new_firm_gov[0],:])
#     print(emg22.loc[emg22['Company']==new_firm_gov[0],'Overall index'].values[0])
#     print(emg22)
    
    single_overall_score = emg22.loc[emg22['Company']==new_firm_gov[0],'Overall index'].values[0].round(2)
    
    return single_gov_score, single_goal_score, single_perf_score, single_overall_score
    
    

    

def overallindex(sector, company_list, governance_weight, goals_weight, performance_weight, firm_ind, new_firm_perf, new_firm_gov, new_firm_goal):
    
    emg1 = df.loc[:,['Company.Name', 'Audited.Report','TCFD New']]
    emg1.rename(columns={"Company.Name": "Company",
                     "Audited.Report": "GHG Assurance",
                     "TCFD New":"TCFD Disclosure"},inplace=True)

    mask = emg1['Company'].isin(company_list)
    emg1 = emg1[mask]

    categorical_mapping = {1.0: 'Yes', 0.5: 'Partial', 0.0: 'No'}
    emg1['GHG Assurance'] = emg1['GHG Assurance'].map(categorical_mapping)
    emg1['TCFD Disclosure'] = emg1['TCFD Disclosure'].map(categorical_mapping)
    
    emg2 = dfnz2.loc[:,['Enter the full company name','Does the company identify an environmental skill as a key board competency (i.e. included chart with all board members and their skills)?', 'Is Executive Compensation tied to any ESG milestones?']]
    emg2.rename(columns={"Enter the full company name": "Company",
                     "Does the company identify an environmental skill as a key board competency (i.e. included chart with all board members and their skills)?": "Environmental Skill as key board competency",
                     "Is Executive Compensation tied to any ESG milestones?":"Executive Compensation tied to ESG milestones"},inplace=True)

    mask = emg2['Company'].isin(company_list)
    emg2 = emg2[mask]
    
    emg = emg1.merge(emg2, on='Company')
    
    
    #emg = enviromentalgovernacemetrics(sector,company_list)[1]
    emg22 = emg.copy()
    
    #encoding all the categorical variables with the mapping 1.0: 'Yes', 0.5: 'Partial', 0.0: 'No'
    categorical_mapping = {'Yes': 1.0, 'Partial':0.5, 'No': 0.0}
    emg22['GHG Assurance'] = emg['GHG Assurance'].map(categorical_mapping)
    emg22['TCFD Disclosure'] = emg['TCFD Disclosure'].map(categorical_mapping)
    emg22['Environmental Skill as key board competency'] = emg['Environmental Skill as key board competency'].map(categorical_mapping)
    emg22['Executive Compensation tied to ESG milestones'] = emg['Executive Compensation tied to ESG milestones'].map(categorical_mapping)
    
    #########Additional company
    #firm_ind = 0
    if (firm_ind == 1):
        emg22.loc[len(emg22)] = new_firm_gov
        
    #################################
    
    
    
    #Creating a new column 'index' having the average of all the categorical variables
    emg22['index'] = emg22[['GHG Assurance','TCFD Disclosure','Environmental Skill as key board competency','Executive Compensation tied to ESG milestones']].mean(axis=1)
    emg22 = emg22.sort_values(by='index',ascending=False)
    
    
    egoal = dfnz2.loc[:,['Enter the full company name',
                     'Does the company have a Net Zero/carbon neutrality goal?',
                     'Does the Net Zero goal cover Scope 1 emissions?',
                     'Does the Net Zero goal cover Scope 2 emissions?',
                     'Does the Net Zero goal cover all of Scope 3 emissions?',
                     'Is the company on the Science Based Targets Institute as working with them to develop or track it\'s Net Zero Goal?',
                     'What is the status of the company\'s goal with the Science Based Target Institute?',
                     'Does the company have an interim goal on the way to Net Zero?',
                     'Does the proxy statement mention "Net Zero" or "Carbon neutral" targets?']]
    egoal.rename(columns={"Enter the full company name": "Company",
                     "Does the company have a Net Zero/carbon neutrality goal?": "Has a Net Zero Goal (NZG)",
                     "Does the Net Zero goal cover Scope 1 emissions?":"NZG covers Scope 1 emissions",
                     "Does the Net Zero goal cover Scope 2 emissions?":"NZG covers Scope 2 emissions",
                     "Does the Net Zero goal cover all of Scope 3 emissions?":"NZG covers all of Scope 3 emissions",
                     "Is the company on the Science Based Targets Institute as working with them to develop or track it's Net Zero Goal?":"Working with the SBTI ",
                     "What is the status of the company's goal with the Science Based Target Institute?":"Status of the goal with SBTI",
                     "Does the company have an interim goal on the way to Net Zero?":"Has an interim goal on the way to Net Zero",
                     "Does the proxy statement mention \"Net Zero\" or \"Carbon neutral\" targets?":"\"Net Zero\" or \"Carbon neutral\" mentioned in Proxy Statement"},inplace=True)

    mask = egoal['Company'].isin(company_list)
    egoal = egoal[mask].fillna('Not Applicable')

    egoal.loc[222,'"Net Zero" or "Carbon neutral" mentioned in Proxy Statement'] = 'Not Applicable'
    
    #egoal = environmentalgoals(sector,company_list)[1]
    egoal22 = egoal.copy()
    categorical_mapping2 = {'Yes': 1.0, 'Committed':1.0, 'No': 0.0, 'Not Applicable': 0.0, 'Validated': 0.5}
    egoal22['Has a Net Zero Goal (NZG)'] = egoal['Has a Net Zero Goal (NZG)'].map(categorical_mapping2)
    egoal22['NZG covers Scope 1 emissions'] = egoal['NZG covers Scope 1 emissions'].map(categorical_mapping2)
    egoal22['NZG covers Scope 2 emissions'] = egoal['NZG covers Scope 2 emissions'].map(categorical_mapping2)
    egoal22['NZG covers all of Scope 3 emissions'] = egoal['NZG covers all of Scope 3 emissions'].map(categorical_mapping2)
    egoal22['Working with the SBTI '] = egoal['Working with the SBTI '].map(categorical_mapping2)
    egoal22['Status of the goal with SBTI'] = egoal['Status of the goal with SBTI'].map(categorical_mapping2)
    egoal22['Has an interim goal on the way to Net Zero'] = egoal['Has an interim goal on the way to Net Zero'].map(categorical_mapping2)
    egoal22['"Net Zero" or "Carbon neutral" mentioned in Proxy Statement'] = egoal['"Net Zero" or "Carbon neutral" mentioned in Proxy Statement'].map(categorical_mapping2)
    
    #########Additional company
    #firm_ind = 0
    if (firm_ind == 1):
        egoal22.loc[len(egoal22)] = new_firm_goal
        
    #################################
    
    egoal22['index'] = egoal22[['Has a Net Zero Goal (NZG)',
                                'NZG covers Scope 1 emissions',
                                'NZG covers Scope 2 emissions',
                                'NZG covers all of Scope 3 emissions',
                                'Working with the SBTI ',
                                'Status of the goal with SBTI',
                                'Has an interim goal on the way to Net Zero',
                                '"Net Zero" or "Carbon neutral" mentioned in Proxy Statement']].mean(axis=1)
    egoal22 = egoal22.sort_values(by='index',ascending=False)
    
    envperf = dfnz2.loc[:,['Enter the full company name', 'What is the company\'s current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)',
                       'Enter the company\'s Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)',
                       'Enter the company\'s Scope 3 emissions in metric tons of CO2e.',
                       ]]
    envperf.rename(columns={"Enter the full company name": "Company",
                     "What is the company's current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)": "Total GHG1",
                     "Enter the company\'s Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)": "Total market-based GHG2",
                     "Enter the company\'s Scope 3 emissions in metric tons of CO2e.":"Total GHG3",
},inplace=True)

    envperf2 = df.loc[:,['GICS.Sector','Company.Name','Revenue','CM10c.Response','CM10a.Response','CM9.Area.in.hectares']]
    envperf2 = envperf2.rename(columns={"Company.Name":"Company","CM10c.Response":"Water Consumption"
                                    ,"CM10a.Response":"Water Withdrawal","CM9.Area.in.hectares":"Biodiversity Areas"})


    envperf_merged = envperf.merge(envperf2,on='Company', how='right')
    envperf_merged.loc[envperf_merged['Company'] == 'Yum! Brands, Inc.','Total GHG1'] = 4291918
    
    mask8 = envperf_merged['Company'].isin(company_list)
    envperf_merged = envperf_merged[mask8]
    
    
    #########Additional company
    #firm_ind = 0
    if (firm_ind == 1):
        envperf_merged.loc[len(envperf_merged)] = new_firm_perf
        
    #################################
        
    
    envperf_merged['Normalised GHG1'] = pd.to_numeric(envperf_merged['Total GHG1'])/envperf_merged['Revenue']
    envperf_merged['Normalised GHG2'] = envperf_merged['Total market-based GHG2']/envperf_merged['Revenue']
    envperf_merged['Normalised GHG3'] = envperf_merged['Total GHG3']/envperf_merged['Revenue']
    envperf_merged['Normalised Water Consumption'] = envperf_merged['Water Consumption']/envperf_merged['Revenue']
    envperf_merged['Normalised Water Withdrawal'] = envperf_merged['Water Withdrawal']/envperf_merged['Revenue']
    envperf_merged['Normalised Biodiversity Areas'] = envperf_merged['Biodiversity Areas']/envperf_merged['Revenue']
    
    envperf_prev10 = envperf_merged

#     mask8 = envperf_merged['Company'].isin(company_list)
#     envperf_prev10 = envperf_merged[mask8]
    
    envperf_prev10['GHG1 Percentile Rank'] = (1-envperf_prev10['Normalised GHG1'].rank(pct=True)).fillna(0)
    envperf_prev10['GHG2 Percentile Rank'] = (1-envperf_prev10['Normalised GHG2'].rank(pct=True)).fillna(0)
    envperf_prev10['GHG3 Percentile Rank'] = (1-envperf_prev10['Normalised GHG3'].rank(pct=True)).fillna(0)
    envperf_prev10['Water Consumption Percentile Rank'] = (1-envperf_prev10['Normalised Water Consumption'].rank(pct=True)).fillna(0)
    envperf_prev10['Water Withdrawal Percentile Rank'] = (1-envperf_prev10['Normalised Water Withdrawal'].rank(pct=True)).fillna(0)
    envperf_prev10['Biodiversity Areas Percentile Rank'] = (envperf_prev10['Normalised Biodiversity Areas'].rank(pct=True)).fillna(0)
    
    envperf_prev10['envperfscore'] = envperf_prev10[['GHG1 Percentile Rank','GHG2 Percentile Rank','GHG3 Percentile Rank','Water Consumption Percentile Rank','Water Withdrawal Percentile Rank','Biodiversity Areas Percentile Rank']].mean(axis=1)
    envperf_prev10 = envperf_prev10.sort_values(by='envperfscore', axis=0, ascending=False)
    perfscore = envperf_prev10[['Company','envperfscore']]
    
    #print(envperf_prev10.iloc[0,:])
    
    #joining the two dataframes emg22 and egoal22 on the column 'Company'
    
    emg22 = emg22.rename(columns={'index':'Environmental Governance Index'})
    egoal22 = egoal22.rename(columns={'index':'Environmental Goals Index'})
    
    perfscore = perfscore.set_index('Company')
    emg22 = emg22.set_index('Company')
    egoal22 = egoal22.set_index('Company')
    emg22 = emg22.join(egoal22, on='Company')
    emg22 = emg22.join(perfscore, on='Company')

    #Assigning weights to the two indexes
#     goals_weight = 0.4
#     governance_weight = 0.6

    #Calculating the overall index using the weights
    weight_sum = governance_weight + goals_weight + performance_weight
    
    emg22['Overall index'] = emg22['Environmental Governance Index']*(governance_weight/weight_sum) + emg22['Environmental Goals Index']*(goals_weight/weight_sum) + emg22['envperfscore']*(performance_weight/weight_sum)
    emg22 = emg22.sort_values(by='Overall index',ascending=True)
    
# #     fontsize = 550/emg22.shape[0]
# #     if (550/emg22.shape[0] > 20):
# #         fontsize = 20
#     fontsize = 20
    
    fig3 = go.Figure(data=go.Heatmap(
#                         z=[emg22['Overall index']],
#                         x=emg22.index,
#                         y=['Overall Index'],
        z=[[value] for value in emg22['Overall index']],
        x=['Overall Index'],
        y=emg22.index,
        
                        colorscale='rdylgn'))
    fig3.update_layout(plot_bgcolor="white", font_family='Helvetica', title_font_family="Helvetica", xaxis_nticks=len(company_list))
    fig3.update_layout(
        title=go.layout.Title(
            text="Climate Strategy Index Based Ranking",
            #xref="paper",
            x=0.5
        ))
    fig3.update_xaxes(title=None,showticklabels=False)
    fig3.update_yaxes(title=None)
    #fig3.update_zaxes(title=None)
    fig3.update_layout(height=30*len(emg22), font=dict(size=20),font_family='Helvetica', title_font_family="Helvetica")
    fig3.update_layout(
    margin=dict(
        l=200,  # left margin
        r=50,  # right margin
        t=50,  # top margin
        b=50  # bottom margin to give more space to x-axis labels
    )
    )
    return fig3
    


navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src='/assets/UCLAAndersonSOM_Wht_PMScoated.png', height="30px"))
                    ],
                    align="center",
                    className="g-0",
                ),
                href="https://www.anderson.ucla.edu/",
                target="_blank",
                style={"textDecoration": "none"},
            ),
            dbc.Row(
                    [dbc.Col(dbc.NavbarBrand("Corporate Sustainability Case Study", className="ms-2")),
                     dbc.Col(width=1)
                    ],
                    align="center",
                    className="g-0",
                ),
            html.A(dbc.Row(
                    [
                        dbc.Col(html.Img(src='/assets/2022IMPACT New Center Logo2.png', height="40px"))
                    ],
                    align="center",
                    className="g-0",
                ),
                   href="https://www.anderson.ucla.edu/about/centers/impactanderson",
                   target="_blank",
                   style={"textDecoration": "none"},
                  )
        ],fluid=True
    ),
    color="#313339",
    dark=True,
)

intro = html.Div([
    html.Br(),
    html.H5("This page provides a comparitive sector-based analysis based on the following metrics:")])

list_group1 = html.Div(
    [
        dbc.ListGroup(
            [
                html.A(dbc.ListGroupItem("Disclosure Status for Environmental Metrics", color="secondary", action=True), href="#dsfem", style={'text-decoration':'none','font-style': 'italic'}),
                html.A(dbc.ListGroupItem("GHG Scope 1 Emissions", color="secondary", action=True), href="#gs1e", style={'text-decoration':'none','font-style': 'italic'}),
                html.A(dbc.ListGroupItem("GHG Scope 2 Emissions", color="secondary", action=True), href="#gs2e", style={'text-decoration':'none','font-style': 'italic'}),
                html.A(dbc.ListGroupItem("GHG Scope 3 Emissions", color="secondary", action=True), href="#gs3e", style={'text-decoration':'none','font-style': 'italic'}),
                html.A(dbc.ListGroupItem("Water Utilization", color="secondary", action=True), href="#wut", style={'text-decoration':'none','font-style': 'italic'}),
                html.A(dbc.ListGroupItem("Biodiversity Areas", color="secondary", action=True), href="#bare", style={'text-decoration':'none','font-style': 'italic'})
            ],
            horizontal=True,
            className="mb-2",
        )
        
    ]
)

list_group2 = html.Div(
    [
        dbc.ListGroup(
            [
                html.A(dbc.ListGroupItem("Governance Metrics", color="secondary", action=True), href="#gm", style={'text-decoration':'none','font-style': 'italic'}),
                html.A(dbc.ListGroupItem("TCFD Disclosure Percentage", color="secondary", action=True), href="#tdp", style={'text-decoration':'none','font-style': 'italic'}),
                html.A(dbc.ListGroupItem("Board Environmental Competency", color="secondary", action=True), href="#bec", style={'text-decoration':'none','font-style': 'italic'}),
                html.A(dbc.ListGroupItem("Environmental Goals", color="secondary", action=True), href="#egs", style={'text-decoration':'none','font-style': 'italic'}),
                html.A(dbc.ListGroupItem("Net Zero Targets", color="secondary", action=True), href="#ntz", style={'text-decoration':'none','font-style': 'italic'})
            ],
            horizontal="lg",
        ),
        html.Br()
    ]
)

card11=dbc.Card([
    dbc.CardHeader("Sector and Company Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Select Sector", style={ 'display': 'flex'}, id='ss1')],width=12),
                dbc.Tooltip("Use the arrow to select your sector of interest or start typing to see matching options. Only one sector can be selected at a time.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="ss1")
                
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in sorted(set(df['GICS.Sector'].tolist())) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Choose Companies", style={ 'display': 'flex'}, id='cc1'),
                dbc.Tooltip("The top 10 companies (based on revenue) in the chosen sector is auto-populated. Use the arrow to select your companies of interest or start typing to see matching options. Only companies in the selected sector will be shown. Multiple companies can be selected.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="cc1")
                    #html.P(" Add/remove companies using the dropdown",style={ 'display': 'flex',  'justify-content':'center'})
                ],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select')
                ,width=12)
            ])
        ])
    
],className="m-1")

card12=dbc.Card([
    dbc.CardHeader("Disclosure Status for Environmental Metrics",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}, id='dsfem'),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="trafficlight"))])
                ])
    
],className="m-1")

card21=dbc.Card([
    dbc.CardHeader("Sector and Company Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Select Sector",style={ 'display': 'flex'}, id='ss2')],width=12),
                dbc.Tooltip("Use the arrow to select your sector of interest or start typing to see matching options. Only one sector can be selected at a time.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="ss2")
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in sorted(set(df['GICS.Sector'].tolist())) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select2')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                   html.P("Choose Companies", style={ 'display': 'flex'}, id='cc2'),
                    dbc.Tooltip("The top 10 companies (based on revenue) in the chosen sector is auto-populated. Use the arrow to select your companies of interest or start typing to see matching options. Only companies in the selected sector will be shown. Multiple companies can be selected.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="cc2")
                    ],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select2')
                ,width=12)
            ])
        ])
    
],className="m-1")

card22=dbc.Card([
    dbc.CardHeader("GHG Scope 1 Emissions",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}, id='gs1e'),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="tghg1"))]),
            dbc.Row([dbc.Col(dcc.Graph(id="nghg1"))])
                ])
    
],className="m-1")

card31=dbc.Card([
    dbc.CardHeader("Sector and Company Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Select Sector",style={'display': 'flex'}, id='ss3')],width=12),
                dbc.Tooltip("Use the arrow to select your sector of interest or start typing to see matching options. Only one sector can be selected at a time.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="ss3")
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in sorted(set(df['GICS.Sector'].tolist())) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select3')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Choose Companies", style={ 'display': 'flex'}, id='cc3'),
                dbc.Tooltip("The top 10 companies (based on revenue) in the chosen sector is auto-populated. Use the arrow to select your companies of interest or start typing to see matching options. Only companies in the selected sector will be shown. Multiple companies can be selected.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="cc3")
                    ],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select3')
                ,width=12)
            ])
        ])
    
],className="m-1")

card32=dbc.Card([
    dbc.CardHeader("GHG Scope 2 Emissions",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}, id='gs2e'),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="tghg2"))]),
            dbc.Row([dbc.Col(dcc.Graph(id="nghg2"))])
                ])
    
],className="m-1")


card41=dbc.Card([
    dbc.CardHeader("Sector and Company Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Select Sector",style={'display': 'flex'}, id='ss4')],width=12),
                dbc.Tooltip("Use the arrow to select your sector of interest or start typing to see matching options. Only one sector can be selected at a time.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="ss4")
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in sorted(set(df['GICS.Sector'].tolist())) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select4')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Choose Companies", style={ 'display': 'flex'}, id='cc4'),
                dbc.Tooltip("The top 10 companies (based on revenue) in the chosen sector is auto-populated. Use the arrow to select your companies of interest or start typing to see matching options. Only companies in the selected sector will be shown. Multiple companies can be selected.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="cc4")
                    ],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select4')
                ,width=12)
            ])
        ])
    
],className="m-1")

card42=dbc.Card([
    dbc.CardHeader("GHG Scope 3 Emissions",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}, id='gs3e'),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="tghg3"))]),
            dbc.Row([dbc.Col(dcc.Graph(id="nghg3"))])
                ])
    
],className="m-1")

card51=dbc.Card([
    dbc.CardHeader("Sector and Company Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Select sector",style={ 'display': 'flex'}, id='ss5')],width=12),
                dbc.Tooltip("Use the arrow to select your sector of interest or start typing to see matching options. Only one sector can be selected at a time.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="ss5")
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in sorted(set(df['GICS.Sector'].tolist())) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select5')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Choose Companies", style={ 'display': 'flex'}, id='cc5'),
                dbc.Tooltip("The top 10 companies (based on revenue) in the chosen sector is auto-populated. Use the arrow to select your companies of interest or start typing to see matching options. Only companies in the selected sector will be shown. Multiple companies can be selected.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="cc5")
                    ],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select5')
                ,width=12)
            ])
        ])
    
],className="m-1")

card52=dbc.Card([
    dbc.CardHeader("Water Utilization",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}, id='wut'),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="wu"))])
                ])
    
],className="m-1")

card61=dbc.Card([
    dbc.CardHeader("Sector and Company Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Select Sector",style={ 'display': 'flex'}, id='ss6')],width=12),
                dbc.Tooltip("Use the arrow to select your sector of interest or start typing to see matching options. Only one sector can be selected at a time.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="ss6")
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in sorted(set(df['GICS.Sector'].tolist())) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select6')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Choose Companies", style={ 'display': 'flex'}, id='cc6'),
                dbc.Tooltip("The top 10 companies (based on revenue) in the chosen sector is auto-populated. Use the arrow to select your companies of interest or start typing to see matching options. Only companies in the selected sector will be shown. Multiple companies can be selected.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="cc6")
                    ],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select6')
                ,width=12)
            ])
        ])
    
],className="m-1")

card62=dbc.Card([
    dbc.CardHeader("Biodiversity Areas",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}, id='bare'),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="biod"))])
                ])
    
],className="m-1")

card71=dbc.Card([
    dbc.CardHeader("Sector and Company Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Select Sector",style={ 'display': 'flex'}, id='ss7')],width=12),
                dbc.Tooltip("Use the arrow to select your sector of interest or start typing to see matching options. Only one sector can be selected at a time.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="ss7")
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in sorted(set(df['GICS.Sector'].tolist())) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select7')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Choose Companies", style={ 'display': 'flex'}, id='cc7'),
                dbc.Tooltip("The top 10 companies (based on revenue) in the chosen sector is auto-populated. Use the arrow to select your companies of interest or start typing to see matching options. Only companies in the selected sector will be shown. Multiple companies can be selected.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="cc7")
                    ],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select7')
                ,width=12)
            ])
        ])
    
],className="m-1")

card72=dbc.Card([
    dbc.CardHeader("Governance Metrics",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}, id="gm"),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="envmetgov"))])
                ])
    
],className="m-1")

card81=dbc.Card([
    dbc.CardHeader("Sector and Company Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Select Sector",style={ 'display': 'flex'}, id='ss8')],width=12),
                dbc.Tooltip("Use the arrow to select your sector of interest or start typing to see matching options. Only one sector can be selected at a time.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="ss8")
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in sorted(set(df['GICS.Sector'].tolist())) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select8')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Choose Companies", style={ 'display': 'flex'}, id='cc8'),
                dbc.Tooltip("The top 10 companies (based on revenue) in the chosen sector is auto-populated. Use the arrow to select your companies of interest or start typing to see matching options. Only companies in the selected sector will be shown. Multiple companies can be selected.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="cc8")
                    ],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select8')
                ,width=12)
            ])
        ])
    
],className="m-1")

card82=dbc.Card([
    dbc.CardHeader("TCFD Disclosure Percentage",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}, id='tdp'),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="tcfdper"))])
                ])
    
],className="m-1")


card91=dbc.Card([
    dbc.CardHeader("Sector and Company Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Select Sector",style={ 'display': 'flex'}, id='ss9')],width=12),
                dbc.Tooltip("Use the arrow to select your sector of interest or start typing to see matching options. Only one sector can be selected at a time.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="ss9")
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in sorted(set(df['GICS.Sector'].tolist())) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select9')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Choose Companies", style={ 'display': 'flex'}, id='cc9'),
                dbc.Tooltip("The top 10 companies (based on revenue) in the chosen sector is auto-populated. Use the arrow to select your companies of interest or start typing to see matching options. Only companies in the selected sector will be shown. Multiple companies can be selected.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="cc9")
                    ],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select9')
                ,width=12)
            ])
        ])
    
],className="m-1")

card92=dbc.Card([
    dbc.CardHeader("Board Environmental Competency",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}, id='bec'),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="boardmem"))])
                ])
    
],className="m-1")


card101=dbc.Card([
    dbc.CardHeader("Sector and Company Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Select Sector",style={ 'display': 'flex'}, id='ss10')],width=12),
                dbc.Tooltip("Use the arrow to select your sector of interest or start typing to see matching options. Only one sector can be selected at a time.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="ss10")
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in sorted(set(df['GICS.Sector'].tolist())) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select10')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Choose Companies", style={ 'display': 'flex'}, id='cc10'),
                dbc.Tooltip("The top 10 companies (based on revenue) in the chosen sector is auto-populated. Use the arrow to select your companies of interest or start typing to see matching options. Only companies in the selected sector will be shown. Multiple companies can be selected.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="cc10")
                    ],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select10')
                ,width=12)
            ])
        ])
    
],className="m-1")

card102=dbc.Card([
    dbc.CardHeader("Environmental Goals",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}, id='egs'),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="envigoals"))])
                ])
    
],className="m-1")


card111=dbc.Card([
    dbc.CardHeader("Sector and Company Selection",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Select Sector",style={ 'display': 'flex'}, id='ss11')],width=12),
                dbc.Tooltip("Use the arrow to select your sector of interest or start typing to see matching options. Only one sector can be selected at a time.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="ss11")
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in sorted(set(df['GICS.Sector'].tolist())) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select11')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Choose Companies", style={ 'display': 'flex'}, id='cc11'),
                dbc.Tooltip("The top 10 companies (based on revenue) in the chosen sector is auto-populated. Use the arrow to select your companies of interest or start typing to see matching options. Only companies in the selected sector will be shown. Multiple companies can be selected.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="cc11")
                    ],width=12)
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(multi=True,
                    id='company_select11')
                ,width=12)
            ])
        ])
    
],className="m-1")

card112=dbc.Card([
    dbc.CardHeader("Net Zero Targets",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}, id="ntz"),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(id="nztar"))])
                ])
    
],className="m-1")

tab2card0=dbc.Card([
    dbc.CardHeader("Climate Strategy Index",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([html.B("Climate Strategy Index is a sector-wise scoring methodology constructed to rank firms based on their environmental performance, governace and goals and relative weights assigned to each of these categories."),
                     html.B("Better overall strategy is associated with a higher index.")],style={"text-align":"center"}),
            html.Br(),
#             dbc.Row([
#                 dbc.Col([],width=5),
#                 dbc.Col([
#                     dbc.Button(
#                         "Download Logic Documentation",
#                         #href="/assets/Index Calculation.pdf",
#                         #download="Index Calculation.pdf",
#                         outline=True,
#                         style={"background-color": "#FDB71A"},
#                         #html.Button("Download Image", id="btn_image"),
#                         id="dnld_file"
#                         #color="Light"
#                         #size="sm",
#                         #className="mx-auto"
#                     ),
#                     dcc.Download(id="download_file")
#                 ],width=2),
#                 dbc.Col([],width=5),
                
#             ], className="d-flex justify-content-center"),
#             dbc.Button(
#                 "Download Logic Documentation",
#                 href="/assets/Index Calculation.pdf",
#                 download="Index Calculation.pdf",
#                 #external_link=True,
#                 style={"color":"C3D7EE","text-align":"center"},
#             ),
            dbc.Row([html.P("The Weights panel can be used to select the sector and appropriate weightage of each category"),
                     html.P("The Ranking panel provides the firm rankings for the selected sector based on the climate strategy index calculated as the weighted mean of environmental performance, governace and goal metrics of the respective firms"),
                     html.P("The Score Breakdown panel lists the features used to calculate each category's index based on an example firm. The example firm can also be added to the sector-level ranking list for comparison")
                ],style={"text-align":"center"})
        ])
    
],className="m-1")

tab2card1=dbc.Card([
    dbc.CardHeader("Weights",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    html.P("Select Sector",style={ 'display': 'flex',  'justify-content':'center'}, id='ss12')],width=12),
                dbc.Tooltip("Use the arrow to select your sector of interest or start typing to see matching options. Only one sector can be selected at a time.",
                            style={"textDecoration": "underline", "cursor": "pointer"},target="ss12")
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(options = [{'label': x, 'value': x} for x in sorted(set(df['GICS.Sector'].tolist())) if x is not None and not pd.isnull(x)],
                    value='Consumer Staples',
                    id='sector_select12')
                ,width=12)
            ]),
            html.Br(),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Performance",style={'text-align':'center'}),
                    dcc.Slider(min=0, max=100, step=10, value=40, id='performance_slider')])
                ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Governance",style={'text-align':'center'}),
                    dcc.Slider(min=0, max=100, step=10, value=30, id='governance_slider')])
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.P("Goals",style={'text-align':'center'}),
                    dcc.Slider(min=0, max=100, step=10, value=30, id='goal_slider')])
                ])
        ])
    
],className="m-1")

tab2card2=dbc.Card([
    dbc.CardHeader("Ranking",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(dcc.Graph(
                id="overall_index"
            ))]),
            dbc.Row([
                dbc.Checklist(
                        options=[
                            {"label": "Add additional firm to ranked list", "value": 0}],
                        id="newfirm_toggle",
                        switch=True,
                        #className="form-check-input"
                        )
            ])
        ])
    
],className="m-1")

tab2card3=dbc.Card([
    dbc.CardHeader("Score Breakdown",style={'background-color': '#C3D7EE', 'text-align': 'center','font-weight': 'bold','font-style': 'italic'}),
    dbc.CardBody(
        [
            dbc.Form([
                dbc.Row(
                    [
                        dbc.Label("For a firm", width="auto"),
                        dbc.Col(
                            dbc.Input(type="text", placeholder="Enter firm name", value="ABC Foods Inc", id="firmname_input"),
                            className="me-3",
                        ),
                        dbc.Label("in", width="auto"),
                        dbc.Label(id='firmsector_input', width="auto"),
                        dbc.Label("sector having annual Revenue", width="auto"),
                        dbc.Col(
                            dbc.InputGroup(
                                [
                                    #dbc.InputGroupText("Annual revenue:"),
                                    dbc.InputGroupText("$"),
                                    dbc.Input(value=7986.252, type="number",id="firmrev_input"),
                                    dbc.InputGroupText("M")
                                ],
                                #className="mb-3",
                            ),
                            className="me-3",
                        ),
                        #dbc.Col(dbc.Button("Submit", color="primary"), width="auto"),
                        
                    ],
                    className="g-2",
                ),
                
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H5(["Environmental Performance Index is the average sector-based percentile ranking of the following Metrics normalised by revenue"])],width=9),
                    dbc.Col([dbc.Button("What is Percentile Ranking?", id="per_rank_exp", n_clicks=0, outline=True, color="secondary", className="me-1")],width=3),
                    #html.H5([""]),
                            #html.Span("percentile ranking", id="percentile_tooltip"),
                            
#                      dbc.Tooltip(
#                          "Percentile ranking indicates the relative position of a score within a distribution, showing the percentage of scores that fall below it.",
#                          style={"textDecoration": "underline", "cursor": "pointer"},
#                          target="percentile_tooltip",
#                      ),
#                     dbc.Button("Open Offcanvas", id="open-offcanvas", n_clicks=0),
                    dbc.Offcanvas(
                        html.P(
                            "Percentile ranking indicates the relative position of a score within a distribution, showing the percentage of scores that fall below it."
                        ),
                        id="per_rank_exp_off",
                        title="Percentile Rank",
                        is_open=False,
                    ),
                ]),
                dbc.Row(
                    [
                        dbc.Col([
                            dbc.Label("Scope 1 Emission", width="auto",style={'font-style': 'italic'}),
                            html.I(className="bi bi-info-circle-fill me-2"),
                            dbc.Input(type="number", value=179.211, id="ghg1_input"),
                            dbc.InputGroupText("thousand metric tons")],
                            className="me-3",
                        ),
                        dbc.Col([
                            dbc.Label("Scope 2 Emission (market-based)", width="auto",style={'font-style': 'italic'}),
                            dbc.Input(type="number", value=68.639, id="ghg2_input"),
                            dbc.InputGroupText("thousand metric tons")],
                            className="me-3",
                        ),
                        dbc.Col([
                            dbc.Label("Scope 3 Emission", width="auto",style={'font-style': 'italic'}),
                            dbc.Input(type="number", value=5941.676, id="ghg3_input"),
                            dbc.InputGroupText("thousand metric tons")],
                            className="me-3",
                        ),
                    ],
                    className="g-2",
                ),
                dbc.Row(
                    [
                        dbc.Col([
                            dbc.Label("Water consumption", width="auto",style={'font-style': 'italic'}),
                            dbc.Input(type="number", value=872.90, id="wc_input"),
                            dbc.InputGroupText("mega litres")],
                            className="me-3",
                        ),
                        dbc.Col([
                            dbc.Label("Water withdrawal", width="auto",style={'font-style': 'italic'}),
                            dbc.Input(type="number", value=5416.50, id="ww_input"),
                            dbc.InputGroupText("mega litres")],
                            className="me-3",
                        ),
                        dbc.Col([
                            dbc.Label("Biodiversity", width="auto",id='biod_tooltip',style={'font-style': 'italic'}),
                            dbc.Tooltip("Biodiversity indicates the total area of sites owned, leased, or managed in or adjacent to protected areas or key biodiversity areas ",
                         style={"textDecoration": "underline", "cursor": "pointer"},
                         target="biod_tooltip",
                                       ),
                            dbc.Input(type="number", value=119537, id="biod_input"),
                            dbc.InputGroupText("hectares")],
                            className="me-3",
                        )
                    ],
                    className="g-2",
                ),
                dbc.Row([
                    dbc.Label("Performance Index based on above values and in comparison to firms listed alongside:", width="auto"),
                    dbc.Label(id='perf_index_disp', width="auto",style={'font-weight': 'bold'}),
                        
                ]),
                
                html.Br(),
                html.Br(),
                dbc.Row([
                    html.H5("Environmental Governace Index is the encoded average of the following Metrics")
                ]),
                dbc.Row(
                    [
                        dbc.Col([
                            dbc.Label("GHG Assurance", width="auto",style={'font-style': 'italic'}),
                            dcc.Dropdown(
                                options=[
                                    {'label': 'Yes', 'value': 1},{'label': 'No', 'value': 0},
                                    {'label': 'Partial', 'value': 0.5}], 
                                value=0,
                                id='ghga_input')],
                            className="me-3",
                        ),
                        dbc.Col([
                            dbc.Label("TCFD Disclosure", width="auto",style={'font-style': 'italic'}),
                            dcc.Dropdown(
                                options=[
                                    {'label': 'Yes', 'value': 1},{'label': 'No', 'value': 0},
                                    {'label': 'Partial', 'value': 0.5}], 
                                value=0.5,
                                id='tcfd_input')],
                            className="me-3",
                        ),
                        dbc.Col([
                            dbc.Label("Environmental skill as a key board competency", width="auto",style={'font-style': 'italic'}),
                            dcc.Dropdown(
                                options=[
                                    {'label': 'Yes', 'value': 1},{'label': 'No', 'value': 0},
                                    {'label': 'Partial', 'value': 0.5}], 
                                value=1,
                                id='envskill_input')],
                            className="me-3",
                        ),
                        dbc.Col([
                            dbc.Label("Executive compensation tied to ESG milestone", width="auto",style={'font-style': 'italic'}),
                            dcc.Dropdown(
                                options=[
                                    {'label': 'Yes', 'value': 1},{'label': 'No', 'value': 0},
                                    {'label': 'Partial', 'value': 0.5}], 
                                value=1,
                                id='envcomp_input')],
                            className="me-3",
                        )
                    ],
                    #style={'background-color': 'aquamarine'}
                    className="g-2",
                ),
                dbc.Row([
                    dbc.Label("Encoding: Yes=1 ; Partial=0.5 ; No:0", width="auto")
                        
                ]),
                dbc.Row([
                    dbc.Label("Governace Index based on above values:", width="auto"),
                    dbc.Label(id='gov_index_disp', width="auto",style={'font-weight': 'bold'}),
                        
                ]),
                
                html.Br(),
                html.Br(),
                dbc.Row([
                    html.H5("Environmental Goals Index is the encoded average of the following Metrics")
                ]),
                dbc.Row(
                    [
                        dbc.Col([
                            dbc.Label("Has a Net Zero Goal", width="auto",style={'font-style': 'italic'}),
                            dcc.Dropdown(
                                options=[
                                    {'label': 'Yes', 'value': 1},{'label': 'No', 'value': 0}], 
                                value=0,
                                id='nzg_input')],
                            className="me-3",
                        ),
                        dbc.Col([
                            dbc.Label("Net Zero goal covers scope 1 emissions", width="auto",style={'font-style': 'italic'}),
                            dcc.Dropdown(
                                options=[
                                    {'label': 'Yes', 'value': 1},{'label': 'No', 'value': 0},
                                    {'label': 'NA', 'value': 0}], 
                                value=0,
                                id='nzs1_input')],
                            className="me-3",
                        ),
                        dbc.Col([
                            dbc.Label("Net Zero goal covers scope 2 emissions", width="auto",style={'font-style': 'italic'}),
                            dcc.Dropdown(
                                options=[
                                    {'label': 'Yes', 'value': 1},{'label': 'No', 'value': 0},
                                    {'label': 'NA', 'value': 0}], 
                                value=0,
                                id='nzs2_input')],
                            className="me-3",
                        ),
                        dbc.Col([
                            dbc.Label("Net Zero goal covers all of scope 3 emissions", width="auto",style={'font-style': 'italic'}),
                            dcc.Dropdown(
                                options=[
                                    {'label': 'Yes', 'value': 1},{'label': 'No', 'value': 0},
                                    {'label': 'NA', 'value': 0}], 
                                value=0,
                                id='nzs3_input')],
                            className="me-3",
                        )
                    ],
                    className="g-2",
                ),
                dbc.Row(
                    [
                        dbc.Col([
                            dbc.Label("Has an interim Goal on the way to Net Zero", width="auto",style={'font-style': 'italic'}),
                            dcc.Dropdown(
                                options=[
                                    {'label': 'Yes', 'value': 1},{'label': 'No', 'value': 0},
                                    {'label': 'NA', 'value': 0}], 
                                value=0,
                                id='ntig_input')],
                            className="me-3",
                        ),
                        dbc.Col([
                            dbc.Label("Working with SBTI", width="auto",style={'font-style': 'italic'}),
                            dcc.Dropdown(
                                options=[
                                    {'label': 'Yes', 'value': 1},{'label': 'No', 'value': 0},
                                    {'label': 'NA', 'value': 0}], 
                                value=0,
                                id='sbti_input')],
                            className="me-3",
                        ),
                        dbc.Col([
                            dbc.Label("Status of goal with SBTI", width="auto",style={'font-style': 'italic'}),
                            dcc.Dropdown(
                                options=[
                                    {'label': 'Comitted', 'value': 1},{'label': 'Validated', 'value': 0.5},
                                    {'label': 'NA', 'value': 0}], 
                                value=0,
                                id='sbti_stat_input')],
                            className="me-3",
                        ),
                        dbc.Col([
                            dbc.Label("'Net Zero'/'Carbon neutral' mentioned in Proxy Statement", width="auto",style={'font-style': 'italic'}),
                            dcc.Dropdown(
                                options=[
                                    {'label': 'Yes', 'value': 1},{'label': 'No', 'value': 0},
                                    {'label': 'NA', 'value': 0}], 
                                value=0,
                                id='ntcnps_input')],
                            className="me-3",
                        ),
                    ],
                    className="g-2",
                ),
                dbc.Row([
                    dbc.Label("Encoding: Yes=1 ; Committed=1 ; Validated=0.5 ; No:0 ; NA:0 ", width="auto")
                        
                ]),
                dbc.Row([
                    dbc.Label("Goals Index based on above values:", width="auto"),
                    dbc.Label(id='goal_index_disp', width="auto",style={'font-weight': 'bold'}),
                        
                ]),
                dbc.Row([
                    dbc.Label("Climate Strategy Index is the average of the above 3 indices:", width="auto"),
                    dbc.Label(id='overall_index_disp', width="auto",style={'font-weight': 'bold'}),
                        
                ]),
                
                
            ]),
            
        ])
    
],className="m-1")


tab2card4=[dbc.Button(
                        "For more information regarding index calculation, click here",
                        outline=True,
                        style={"background-color": "#FDB71A"},
                        id="dnld_file"
                    ),dcc.Download(id="download_file")]


tab1 = html.Div([
    dbc.Row([dbc.Col([intro],width="auto")],className="m-1", justify="center"),
    dbc.Row([dbc.Col([list_group1],width="auto")],className="m-1", justify="center"),
    dbc.Row([dbc.Col([list_group2],width="auto")],className="m-1", justify="center"),
    dbc.Row([dbc.Col([card11],width=3),dbc.Col([card12],width=9)],className="m-1"),
    dbc.Row([dbc.Col([card21],width=3),dbc.Col([card22],width=9)],className="m-1"),
    dbc.Row([dbc.Col([card31],width=3),dbc.Col([card32],width=9)],className="m-1"),
    dbc.Row([dbc.Col([card41],width=3),dbc.Col([card42],width=9)],className="m-1"),
    dbc.Row([dbc.Col([card51],width=3),dbc.Col([card52],width=9)],className="m-1"),
    dbc.Row([dbc.Col([card61],width=3),dbc.Col([card62],width=9)],className="m-1"),
    dbc.Row([dbc.Col([card71],width=3),dbc.Col([card72],width=9)],className="m-1"),
    dbc.Row([dbc.Col([card81],width=3),dbc.Col([card82],width=9)],className="m-1"),
    dbc.Row([dbc.Col([card91],width=3),dbc.Col([card92],width=9)],className="m-1"),
    dbc.Row([dbc.Col([card101],width=3),dbc.Col([card102],width=9)],className="m-1"),
    dbc.Row([dbc.Col([card111],width=3),dbc.Col([card112],width=9)],className="m-1")
])

tab2 = html.Div([dbc.Row([tab2card0],className="m-1"),
                 dbc.Row([dbc.Col([dbc.Row(tab2card1,className="m-1"),dbc.Row(tab2card3,className="m-1")],width=6,),
                          dbc.Col([dbc.Row(tab2card2,className="m-1"),dbc.Row(tab2card4,className="m-1")],width=6)])
                 #dbc.Row([dbc.Col([tab2card2],width=12)],className="mb-4 ml-3"),
                 #dbc.Row([dbc.Col([tab2card3],width=6)],className="mb-4 ml-3")
                ])



app.layout = html.Div([
    dbc.Row([dbc.Col(navbar)],className="mb-4"),
    dcc.Tabs(id="tabs-styled-with-props", value='tab-1', 
             children=[
        dcc.Tab(label='Environmental Disclosure and Performance Metrics', value='tab-1'),
        dcc.Tab(label='Climate Strategy Index', value='tab-2'),
    ], 
             colors={
        "border": "white",
        "primary": "#FDE900",
        "background": "#FDE900"
    }),
    html.Div(id='tabs-content-props')
])

@callback(Output('tabs-content-props', 'children'),
              Input('tabs-styled-with-props', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return tab1
    elif tab == 'tab-2':
        return tab2


@callback(
    [Output('company_select', 'options'),
     Output('company_select', 'value')],
    [Input('sector_select', 'value')]
)
def update_companylist(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('trafficlight', 'figure'),
    [State('sector_select', 'value')],
    [Input('company_select', 'value')]
)
def update_statew(sector,company_list):
    fig=trafficlight(sector,company_list)
    return fig

@callback(
    [Output('company_select2', 'options'),
     Output('company_select2', 'value')],
    [Input('sector_select2', 'value')]
)
def update_companylist2(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    [Output('tghg1', 'figure'),
     Output('nghg1', 'figure')],
    [State('sector_select2', 'value')],
    [Input('company_select2', 'value')]
)
def update_tghg1(sector,company_list):
    fig=tghg1(sector,company_list)
    fig2=nghg1(sector,company_list)
    return fig, fig2

@callback(
    [Output('company_select3', 'options'),
     Output('company_select3', 'value')],
    [Input('sector_select3', 'value')]
)
def update_companylist3(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    [Output('tghg2', 'figure'),
     Output('nghg2', 'figure')],
    [State('sector_select3', 'value')],
    [Input('company_select3', 'value')]
)
def update_tghg2(sector,company_list):
    fig32=tghg2(sector,company_list)
    fig322=nghg2(sector,company_list)
    return fig32, fig322

@callback(
    [Output('company_select4', 'options'),
     Output('company_select4', 'value')],
    [Input('sector_select4', 'value')]
)
def update_companylist4(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    [Output('tghg3', 'figure'),
     Output('nghg3', 'figure')],
    [State('sector_select4', 'value')],
    [Input('company_select4', 'value')]
)
def update_tghg3(sector,company_list):
    fignorm=tnghg3(sector,company_list,"Normalised GHG3",1)
    figtotal=tnghg3(sector,company_list,"Total GHG3",2)
    return figtotal, fignorm 

@callback(
    [Output('company_select5', 'options'),
     Output('company_select5', 'value')],
    [Input('sector_select5', 'value')]
)
def update_companylist5(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('wu', 'figure'),
    [State('sector_select5', 'value')],
    [Input('company_select5', 'value')]
)
def update_wu(sector,company_list):
    figu=water_util(sector,company_list)
    return figu

@callback(
    [Output('company_select6', 'options'),
     Output('company_select6', 'value')],
    [Input('sector_select6', 'value')]
)
def update_companylist6(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('biod', 'figure'),
    [State('sector_select6', 'value')],
    [Input('company_select6', 'value')]
)
def update_biod(sector,company_list):
    figb=biodiver(sector,company_list)
    return figb


@callback(
    [Output('company_select7', 'options'),
     Output('company_select7', 'value')],
    [Input('sector_select7', 'value')]
)
def update_companylist7(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('envmetgov', 'figure'),
    [State('sector_select7', 'value')],
    [Input('company_select7', 'value')]
)
def update_envmetgov(sector,company_list):
    figgvnmet=enviromentalgovernacemetrics(sector,company_list)[0]
    return figgvnmet

@callback(
    [Output('company_select8', 'options'),
     Output('company_select8', 'value')],
    [Input('sector_select8', 'value')]
)
def update_companylist8(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('tcfdper', 'figure'),
    [State('sector_select8', 'value')],
    [Input('company_select8', 'value')]
)
def update_tcfdper(sector,company_list):
    figtcfdper=tcfdpercentage(sector,company_list)
    return figtcfdper

@callback(
    [Output('company_select9', 'options'),
     Output('company_select9', 'value')],
    [Input('sector_select9', 'value')]
)
def update_companylist9(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('boardmem', 'figure'),
    [State('sector_select9', 'value')],
    [Input('company_select9', 'value')]
)
def update_boardmem(sector,company_list):
    figboardmem=boardmember(sector,company_list)
    return figboardmem

@callback(
    [Output('company_select10', 'options'),
     Output('company_select10', 'value')],
    [Input('sector_select10', 'value')]
)
def update_companylist10(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('envigoals', 'figure'),
    [State('sector_select10', 'value')],
    [Input('company_select10', 'value')]
)
def update_envigoals(sector,company_list):
    figenvigoals=environmentalgoals(sector,company_list)[0]
    return figenvigoals

@callback(
    [Output('company_select11', 'options'),
     Output('company_select11', 'value')],
    [Input('sector_select11', 'value')]
)
def update_companylist11(sector):
    companies, top_companies = company_list(sector)
    options = [{'label': x, 'value': x} for x in companies]
    value = top_companies
    return options,value

@callback(
    Output('nztar', 'figure'),
    [State('sector_select11', 'value')],
    [Input('company_select11', 'value')]
)
def update_nztar(sector,company_list):
    fignztar=netzerotarget(sector,company_list)
    return fignztar

@callback(
    [Output('overall_index', 'figure'),
     Output('firmsector_input','children')],
    [Input('sector_select12', 'value'),
     Input('governance_slider', 'value'),
     Input('goal_slider', 'value'),
     Input('performance_slider', 'value'),
     Input('newfirm_toggle', 'value')],
    [State('firmname_input', 'value'),
     State('firmrev_input', 'value'),
     State('ghg1_input', 'value'),
     State('ghg2_input', 'value'),
     State('ghg3_input', 'value'),
     State('wc_input', 'value'),
     State('ww_input', 'value'),
     State('biod_input', 'value'),
     State('ghga_input', 'value'),
     State('tcfd_input', 'value'),
     State('envskill_input', 'value'),
     State('envcomp_input', 'value'),
     State('nzg_input', 'value'),
     State('nzs1_input', 'value'),
     State('nzs2_input', 'value'),
     State('nzs3_input', 'value'),
     State('ntig_input', 'value'),
     State('sbti_input', 'value'),
     State('sbti_stat_input', 'value'),
     State('ntcnps_input', 'value')]
    
)
def update_overallindex(sector,governance_weight, goals_weight, performance_weight, toggle, name, rev, ghg1, ghg2, ghg3, wc, ww, biod, ghga, tcfd, envskill, envcomp, nzg, nzs1, nzs2, nzs3, ntig, sbti, sbti_stat, ntcnps):
    companies = company_list_from_sector(sector)
    name_bold = "<b>"+ name+ "</b>"
    if toggle:
        firm_ind = 1
    else:
        firm_ind = 0
    new_firm_perf = [name_bold,ghg1*1000,ghg2*1000,ghg3*1000,sector,rev,wc,ww,biod]
    new_firm_gov = [name_bold,ghga,tcfd,envskill,envcomp]
    new_firm_goal = [name_bold,nzg,nzs1,nzs2,nzs3,ntig,sbti,sbti_stat,ntcnps]
    
    figindex=overallindex(sector, companies, governance_weight, goals_weight, performance_weight, firm_ind, new_firm_perf, new_firm_gov, new_firm_goal)
    return figindex, sector


@callback(
    [Output('gov_index_disp', 'children'),
     Output('goal_index_disp', 'children'),
     Output('perf_index_disp', 'children'),
     Output('overall_index_disp', 'children')],
    [Input('sector_select12', 'value'),
     Input('governance_slider', 'value'),
     Input('goal_slider', 'value'),
     Input('performance_slider', 'value'),
     Input('firmname_input', 'value'),
     Input('firmrev_input', 'value'),
     Input('ghg1_input', 'value'),
     Input('ghg2_input', 'value'),
     Input('ghg3_input', 'value'),
     Input('wc_input', 'value'),
     Input('ww_input', 'value'),
     Input('biod_input', 'value'),
     Input('ghga_input', 'value'),
     Input('tcfd_input', 'value'),
     Input('envskill_input', 'value'),
     Input('envcomp_input', 'value'),
     Input('nzg_input', 'value'),
     Input('nzs1_input', 'value'),
     Input('nzs2_input', 'value'),
     Input('nzs3_input', 'value'),
     Input('ntig_input', 'value'),
     Input('sbti_input', 'value'),
     Input('sbti_stat_input', 'value'),
     Input('ntcnps_input', 'value')]
    
)
def update_indexplaceholders(sector,governance_weight, goals_weight, performance_weight, name, rev, ghg1, ghg2, ghg3, wc, ww, biod, ghga, tcfd, envskill, envcomp, nzg, nzs1, nzs2, nzs3, ntig, sbti, sbti_stat, ntcnps):
    companies = company_list_from_sector(sector)
    name_bold = "<b>"+ name+ "</b>"
#     if toggle:
#         firm_ind = 1
#     else:
#         firm_ind = 0
    new_firm_perf = [name_bold,ghg1*1000,ghg2*1000,ghg3*1000,sector,rev,wc,ww,biod]
    new_firm_gov = [name_bold,ghga,tcfd,envskill,envcomp]
    new_firm_goal = [name_bold,nzg,nzs1,nzs2,nzs3,ntig,sbti,sbti_stat,ntcnps]
    
    gov, goal, perf, overall = index_calculator(sector, companies, governance_weight, goals_weight, performance_weight, 1, new_firm_perf, new_firm_gov, new_firm_goal)
    
    return gov, goal, perf, overall 


##File download
@callback(
    Output("download_file", "data"),
    Input("dnld_file", "n_clicks"),
    prevent_initial_call=True,
)
def download_func(n_clicks):
    FILE_PATH = PATH.joinpath("assets").resolve()
    return dcc.send_file(
        FILE_PATH.joinpath('Index Calculation.pdf')
    )

##off canvas 
@app.callback(
    Output("per_rank_exp_off", "is_open"),
    Input("per_rank_exp", "n_clicks"),
    [State("per_rank_exp_off", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open



if __name__ == '__main__':
    app.run(debug=True, port=8000)
