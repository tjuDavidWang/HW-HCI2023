# 导入需要的库
import plotly.express as px
import dash
from dash import dcc
from dash import html
import pandas as pd
import plotly.graph_objects as go

# 加载数据
region = pd.read_csv('salaries-by-region.csv')
type = pd.read_csv('salaries-by-college-type.csv')
major = pd.read_csv('degrees-that-pay-back.csv')

# 列名列表，这些列的值会被用于滑块的标记
col_num_name = ["Starting Median Salary", "Mid-Career Median Salary",
                "Mid-Career 10th Percentile Salary", "Mid-Career 25th Percentile Salary",
                "Mid-Career 75th Percentile Salary", "Mid-Career 90th Percentile Salary"]
# 数据列表
data = [region, type, major]

# 清理数据集中的数值列，将美元符号和逗号去除，然后转换为数字类型
for i_data in data:
    for name in col_num_name:
        i_data[name] = i_data[name].str.replace('$', '', regex=False)   # 去除美元符号
        i_data[name] = i_data[name].str.replace(',', '')  # 去除逗号
        i_data[name] = pd.to_numeric(i_data[name], errors='coerce')  # 转换为数字类型

# 设置默认选项
default_column = 'Mid-Career Median Salary'

# 创建滑动条的标记
slider_marks = {
    0: {'label': 'Start', 'style': {'writing-mode': 'horizontal-tb', 'text-orientation': 'mixed'}},
    1: {'label': 'Median', 'style': {'writing-mode': 'horizontal-tb', 'text-orientation': 'mixed'}},
    2: {'label': '90%', 'style': {'writing-mode': 'horizontal-tb', 'text-orientation': 'mixed'}},
    3: {'label': '75%', 'style': {'writing-mode': 'horizontal-tb', 'text-orientation': 'mixed'}},
    4: {'label': '25%', 'style': {'writing-mode': 'horizontal-tb', 'text-orientation': 'mixed'}},
    5: {'label': '10%', 'style': {'writing-mode': 'horizontal-tb', 'text-orientation': 'mixed'}}
}

# 创建一个新列 "Salary"，并将其值设置为 default_column 对应的值
# 这个列将被用于设置颜色范围
color_min = 0
color_max = 250000
region['Salary'] = region[default_column]

# 创建一个新列 "CustomData"，并将其值设置为 selected_column 对应的值
# 这个列将被用于设置自定义数据
selected_column = default_column
region['CustomData'] = region[selected_column].apply(lambda x: f'${x:,.2f}')

# 创建一个地理信息图，将 Salary 列用于设置颜色，将 CustomData 和 States 列用于设置自定义数据
fig = px.choropleth(region,
                    locations='States', locationmode='USA-states',
                    color='Salary',
                    custom_data=['CustomData', 'States'],  # 添加自定义数据，包括薪资和州名
                    color_continuous_scale='blues',
                    range_color=[color_min, color_max],  # 设置颜色范围
                    scope='usa',
                    title='Mid-Career Median Salary by Region')

# 创建 Dash 应用
app = dash.Dash(__name__)

# 定义应用的布局
app.layout = html.Div([
    # 网页标题
    html.H1("Data Visualization ",
            style={"textAlign": "center", "color": "white", "backgroundColor": "black", "marginBottom": "0px",
                   "marginTop": "0px"}),
    # 作者信息
    html.H5("Author: Weida Wang 2151300",
            style={"textAlign": "center", "fontStyle": "italic", "color": "white", "backgroundColor": "black",
                   "marginTop": "0px"}),
    # 滑动条组件
    html.Div([
        dcc.Slider(
            id='column-slider',
            min=0,
            max=len(col_num_name) - 1,
            value=col_num_name.index(default_column),
            marks=slider_marks,
            step=1
        )
    ], style={'width': '300px', 'padding': 'auto', 'paddingTop': '0px', 'paddingBottom': '0px', 'margin': 'auto'}),
    # 图表组件
    html.Div([
        html.Div([
            dcc.Graph(id='graph1', figure=fig, clickData={'points': [{'location': 'CA'}]}),  # 默认点击数据为 'CA'
        ], style={'display': 'inline-block', 'width': '50%'}),
        html.Div([
            dcc.Graph(id='graph2', figure={}),  # 图表初始为空
        ], style={'display': 'inline-block', 'width': '50%', 'textAlign': 'center', "marginBottom": "0px",
                  "marginTop": "0px"}),
    ], style={'marginTop': '0px', 'marginButtom': '0px'}),
    html.Div([
        html.Div([
            dcc.Graph(id='graph3', figure={}),  # 图表初始为空
        ], style={'display': 'inline-block', 'width': '50%', 'height': '50%', 'textAlign': 'center',
                  "marginBottom": "0px",
                  "marginTop": "0px"}),
        html.Div([
            dcc.Graph(id='graph4', figure={}),  # 图表初始为空
        ], style={'display': 'inline-block', 'width': '50%', 'textAlign': 'center', "marginBottom": "0px",
                  "marginTop": "0px"}),
    ], style={'marginTop': '0px', 'marginBottom': '0px'}),
], style={'backgroundColor': 'black', 'color': 'white'})


# 定义一个回调函数，当滑动条的值发生改变时，更新地理信息图
@app.callback(
    dash.dependencies.Output('graph1', 'figure'),
    [dash.dependencies.Input('column-slider', 'value')]
)
def update_figure(selected_index):
    # 从滑动条中获取选中的列名
    selected_column = col_num_name[selected_index]

    # 更新 Salary 列的值
    region['Salary'] = region[selected_column]

    # 更新 CustomData 列的值
    region['CustomData'] = region[selected_column].apply(lambda x: f'${x:,.2f}')

    # 创建新的地理信息图
    fig = px.choropleth(region,
                        locations='States',
                        locationmode='USA-states',
                        color='Salary',
                        custom_data=['CustomData', 'States'],
                        color_continuous_scale='Blues',
                        range_color=[color_min, color_max],
                        scope='usa',
                        )
    # 更新图表的布局
    fig.update_layout(
        title_text='Median Salary by Region',
        title_x=0.5, title_y=0.9,
        geo_bgcolor='black',  # 设置地图背景色为黑色
        plot_bgcolor='black',  # 设置图表背景色为黑色
        paper_bgcolor='black',  # 设置整个画布的背景色为黑色
        font=dict(color='white')  # 设置字体颜色为白色
    )
    fig.update_traces(hovertemplate='<b>%{location}</b><br>' +
                                    f'{selected_column}: ' + '%{customdata[0]}<br>' +
                                    'State Code: %{customdata[1]}')

    return fig


# 定义一个回调函数，当点击地图或者滑动条的值发生改变时，更新散点图
@app.callback(
    dash.dependencies.Output('graph2', 'figure'),
    [dash.dependencies.Input('graph1', 'clickData'),
     dash.dependencies.Input('column-slider', 'value')]
)
def update_graph2(clickData, selected_index):
    # 从点击的数据中获取选中的州名
    selected_state = clickData['points'][0]['location']
    # 从滑动条中获取选中的列名
    selected_column = col_num_name[selected_index]

    # 选取与选中州对应的数据
    df_selected = region[region['States'] == selected_state]

    # 创建散点图
    fig2 = go.Figure(data=go.Scatter(
        x=df_selected['School Name'],
        y=df_selected[selected_column],
        mode='markers',
        marker=dict(
            color=df_selected[selected_column],
            colorscale='blues',  # 设置颜色方案为蓝色系
            colorbar=dict(title="Salary"),
            showscale=True,
            cmin=0,  # 设置颜色范围的最小值
            cmax=250000  # 设置颜色范围的最大值
        )
    ))

    # 更新散点图的布局
    fig2.update_layout(title='Schools in {} - {}'.format(selected_state, selected_column),
                       xaxis_title='School Name', xaxis_visible=False, xaxis_showgrid=True,
                       yaxis_title=selected_column, yaxis_visible=True, yaxis_showgrid=True,
                       title_x=0.5, title_y=0.9,
                       paper_bgcolor='black',
                       plot_bgcolor='rgb(25,25,25)',
                       font=dict(color='white'),
                       margin=dict(l=50, r=50, t=50, b=50),  # 调整边距，添加边框
                       )

    return fig2


# 定义一个回调函数，当滑动条的值发生改变时，更新箱线图
@app.callback(
    dash.dependencies.Output('graph3', 'figure'),
    [dash.dependencies.Input('column-slider', 'value')]
)
def update_boxplot(selected_index):
    # 从滑动条中获取选中的列名
    selected_column = col_num_name[selected_index]

    # 创建箱线图
    fig = px.box(type, x="School Type", y=selected_column, color="School Type",
                 title="Salary by School Type",
                 color_discrete_sequence=px.colors.sequential.Blues,
                 )

    # 更新箱线图的布局
    fig.update_layout(xaxis_title="School Type", yaxis_title=selected_column, title_x=0.5, title_y=0.9,
                      paper_bgcolor='black',
                      plot_bgcolor='black',
                      font=dict(color='white')
                      )

    return fig


# 定义一个回调函数，当滑动条的值发生改变时，更新条形图
@app.callback(
    dash.dependencies.Output('graph4', 'figure'),
    [dash.dependencies.Input('column-slider', 'value')]
)
def update_barplot(selected_index):
    # 声明全局变量major
    global major
    # 从滑动条中获取选中的列名
    selected_column = col_num_name[selected_index]

    # 按照选中的列对专业数据进行排序
    major = major.sort_values(by=selected_column, na_position='last')

    # 创建条形图
    fig4 = px.bar(major, x=selected_column, y='Undergraduate Major', title=selected_column,
                  color_discrete_sequence=['#1f77b4'])
    # 更新条形图的布局
    fig4.update_layout(
        xaxis_title=selected_column,
        yaxis_title='Undergraduate Major',
        title_x=0.5,
        title_y=0.9,
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white')
    )
    return fig4


if __name__ == '__main__':
    app.run_server(debug=True)
