import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt
st.set_page_config(layout="wide")


def load_data():
    #2 pandas functions in 1 line
    df=pd.read_csv("volcanoes.csv",encoding="cp1252").dropna()
    #had to look this up online, kept getting a weird error message, clears missing values and encodes as latin alphabet
    return df

def chart_options(index):
    st.header("Chart Options")
    #Splitting page into 3 columns and defining each for organization (c2, c3, c4)
    c2,c3,c4=st.beta_columns(3)
    alpha=c2.slider("Select Transparency",0.0,1.0,.5,key=index)
    grid=c3.checkbox("Grid?",key=index)
    color=c4.selectbox("Select Color for Charts",["purple","red","blue","green","yellow","orange","black","grey"],key=index)

#Grid Feature, with index as key so it applies to each chart
    if grid ==True:
        linestyle=c3.selectbox("What lines would you like for the grid",["-","--","-.",":"],key=index)
        thickness=c3.slider("Grid thickness",0.0,2.0,.5,key=index)
        color2=c3.selectbox("Select Color for grid",["purple","red","blue","green","yellow","orange","black","grey"],key=index)

    else:
        linestyle=0
        thickness=0
        color2=0
    return alpha,grid,linestyle,thickness,color,color2


def load_charts():
    st.header("CHART PARTY!!")
    index=0
    alpha,grid,linestyle,thickness,color,color2=chart_options(index)
    df=load_data()
    col1,col2=st.beta_columns(2)

    plt.hist(df["Elevation (m)"], bins=30,color=color, alpha=alpha)
    if grid==True:
        plt.grid(color=color2, linestyle=linestyle, linewidth=thickness)

    plt.ylabel("Number of Volcanos")
    plt.xlabel("Elevation of Volcanos")
    plt.title(f"Distribution of Volcano Elevation")
    col1.pyplot(plt)
    col2.header("Elevation Statistics")
    col2.write(df["Elevation (m)"].describe())
    plt.clf()
    index+=1

#Region Chart
    alpha,grid,linestyle,thickness,color,color2=chart_options(index)
    objects = df["Region"].unique()
    y_pos = np.arange(len(objects))
    performance = [len(df[df["Region"]==x]) for x in objects]
    plt.barh(y_pos, performance, align='center', alpha=alpha,color=color)
    if grid==True:
        plt.grid(color=color2, linestyle=linestyle, linewidth=thickness)

    plt.yticks(y_pos, objects)
    plt.xlabel('Number of Volcanos')
    plt.ylabel("Regions")
    plt.title('Number of Volcanos by Region')
    st.pyplot(plt)
    #clears figure for next plot
    plt.clf()
    index+=1

#Dominant Rock Chart
    alpha,grid,linestyle,thickness,color,color2=chart_options(index)
    objects = df["Dominant Rock Type"].unique()
    y_pos = np.arange(len(objects))
    performance = [len(df[df["Dominant Rock Type"]==x]) for x in objects]
    plt.barh(y_pos, performance, align='center', alpha=alpha,color=color)
    if grid==True:
        plt.grid(color=color2, linestyle=linestyle, linewidth=thickness)

    plt.yticks(y_pos, objects)
    plt.xlabel('Number of Volcanos')
    plt.ylabel("Rock Type")
    plt.title('Number of Volcanos w/Rock Type')
    st.pyplot(plt)
    plt.clf()
    index+=1

  #Tectonic Setting Chart
    alpha,grid,linestyle,thickness,color,color2=chart_options(index)
    objects = df["Tectonic Setting"].unique()
    y_pos = np.arange(len(objects))
    performance = [len(df[df["Tectonic Setting"]==x]) for x in objects]
    plt.barh(y_pos, performance, align='center', alpha=alpha,color=color)
    if grid==True:
        plt.grid(color=color2, linestyle=linestyle, linewidth=thickness)

    plt.yticks(y_pos, objects)
    plt.xlabel('Number of Volcanos')
    plt.ylabel("Tectonic Setting")
    plt.title('Number of Volcanos by Tectonic Setting')
    st.pyplot(plt)
    plt.clf()
    index+=1


    alpha,grid,linestyle,thickness,color,color2=chart_options(index)
    years=[]
    #Fixing the Issue of common era and before common era by splitting and taking only the year value
    for i,x in enumerate(df["Last Known Eruption"]):
        if "BCE" in x:
            x=-int(x.split(" ")[0])
        elif "CE" in x:
            x=int(x.split(" ")[0])
        elif x=="Unknown":
            continue
        years.append(x)

    #Creating Histogram for last known eruption distribution
    plt.hist(years, bins=20,color=color, alpha=alpha)
    if grid==True:
        plt.grid(color=color2, linestyle=linestyle, linewidth=thickness)
    plt.ylabel("Number of Volcanos")
    plt.xlabel("Year of Last Eruption")
    plt.title(f"Distribution of Last Eruptions")
    st.pyplot(plt)


def load_maps():
    df=load_data()
    options=[]
    for x in df:
        options.append(x)
    #TTS = Tooltip Select, creates multiselect box, shows selection option data at the bottom
    tts=st.multiselect("Select data to diplay on mouse hover and on dataframe below map",options)
    tt=""
    for feature in tts:
        tt=tt+" "+feature+": {"+feature+"} |"
    #Breaking up the data by aboveground and underground volcanoes, making the underground data positive for map represenation
    under=df[df["Elevation (m)"]<0]
    under["elev"]=-under["Elevation (m)"]
    over=df[df["Elevation (m)"]>0]
    over["elev"]=over["Elevation (m)"]
    view=pdk.ViewState(latitude=over["Latitude"].mean(),longitude=over["Longitude"].mean(),pitch=20,zoom=0)

#Creating Map Layers
    o = pdk.Layer("ColumnLayer",data=over,get_position=["Longitude", "Latitude"],get_elevation="elev",elevation_scale=100,radius=10000,pickable=True,auto_highlight=True,get_fill_color=[225,0,0,225])
    u= pdk.Layer("ColumnLayer",data=under,get_position=["Longitude", "Latitude"],get_elevation="elev",elevation_scale=100,radius=10000,pickable=True,auto_highlight=True,get_fill_color=[0,30,225,225])
    tooltip = {"html": tt,"style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"}}
#Using pydeck for map
    map=pdk.Deck(map_provider='carto',layers=[o,u],initial_view_state=view,api_keys=None,tooltip=tooltip)
    st.pydeck_chart(map)
   #Making sure the tooltip selector only selects column headings, not data
    for x in df:
        if x not in tts:
            df=df.drop(columns=[x])
    st.dataframe(df)

def main():
#Main and Sidebar
    st.title("Volcano Explorer")
    st.sidebar.title("Menu Navigator:")
    mm=st.sidebar.selectbox("Select Feature",["View Maps","View Charts","Raw Data"])
    if  mm=="View Charts":
        load_charts()
    if mm=="Raw Data":
        st.header("Raw Data")
        st.dataframe(load_data())
    if mm=="View Maps":
        load_maps()

main()
