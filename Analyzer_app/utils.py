from django.shortcuts import render
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

month_order = ['January', 'February', 'March', 'April', 'May', 'June','July', 'August', 'September', 'October', 'November', 'December']

instructor_values = {
    'Marco': 15,
    'Lorenzo': 15,
    'Alberto': 25,
    'Federica': 30*1.22,
    'Caterina': 30*1.22
}

def OpenSpreadSheet(name_file, name_sheet):
  credentials = ServiceAccountCredentials.from_json_keyfile_name('pippo.json')
  gc = gspread.authorize(credentials)
  spreadsheet = gc.open(name_file)

  if not isinstance(name_sheet, list):
      name_sheet = [name_sheet]

  worksheets = []
  for sheet in name_sheet:
    SHEET = spreadsheet.worksheet(sheet)
    sheet_data = SHEET.get_all_values()
    df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
    worksheets.append(df)
  return worksheets

def clean_and_convert(value):
    if isinstance(value, (int, float)):
        return float(value)
    cleaned_value = ''.join(filter(lambda x: x.isdigit() or x in '-', str(value)))
    if cleaned_value == '':
        return 0.0  # Or any default value you prefer
    
    return float(cleaned_value)

def clean_commerciale(commerciale):
    commerciale['Paid'] = commerciale['Paid'].apply(clean_and_convert)
    commerciale['Prezzo totale'] = commerciale['Prezzo totale'].apply(clean_and_convert)
    commerciale['Data'] = pd.to_datetime(commerciale['Data inizio'], dayfirst=True)
    commerciale['Month'] = commerciale['Data'].dt.strftime('%B')

    commerciale['Data fine'] = pd.to_datetime(commerciale['Data fine'], dayfirst=True)
    commerciale['Mese fine'] = commerciale['Data fine'].dt.strftime('%B')
    commerciale["Ones"] = 1

    commerciale["Paid_month"] = commerciale.groupby('Month')['Paid'].transform('sum')
    commerciale["Contratti_month"] = commerciale.groupby('Month')['Prezzo totale'].transform('sum')
    commerciale["Utenti_day"] = round(commerciale.groupby('Data')['Data'].transform('count'),2)
    commerciale["Utenti_month"] = round(commerciale.groupby('Month')['Month'].transform('count'),2)
    commerciale['Paid_user_month_y'] = round(commerciale.groupby('Month')['Paid'].transform('sum') / commerciale.groupby('Month')['Nome e Cognome'].transform('nunique'),2)
    commerciale['Contratti_month_y'] = round(commerciale.groupby('Month')['Prezzo totale'].transform('sum') / commerciale.groupby('Month')['Nome e Cognome'].transform('nunique'),2)
    commerciale["Paid_user_month_m"] = round(commerciale['Paid_user_month_y']/12,2)
    commerciale["Contratti_month_m"] = round(commerciale['Contratti_month_y']/12,2)
    return commerciale

def clean_spese(spese):
    spese['Valore'] = spese['Valore'].apply(clean_and_convert)
    spese['Data'] = pd.to_datetime(spese['Data'], dayfirst=True)
    spese['Month'] = spese['Data'].dt.strftime('%B')
    return spese

def clean_trattative(trattative):
    trattative['Data inizio trattativa'] = pd.to_datetime(trattative['Data inizio trattativa'], dayfirst=True)
    trattative['Month'] = trattative['Data inizio trattativa'].dt.strftime('%B')
    trattative["Count"] = 1
    return trattative

def clean_corsi(corsi):
    corsi['Data'] = pd.to_datetime(corsi['Data'], dayfirst=True)
    corsi['Month'] = corsi['Data'].dt.strftime('%B')
    corsi['Ora inizio'] = pd.to_datetime(corsi['Ora inizio'], format='%H:%M')
    corsi['Ora fine'] = pd.to_datetime(corsi['Ora fine'], format='%H:%M')
    corsi['Durata'] = corsi['Ora fine'] - corsi['Ora inizio']
    corsi['Durata_hours'] = (corsi['Durata'].dt.total_seconds() / (60*60)).apply(clean_and_convert)
    corsi['Day_of_Week'] = corsi['Data'].dt.day_name()
    return corsi

def clean_private(private):
    private['Data'] = pd.to_datetime(private['Data'], dayfirst=True)
    private['Month'] = private['Data'].dt.strftime('%B')
    private['Ora inizio'] = pd.to_datetime(private['Ora inizio'], format='%H:%M')
    private['Ora fine'] = pd.to_datetime(private['Ora fine'], format='%H:%M')
    private['Durata'] = private['Ora fine'] - private['Ora inizio']
    private['Durata_hours'] = (private['Durata'].dt.total_seconds() / (60*60)).apply(clean_and_convert)
    private['Day_of_Week'] = private['Data'].dt.day_name()
    return private

def melt_staff(wide_df):
    tall_df = pd.melt(
        wide_df,
        id_vars=['Data'],  # 'Data' is the column that will remain fixed
        var_name='Instructor',  # column containing instructor names
        value_name='ore'  # column containing the corresponding values
    )
    return tall_df

def clean_staff(staff):
    staff['Data'] = pd.to_datetime(staff['Data'], dayfirst=True)
    staff['Month'] = staff['Data'].dt.strftime('%B')
    staff['ore'] = pd.to_numeric(staff['ore'].str.replace(',', '.'))    
    staff['Instructor_value'] = staff['Instructor'].map(instructor_values)
    staff['Instructor_earn'] = staff['ore'] * staff['Instructor_value']
    return staff

def my_layout(fig):
    fig.update_layout(
        xaxis_title='',
        yaxis_title='',
        legend_title_text='Legend',
        title_x=0.5,
        title_font=dict(size=16),
        legend=dict(orientation="h"),
        )
    return fig

def standard_hist(data,x,y,title,legend_value=None, stack=False, exclude_words=[]):
    hover_data = [col for col in data.columns.tolist() if all(word not in col for word in exclude_words)]

    color_discrete_map = None
    if legend_value is not None:
        color_discrete_map = dict(zip(data[legend_value].unique(), px.colors.qualitative.Bold))

    fig = px.bar(data, x=x, y=y, title=title, text=y, hover_data=hover_data,
                 template="plotly_white", color=legend_value, category_orders={'Month': month_order},
                 color_discrete_map=color_discrete_map)

    fig = my_layout(fig)
    if stack:
        fig.update_layout(barmode='stack')  

    fig.update_traces(marker_line_width=1, marker_line_color="black")
    return fig
