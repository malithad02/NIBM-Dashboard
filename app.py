import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# ---------------------------------------------------------
# 1. SETUP APP
# ---------------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server = app.server  # Required for Render deployment

# ---------------------------------------------------------
# 2. LAYOUT
# ---------------------------------------------------------
app.layout = dbc.Container([
    # Title
    dbc.Row(dbc.Col(html.H1(" Data Science Student's Literacy Dashboard", className="text-center mt-4 mb-4"))),
    
    # The "Secret" Timer (Updates data every 5 seconds)
    dcc.Interval(id='timer', interval=5000, n_intervals=0),
    
    # Chart Row 1
    dbc.Row([
        dbc.Col(dcc.Graph(id='scatter'), width=12, lg=6, className="mb-4"),
        dbc.Col(dcc.Graph(id='bar'), width=12, lg=6, className="mb-4"),
    ]),
    
    # Chart Row 2
    dbc.Row([
        dbc.Col(dcc.Graph(id='box'), width=12, lg=6, className="mb-4"),
        dbc.Col(dcc.Graph(id='violin'), width=12, lg=6, className="mb-4"),
    ])
], fluid=True)

# ---------------------------------------------------------
# 3. LOGIC (CALLBACKS)
# ---------------------------------------------------------
@app.callback(
    [Output('scatter', 'figure'), Output('bar', 'figure'),
     Output('box', 'figure'), Output('violin', 'figure')],
    [Input('timer', 'n_intervals')]
)
def update_graphs(n):
    # I found your link from your screenshot and fixed it to 'output=csv'
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ1gF4lUrUv081mm-qt5Vy4a5iSeY00W-vuSZ5QSt8YfNRwWpcfzXdBrUwu9waV_xL1H9M0T8iL8GeI/pub?output=csv"
    
    try:
        # Read the data
        df = pd.read_csv(url)
        
        # 1. CLEAN COLUMN NAMES
        # Remove any accidental spaces at the start/end of names
        df.columns = df.columns.str.strip()
        
        # 2. FIX DUPLICATE NAMES (The "Magic Fix")
        # Google Sheets sends multiple columns named "Proficiency". 
        # We rename them by their POSITION (index) to avoid confusion.
        cols = list(df.columns)
        if cols.count('Proficiency') > 1:
            # We assume the order is: Pandas -> Scikit -> Plotly -> TensorFlow
            # Note: You might need to adjust these numbers if your sheet changes
            df.columns.values[9] = 'Proficiency_Pandas'
            df.columns.values[10] = 'Proficiency_Scikit'
            df.columns.values[11] = 'Proficiency_Plotly'
            df.columns.values[12] = 'Proficiency_TensorFlow'
        
        # Also fix cut-off names if they exist
        if 'Projects_C' in df.columns:
            df.rename(columns={'Projects_C': 'Projects_Completed'}, inplace=True)
        if 'Courses_C' in df.columns:
            df.rename(columns={'Courses_C': 'Courses_Completed'}, inplace=True)

        # 3. FORCE NUMBERS
        # This prevents crashes if the sheet has text in number columns
        df['Study_Hours_Per_Week'] = pd.to_numeric(df['Study_Hours_Per_Week'], errors='coerce')
        df['Projects_Completed'] = pd.to_numeric(df['Projects_Completed'], errors='coerce')
        df['Courses_Completed'] = pd.to_numeric(df['Courses_Completed'], errors='coerce')
        
        # If we successfully renamed Pandas, convert it too. If not, fill with 0.
        if 'Proficiency_Pandas' in df.columns:
            df['Proficiency_Pandas'] = pd.to_numeric(df['Proficiency_Pandas'], errors='coerce')
        else:
            df['Proficiency_Pandas'] = 0

        # 4. BUILD CHARTS
        fig1 = px.scatter(df, x='Study_Hours_Per_Week', y='Proficiency_Pandas', 
                          size='Projects_Completed', color='Year', 
                          title="Study Hours vs Pandas Skill", template="plotly_white")
        
        fig2 = px.bar(df, x='Year', y='Courses_Completed', 
                      title="Avg Courses by Year", template="plotly_white")
        
        fig3 = px.box(df, x='Confidence_Level', y='Projects_Completed', 
                      title="Confidence vs Projects", template="plotly_white")
        
        fig4 = px.violin(df, x='AI_Impact', y='Projects_Completed', box=True, 
                         title="AI Impact on Output", template="plotly_white")
        
        return fig1, fig2, fig3, fig4

    except Exception as e:
        print(f"ERROR: {e}")
        # Return empty charts with the error message so you can see it on screen
        return px.scatter(title=f"Error: {e}"), px.bar(), px.box(), px.violin()

if __name__ == '__main__':
    app.run(debug=True)