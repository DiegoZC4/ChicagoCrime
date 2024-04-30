import pandas as pd
from datetime import date, time
# interactive plots
import folium
from folium.plugins import Fullscreen, MarkerCluster, BeautifyIcon
import plotly.express as px
import plotly.io as pio
import pickle

class Crime:
  def __init__(self):
    self.crime=pd.read_pickle('crime.pkl')
    self.patrol = pickle.load(open('patrol.pkl','rb'))
    self.colors = ['red','green','orange','black']
    self.colorLegend = {k:v for k,v in zip(['Violent Crime','Property Crime','Violation','Crimes Against Children'], self.colors)}
    self.patrolLegend = {'UChicago Campus':'blue','Extended Patrol Area':'black'}
  
  def dateBounds(self):
    return [str(self.crime['Datetime'].dt.date.min()),str(self.crime['Datetime'].dt.date.max())]

  def map(self,data,icon_size=25):
    map = folium.Map(location=[data['Latitude'].mean(), data['Longitude'].mean()], zoom_start=14)
    Fullscreen(
      position="topright",
      title="Fullscreen",
      title_cancel="Exit Fullscreen",
      force_separate_button=True,
    ).add_to(map)
    for area in self.patrol: area.add_to(map)

    markers = MarkerCluster().add_to(map)
      
    for index, row in data.iterrows():
      folium.Marker(
      [row['Latitude'],row['Longitude']],
      popup=folium.Popup(folium.Html(f'<div style="display:inline-block;font-size:16px;">{row["Details"]}</div>', script=True), max_width=265),
      icon = BeautifyIcon(icon=row['Icon'], inner_icon_style=f"color:{self.colors[row['Color']]};font-size:{icon_size}px;",background_color='transparent',border_color='transparent',icon_anchor=(icon_size/2, icon_size/2))
      ).add_to(markers)
    return map._repr_html_()
  
  def filterPlot(self, form):
    data = self.crime
    # dates
    if startDate:= form.get('startDate'):
      data = data[date.fromisoformat(startDate)<=data['Datetime'].dt.date]
    if endDate:= form.get('endDate'):
      data = data[date.fromisoformat(endDate)>=data['Datetime'].dt.date]
    # times
    if startTime:= form.get('startTime'):
      data = data[time.fromisoformat(startTime)<=data['Datetime'].dt.time]
    if endTime:= form.get('endTime'):
      data = data[time.fromisoformat(endTime)>=data['Datetime'].dt.time]
    # weekdays
    data = data[data['Weekday'].isin([var for var in form.keys() if 'day' in var])]
    # details
    if details:= form.get('details'):
      for word in details.split(','):
        data=data[data['Details'].str.contains(word.strip(), case=False)]
    
    if not len(data): return {'empty':True}
    self.data=data

    results = {}
    plots = []
    # map
    if form.get('Map'):
      results['map'] = self.map(data)
      results['colorLegend'] = self.colorLegend
      results['patrolLegend'] = self.patrolLegend

    # table
    if form.get('Table'):
      results['table'] = data.drop(['Color','Icon','Details'],axis=1).to_html(classes='sortable', index=False, table_id='crime_data')
  
    # lines
    if form.get('Day'):plots.append(self.plot('Datetime',data.groupby(data['Datetime'].dt.time),'Hourly','Time'))
    if form.get('Week'): plots.append(self.plot('Weekday',data.groupby(data['Weekday']),'Weekday','Day of the Week'))
    if form.get('Year'): plots.append(self.plot('Datetime',data.groupby(data['Datetime'].dt.date),'Daily','Date'))
    
    # Pies
    if form.get('Street'):
      plots.append(self.pie('Street',data['Address'].str.slice(5)))
    for col in ['Type','Description','Scene','Neighborhood']:
      if form.get(col): plots.append(self.pie(col))
    
    results['plots'] = [pio.to_json(p) for p in plots]
    results['count'] = len(data)
    results['shepherd'] = len(data)%10 == 4
    return results
  
  def plot(self,column,data,title,xlabel):
    return px.line(data.size().reset_index(name='Count'), x=column, y='Count', title=f'{title} Crime Count',
            labels={'Datetime': xlabel, 'Count': 'Number of Crimes'}, markers=True)
  
  def pie(self,name,data=[]):
    if not len(data): data = self.data[name]
    counts = data.value_counts().reset_index()
    counts.columns = [name, 'Counts']

    # Create an interactive pie chart
    fig = px.pie(counts, values='Counts', names=name, title=f'Crime by {name}')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig    