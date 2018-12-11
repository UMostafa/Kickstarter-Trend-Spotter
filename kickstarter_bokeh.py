import bokeh
from bokeh.plotting import figure
from bokeh.io import curdoc #, output_file,show,save
from bokeh.models import PanTool, ResetTool, HoverTool, ColumnDataSource
from bokeh.layouts import column,layout
from bokeh.models.annotations import Label
from bokeh.models.widgets import Slider,Button
import pandas as pd
import re
from random import randint
from datetime import datetime,date
from numpy import nan as Nan
import calendar


##########################################################################
##                              LOAD DATA                               ##
##########################################################################

df = pd.read_csv('kickstarter_tech_post_nlp_db',sep='\t')

##########################################################################
##                            DATA WRANGLING                            ##
##########################################################################

# Fix 'pyLDAvis_topics_top3_clean' column by converting to an actual list
def str_to_list(x):
    try:
        x = re.sub(',','',x)
        x = re.sub("'", "",x)
        return x[1:-1].split()
    except:
        return x

df['pyLDAvis_topics_top3_clean'] = df['pyLDAvis_topics_top3_clean'].apply(str_to_list)
df['topics'] = df['pyLDAvis_topics_top3_clean']

# Convert start/end_dt to datetime dates
df['funding_end_dt'] = df['funding_end_dt'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
df['funding_start_dt'] = df['funding_start_dt'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
df['ending'] = df['funding_end_dt'].apply(lambda x: x.strftime("%Y")+'-'+x.strftime("%m"))

# Reduce DataFrame to keep relevant columns only
df['successful_flg'] = df['successful'].apply(lambda x: 1 if x == True else 0)
df['tag_flg'] = df['tag'].apply(lambda x: 1 if x=='Project We Love' else 0)
DA_df = df[['project','ending','backers','pledged','goal','pct_funded','successful','tag','category','topics','successful_flg','tag_flg']]

# Get rid of records with None values
DA_df = DA_df[~DA_df['goal'].isnull()] #<-------------------------------------------------------
DA_df = DA_df[~DA_df['pledged'].isnull()] #<-------------------------------------------------------
DA_df = DA_df[~DA_df['category'].isnull()] #<-------------------------------------------------------
DA_df = DA_df[~DA_df['project'].isnull()] #<-------------------------------------------------------
DA_df = DA_df[~DA_df['backers'].isnull()] #<-------------------------------------------------------

# Get rid of records that have tag stored in category
DA_df = DA_df[DA_df['category'] != 'Project We Love']

# Create periodic variables (to be used later when creating slider)
DA_df['period'] = DA_df['ending'].apply(lambda x: datetime.strptime(x,'%Y-%m'))
DA_df['mth'] = DA_df['ending'].apply(lambda x: int(x[:4])+int(x[-2:])/12)

##########################################################################
##                                 BOKEH                                ##
##########################################################################

# Define colormap and normalize size of bubble
colormap = {'Web':'#34495E','Apps':'crimson','Software':'goldenrod'}
DA_df['color'] = [colormap[x] for x in DA_df['category']]
DA_df['backers'] = DA_df['backers'].apply(lambda x: int(x))
DA_df['pledged'] = DA_df['pledged'].apply(lambda x: int(x))
DA_df['pct_funded_'] = DA_df['pct_funded'].apply(lambda x: max(3,int(x/20)))
DA_df['pledged_'] = DA_df['pledged'].apply(lambda x: int(x/1000))
DA_df['backers_'] = DA_df['backers'].apply(lambda x: max(3,x/200))

# Create Column DataSource
web = ColumnDataSource(DA_df[DA_df['category'] == 'Web'])
web_original = ColumnDataSource(DA_df[DA_df['category'] == 'Web'])
apps = ColumnDataSource(DA_df[DA_df['category'] == 'Apps'])
apps_original = ColumnDataSource(DA_df[DA_df['category'] == 'Apps'])
software = ColumnDataSource(DA_df[DA_df['category'] == 'Software'])
software_original = ColumnDataSource(DA_df[DA_df['category'] == 'Software'])

# Prep output file
#output_file('kickstarter_trend_spotter.html')

# Create figure object
f = figure(plot_height=650, 
           plot_width=1100,
           background_fill_color = "grey",
           background_fill_alpha=0.000,
           y_axis_type="log",
           x_axis_type="log")

# Create glyphs
f.circle(x = "backers_", 
         y = "pledged",
         size = "backers_",
         fill_alpha=0.7,
         color = "color", 
         legend = 'Web',
         source = web)

f.circle(x = "backers_", 
         y = "pledged",
         size = "backers_", 
         fill_alpha=0.7,
         color = "color", 
         legend = 'Apps',
         source = apps)

f.circle(x = "backers_", 
         y = "pledged",
         size = "backers_", 
         fill_alpha=0.7,
         color = "color", 
         legend = 'Software',
         source = software)

# Style the legend
f.legend.location = 'top_right'
f.legend.background_fill_alpha = 0.2
f.legend.border_line_color = None
f.legend.margin = 20
f.legend.label_text_color = 'grey'

# Style the tools
#hover = HoverTool(tooltips=[("Topic","@topic"),("Pledged","@pledged"),("Backers","@backers")]) #("Project","@project"),
hover = HoverTool(tooltips="""
<div>
    <div>
        <span style="font-size: 15px; font-weight: bold; color: #34495E;">@project</span>
    </div>
    <div>
        <span style="font-size: 12px; font-weight: bold; color: #7F8C8D;">@ending</span><br>
        <span style="font-size: 10px; color: #7F8C8D;">Pledged: @pledged</span><br>
        <span style="font-size: 10px; color: #7F8C8D;">Backers: @backers</span><br>
        <span style="font-size: 10px; color: #7F8C8D;">Goal: @goal</span><br>
        <span style="font-size: 10px; color: #7F8C8D;">Funded:Goal Ratio: @pct_funded</span><br>
        <span style="font-size: 10px; color: #7F8C8D;">Topics: @topics</span>
    </div>
</div>
""")

f.add_tools(hover)
f.toolbar_location = 'below'
f.toolbar.logo = None # removes Bokeh logo

# Style the title
f.title.text = 'Kickstarter Trend Spotter' 
f.title.text_font_size = '44px'
#f.title.align = 'center'

# Style the axes
f.axis.minor_tick_line_color = 'grey'
f.xaxis.axis_label = 'Backers'
f.yaxis.axis_label = 'Peldged Amount ($K)'
f.axis.axis_label_text_color = 'black'
f.axis.major_label_text_color = 'grey'
f.axis.axis_label_text_font_size = '12px'
f.axis.axis_label_text_align = 'right'

# Style the grid
f.grid.grid_line_dash = [5,3]

# Create slider functions
def slider_update(attr,old,new):
    s = 0
    # Filter data
    web.data = {key:[value for i,value in enumerate(web_original.data[key]) if web_original.data['mth'][i]<=slider.value] 
    for key in web_original.data}
    apps.data = {key:[value for i,value in enumerate(apps_original.data[key]) if apps_original.data['mth'][i]<=slider.value] 
    for key in apps_original.data}
    software.data = {key:[value for i,value in enumerate(software_original.data[key]) if software_original.data['mth'][i]<=slider.value] 
    for key in software_original.data}
    # Update label
    s = slider.value
    yr = int(s)
    mth = int(round(s%1*12))
    if mth > 0:
        label.text = calendar.month_abbr[mth]+' '+str(yr)
    else:
        label.text = calendar.month_abbr[12]+' '+str(yr-1)


# Create mths range
mths = sorted(set(list(web_original.data['mth']) + list(apps_original.data['mth']) + list(software_original.data['mth'])))

# Create Slider widgets
slider = Slider(start=2012,end=max(mths),value=2012,step=1/12,title="Projects ending on or before")
slider.on_change('value',slider_update)

# Add Year-Month label
label = Label(x = 3,
              y = 6,
              text = '',
              text_font_size='50pt',
              text_color='#DCDCDC',
              render_mode="css")
f.add_layout(label)

# Create auto-play button

def animate_update():
    mth = slider.value + 1/12
    if mth > mths[-1]:
        mth = 2012 #mths[0]
    slider.value = mth

callback_id = None

def animate():
    global callback_id
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        callback_id = curdoc().add_periodic_callback(animate_update, 200)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(callback_id)

button = Button(label='► Play', width=60)
button.on_click(animate)

# Create layout and add to curdoc
lay_out = layout([[f],[slider,[button]]]) #[button]
curdoc().add_root(lay_out)


