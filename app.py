import pandas as pd
import streamlit as st
import plotly.express as plt
import numpy as np

df = pd.read_csv("vehicles_us.csv",parse_dates=['date_posted'], date_format='%Y-%m-%d')
#df['model_year']=df['model_year'].astype('Int64')
#df['odometer']=df['odometer'].astype('Int64')
#df['odometer']=df['odometer'].fillna(0)

print(df.info())

# Fill NAN values for is_4wd with 0
df['is_4wd']=df['is_4wd'].fillna(0)

# Fill NAN values for paint_color with 0
df['paint_color']=df['paint_color'].fillna('Unknown')

# Fill NAN values for model_year with  median of model_year for that model
df['model_year'] = df['model_year'].fillna(df.groupby('model')['model_year'].transform('median'))
#df['model_year'] = df.groupby(['model'])['model_year'].transform(lambda x: x.fillna(x.median()))


# Fill NAN values for odometer with  median of odometer when grouped by condition
df['odometer'] = df['odometer'].fillna(df.groupby(['condition'])['odometer'].transform('median'))

# Fill NAN values for cylinders with  median of cylinders when grouped by type
df['cylinders'] = df['cylinders'].fillna(df.groupby(['type'])['cylinders'].transform('median'))

# Splitting Model column into Make and Model_Series  columns
df[['make', 'model_series']] = df['model'].str.split(' ', n=1, expand=True).fillna('')


#df_head =  df.head(10)
#display(df_head)
#display(df.columns)
print(df.info())
#display(df.describe())

df_counts = df.groupby('model_year').agg(vehicles_available = ('type','count')).reset_index()
#print(df_counts)
st.header("Used Vehicle Information(US) for Sale", divider=True)


year_series = df['model_year']
years = year_series.sort_values(ascending=False).unique()
clean_arr = years[~np.isnan(years)]
cleaned_year_list = clean_arr.tolist()

st.sidebar.header('Filter Options:')
selected_year = st.sidebar.selectbox('Year', cleaned_year_list)


@st.cache_data
def load_vehicle_info(year):
    df_yearwise_counts = df[df['model_year'] == selected_year].reset_index(drop=True)
    return df_yearwise_counts

result_df = load_vehicle_info(selected_year)

sorted_unique_model = sorted(result_df.model.unique())
selected_model = st.sidebar.multiselect('Model', sorted_unique_model,sorted_unique_model)


sorted_unique_condition = sorted(result_df.condition.unique())
selected_condition = st.sidebar.multiselect('Condition', sorted_unique_condition,sorted_unique_condition)

sorted_unique_fuel = sorted(result_df.fuel.unique())
selected_fuel = st.sidebar.multiselect('Fuel Type', sorted_unique_fuel,sorted_unique_fuel)

sorted_unique_color = sorted(result_df.paint_color.astype(str).unique())
selected_color = st.sidebar.multiselect('Body Color', sorted_unique_color,sorted_unique_color)


selected_result_df = result_df[(result_df.condition.isin(selected_condition)) & (result_df.model.isin(selected_model)) 
                               & (result_df.fuel.isin(selected_fuel)) & (result_df.paint_color.isin(selected_color) )]
                                                                         #& (result_df.price.astype(int) < selected_price))]

if selected_result_df.shape[0] != 0:
    st.dataframe(selected_result_df)
else:
    st.write("No Data Retrieved")
    
    
disp_graph = st.checkbox("Select Checkbox to display Vehicle  color count graph using filtered data:")
#st.write("Vehicles available in Year by Color:: ")
df_counts = selected_result_df.groupby('paint_color').agg(vehicles_available = ('model_year','count')).reset_index()
#st.write(df_counts)

if disp_graph:
    fig = plt.histogram(df_counts, x='paint_color', y='vehicles_available', title='Vehicle (colors) available for selected criteria',nbins=10, width=1200, height=800)
    fig.update_layout(
    xaxis_title_text = 'Vehicle Color', 
    yaxis_title_text = 'Available count'
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("")



## Data Visualization
#This Scatter  plot show the price vs Odometer value for a given make (RAM) of the car
#st.write("Scatter plot of Price vs Odometer:")

disp_scat_plot_graph = st.checkbox("Select Checkbox to display Scatter plot graph Price vs Odometer for vehicle brand RAM ")

if disp_scat_plot_graph:
    # Create the scatter plot using Plotly Express
    subset = df[df['make'] == 'ram']
    #fig = plt.scatter(subset, x='price', y='odometer',
    #             title='Vehicle Price vs Odometer Scatter Plot')
    scatter_plt = plt.scatter(subset, y='price', x='odometer', color='make', color_discrete_sequence=plt.colors.qualitative.Plotly,
                 title='Vehicle Price vs Odometer Scatter Plot')

    # Display the plot in Streamlit
    st.plotly_chart(scatter_plt)
    
    ## Data Visualization
    
else:
    st.write("")
    
    
## Data Visualization
# This Box plot gives an idea of the median prices comparison of prices between pickup trucks for ford, toyota & chevrolet
#st.write("Box plot of Price vs type:")
disp_box_plot_graph = st.checkbox("Select Checkbox to display box plot graph using base data Price vs Vehicle Type:")

if disp_box_plot_graph:


    makes = ['ford', 'toyota', 'chevrolet']
    subset = df[(df['make'].isin(makes)) & (df['type'] == 'pickup')]
    box_plt = plt.box(subset, x='price', y='make', title='Vehicle Price distribution for pickup trucks ( ford , toyota & chevrolet )')
    #box_plt = plt.box(df, x='price', y='type', color_discrete_sequence=plt.colors.qualitative.Plotly,
    #             title='Vehicle Price distribution by type')
    st.plotly_chart(box_plt)
    #box_plt.show()
