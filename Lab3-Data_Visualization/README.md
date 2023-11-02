# README

HCI Lab 3: Data Visualization

![demo](https://github.com/tjuDavidWang/HCI2023/blob/main/Lab3-Data_Visualization/demo.png)

## **Requirements**

- Python 3.7+
- Pandas
- Plotly
- Dash

Install these with: 

```python
pip install pandas plotly dash
```

## **Data**

Place these datasets in the root directory:

- *salaries-by-region.csv*
- *salaries-by-college-type.csv*
- *degrees-that-pay-back.csv*

The data referenced in this analysis was sourced from Kaggle's dataset repository, specifically from the URL: https://www.kaggle.com/datasets/wsj/college-salaries/data.

## **Running**

Run **`python dashboard.py`** and open **`http://127.0.0.1:8050/`** in your browser.

## **Usage**

The dashboard contains a US map, scatter plot, box plot, and bar chart. Use the slider to select the career stage and click on a state in the map to view specific data.
