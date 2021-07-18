import requests
import json
from django.shortcuts import render
import pandas as pd
from tensorflow.keras.models import load_model
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime
#from gtts import gTTS
import os
from django.conf import settings
#from playsound import playsound

#from twilio.rest import Client
#account_sid="your account id"
#auth_token="your token"
#client=Client(account_sid,auth_token)
# import io
# import urllib, base64
# import os

import geocoder
import reverse_geocoder as rg

model = load_model('ibm3_best.h5') 
print ('model loaded..')

wind_speed_mean = 7.549162
wind_direction_mean = 123.516124 

wind_speed_std = 4.227196  
wind_dir_std = 93.435472

norm_data = pd.DataFrame()

language = 'en'
#audio = "assets/speech.mp3"

audio = (os.path.join(settings.MEDIA_ROOT, 'speech.mp3'))
# Create your views here.

def home(request):
    #url="http://api.openweathermap.org/data/2.5/weather?q=indore&units=imperial&appid=d55d5d4915b255b333b029be932d96ec"
    url="http://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&appid=d55d5d4915b255b333b029be932d96ec"
    city= request.POST.get('city')
    uri=''
    number= request.POST.get('number')
    print(number)
    #print(number)

    #city="indore"
    #s=requests.get(url.format(city))
    #print(s.text)
    r=requests.get(url.format(city)).json()
    print(r)
    #r=requests.get(url).json()
    if(city==None):
        return render(request,"ui.html")
    else:
        if(r.get('cod')=='200'):
            r = (r['list'])

            final_df = pd.DataFrame()
            temp= []
            wind_speed=[]
            wind_direc=[]
            date_time=[]
            norm_wind_speed=[]
            norm_wind_dir=[]
            for i in r:
                print("temp",i['main']['temp'])
                temp.append(i['main']['temp'])
                
            for i in r:
                print("wind",i['wind']['speed'])
                wind_speed.append(i['wind']['speed'])
            for i in r:
                print ("direction", i['wind']['deg'])
                wind_direc.append(i['wind']['deg'])

            for i in r:
                print ("date_time", i['dt_txt'])
                date_time.append(i['dt_txt'])    
                
            final_df["Temprature (C)"] = temp
            final_df["Wind Speed (m/s)"] = wind_speed
            final_df['Wind Direction (deg)']=wind_direc
            final_df['Date Time']=date_time
            print(final_df)
            for i in final_df.itertuples():
                print(i)
                #print ((i.wind_speed- wind_speed_mean) /wind_speed_std) 
                norm_wind_speed.append((i._2- wind_speed_mean) /wind_speed_std)
            for i in final_df.itertuples():
                norm_wind_dir.append((i._3 -wind_direction_mean)/wind_dir_std)

            norm_data['speed'] =norm_wind_speed     
            norm_data['dir']= norm_wind_dir

            prediction = model.predict(norm_data)
            print (prediction)    
            final_df["Active Power (kW)"] = prediction
            current_temp=final_df.at[1,"Temprature (C)"]
            current_date_time= datetime.datetime.now()
            max_df = pd.DataFrame()
            
            max_dt=[]
            max_prediction=[]
            for i in final_df.itertuples():
            
                if((i._5)>=600.0):
                    print(i)
                    max_dt.append(i._4)
                    print("max_dt",max_dt)
                    max_prediction.append(i._5)
                           
            print(max_dt)
            print(max_prediction)
            max_df["Maximum Active Power (kW)"] = max_prediction
            max_df['Date Time']= max_dt
            max_df.head() 
          

            #temprature v/s predicted power   
            plt.bar(final_df["Temprature (C)"],final_df['Active Power (kW)'] )
            plt.xlabel("Temprature (C)") 
            plt.ylabel("Predicted Power")
            plt.title('Temprature  v/s Predicted Power')
            plt.savefig('assets/date_time_powernew.png')
            plt.clf()
            
            
            plt.bar(final_df['Wind Speed (m/s)'],final_df['Active Power (kW)'] )
            plt.xlabel("Wind Speed (m/s)")
            plt.ylabel("Predicted Power")
            plt.title('Wind Speed  v/s Predicted Power')
            
            
            plt.savefig('assets/wind_speed_powernew.png')
            plt.clf()
            #import matplotlib.pyplot as plt2
    
            plt.bar(final_df['Wind Direction (deg)'],final_df['Active Power (kW)'] )
            plt.xlabel("Wind Direction (deg)")
            plt.ylabel("Predicted Power")
            plt.title('Wind Direction  v/s Predicted Power')
            
            plt.savefig('assets/wind_direction_powernew.png')
            plt.clf()
          
            
            

            html_table=final_df.to_html(index=True,classes="w3-table w3-striped w3-bordered  ")
        
        
            #sms=client.messages.create(
             #       from_="+12056515710",
              #      body=current_date_time,
               #     to="+916265925056",
            #)
            #print(sms.sid)
            try:
            
                five_table=max_df.head(8).to_html(index=False,classes="w3-table w3-striped w3-bordered ")
                string = str(max_dt[0])
                date = datetime.datetime.strptime(string, "%Y-%m-%d  %H:%M:%S")

                text =city+"will get"+  "Maximum output active Power of "+str(int(max_prediction[0]))+"kilo watt at"+ " " +str(date)
                print ('text',text)
                #sp= gTTS(text = text, lang = language, slow= False)
                #sp.save(audio)
                #playsound(audio) 
                #os.remove(audio)
            except:
                text ="There is no Such time in upcoming 5 Days for getting maximum output power in "
                #sp  =  gTTS(text = 'There is no Such time in upcoming 5 Days for getting maximum output power in '+city, lang = language, slow= False)
                #sp.save(audio)
                #playsound(audio) 
                #os.remove(audio)
            
            #print ('max_dt', max_dt)
            #text = max_dt[0] + "WIth power"+max_prediction[0] 
            #print ('Text', text)                     
            
            
            return render(request, 'table.html', {
                'html_table': html_table,'cityo':city,'data':uri,'five_table':five_table,'current_temp':current_temp,'current_date_time':current_date_time
            })
            

         

            
        else:
            print("city not found")
    return render(request,"ui.html")
def curr(request):
    number= request.POST.get('number')
    print(number)
    g = geocoder.ip('me')
    print(g.latlng)
    coordinates = g.latlng
    result = rg.search(coordinates) 
    result = (result[0].items())
    name = []
    for i in result:
        #print (i[1])
        name.append(i[1])
    print (name[2])

 
    city = name[2]
  
 
    url="http://api.openweathermap.org/data/2.5/forecast?q={}&appid=d55d5d4915b255b333b029be932d96ec"
    
    r=requests.get(url.format(city)).json()
    print(r)
    #r=requests.get(url).json()
    if(city==None):
        return render(request,"ui.html")
    else:
        if(r.get('cod')=='200'):
            r = (r['list'])

            final_df = pd.DataFrame()
            temp= []
            wind_speed=[]
            wind_direc=[]
            date_time=[]
            norm_wind_speed=[]
            norm_wind_dir=[]
            for i in r:
                print("temp",i['main']['temp'])
                temp.append(i['main']['temp'])
                
            for i in r:
                print("wind",i['wind']['speed'])
                wind_speed.append(i['wind']['speed'])
            for i in r:
                print ("direction", i['wind']['deg'])
                wind_direc.append(i['wind']['deg'])

            for i in r:
                print ("date_time", i['dt_txt'])
                date_time.append(i['dt_txt'])    
                
            final_df["Temprature (C)"] = temp
            final_df["Wind Speed (m/s)"] = wind_speed
            final_df['Wind Direction (deg)']=wind_direc
            final_df['Date Time']=date_time
            print(final_df)
            for i in final_df.itertuples():
                print(i)
                #print ((i.wind_speed- wind_speed_mean) /wind_speed_std) 
                norm_wind_speed.append((i._2- wind_speed_mean) /wind_speed_std)
            for i in final_df.itertuples():
                norm_wind_dir.append((i._3 -wind_direction_mean)/wind_dir_std)

            norm_data['speed'] =norm_wind_speed     
            norm_data['dir']= norm_wind_dir

            prediction = model.predict(norm_data)
            print (prediction)    
            final_df["Active Power (kW)"] = prediction
            max_df = pd.DataFrame()
            
            max_dt=[]
            max_prediction=[]
            for i in final_df.itertuples():
            
                if((i._5)>=600.0):
                    print(i)
                    max_dt.append(i._4)
                    print("max_dt",max_dt)
                    max_prediction.append(i._5)
            print(max_dt)
            print(max_prediction)
            max_df["Maximum Active Power (kW)"] = max_prediction
            max_df['Date Time']= max_dt
            max_df.head() 

            current_temp=final_df.at[1,"Temprature (C)"]
            current_date_time= datetime.datetime.now()
            #temprature v/s predicted power   
            plt.bar(final_df["Temprature (C)"],final_df['Active Power (kW)'] )
            plt.xlabel("Temprature (C)")
            plt.ylabel("Predicted Power")
            plt.title('Temprature  v/s Predicted Power')
            plt.savefig('assets/date_time_powernew.png')
            plt.clf()
            
            
            plt.bar(final_df['Wind Speed (m/s)'],final_df['Active Power (kW)'] )
            plt.xlabel("Wind Speed (m/s)")
            plt.ylabel("Predicted Power")
            plt.title('Wind Speed  v/s Predicted Power')
        
            
            plt.savefig('assets/wind_speed_powernew.png')
            plt.clf()
            
    
            plt.bar(final_df['Wind Direction (deg)'],final_df['Active Power (kW)'] )
            plt.xlabel("Wind Direction (deg)")
            plt.ylabel("Predicted Power")
            plt.title('Wind Direction  v/s Predicted Power')
            
            plt.savefig('assets/wind_direction_powernew.png')
            plt.clf()
    
           
            html_table=final_df.to_html(index=True,classes="w3-table w3-striped w3-bordered  ")
            five_table=max_df.head(8).to_html(index=False,classes="w3-table w3-striped w3-bordered ")
           
          #  sms=client.messages.create(
            #         from_="+12056515710",
           #          body=current_date_time,
             #    to="+916265925056",
             #)
            #print(sms.sid)
            try:
            
                five_table=max_df.head(8).to_html(index=False,classes="w3-table w3-striped w3-bordered ")
                string = str(max_dt[0])
                date = datetime.datetime.strptime(string, "%Y-%m-%d  %H:%M:%S")

                text = city+"will get"+ "Maximum output active Power of "+str(int(max_prediction[0]))+"kilo watt at"+ " " +str(date)
                print ('text',text)
                #sp= gTTS(text = text, lang = language, slow= False)
                #sp.save(audio)
                #playsound(audio) 
                #os.remove(audio)
            except:
                text = 'There is no Such time in upcoming 5 Days for getting maximum output power in '+city
                #sp  =  gTTS(text = 'There is no Such time in upcoming 5 Days for getting maximum output power in '+city, lang = language, slow= False)
                #sp.save(audio)
                #playsound(audio) 
                #os.remove(audio)
           
            return render(request, 'table.html', {
                'html_table': html_table,'cityo':city,'five_table':five_table,'current_temp':current_temp,'current_date_time':current_date_time
            })
        else:
            print("city not found")
    return render(request,"ui.html")
   

def maint(request):
    return render(request,"maintaince.html")
def graph(request):
    return render(request,"graph.html")
