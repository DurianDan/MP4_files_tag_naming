from geopy.geocoders import Nominatim
from geopy.point import Point
import gpxpy.gpx
from glob import glob
from os import path
from datetime import timedelta, datetime
import shutil
from os import mkdir
import csv

def tag_time(file):
    '''return a dict with 'day','weekday','year','month','time','date_time'object of a file'''
    ctime = path.getctime(file)
    start_datetime = datetime.fromtimestamp(ctime)
    from moviepy import editor
    fileMP4 = editor.VideoFileClip(file)
    dur = fileMP4.duration
    time_change = timedelta(seconds = dur, hours = 7)
    end_datetime = start_datetime + time_change
    return_dict = {"day":start_datetime.strftime("%d"),"weekday":start_datetime.strftime("%a"),"year":start_datetime.strftime("%Y"),"month":start_datetime.strftime("%b"),'time':start_datetime.strftime("%X"),"end_datetime":end_datetime,"start_datetime":start_datetime}
    return return_dict    
def tag_weather(csvfile_dirs:list,starttime:datetime,endtime:datetime):
    weather_tag = set()
    for file in csvfile_dirs:
    #make a list of datetime to compare
        startdatecompare = starttime.strftime("%m")+"/"+starttime.strftime("%d")+"/"+starttime.strftime("%Y")
        with open(file,"r") as csvfile:
            handle = csv.reader(csvfile)
            fields = next(handle)
            list_weather_index = list(handle)
        for i in list_weather_index:
            if startdatecompare[:10 ]== i[1][:10] and endtime.strftime("%X") >i[1][10:] and starttime.strftime("%X") < i[1][10:]:
                weather_tag.add(i[4]+"°C")
                weather_tag.add(i[10]+"kph")
                weather_tag.add(i[13]+'km')
                weather_tag.add(i[14]+"cc%")
                weather_tag.add(i[15]+"%")
                weather_tag.add(i[16]+":w")
    return weather_tag
def tag_place_speed(GPX_files:list,start_datetime:datetime,end_datetime:datetime):
    listpoints = []
    listpoints_mis = []
    speed = []
    place_tag = set()
    return_dict = {}
    for file in GPX_files:
        gpx_file = open(file, 'r') 
        gpx = gpxpy.parse(gpx_file)
        for track in gpx.tracks: 
            for segment in track.segments: 
                for i in range(len(segment.points)):
                    point = segment.points[i]
                    pointdate = point.time.strftime("%x")
                    filedate = start_datetime.strftime("%x")
                    pointtime = point.time.strftime("%X")
                    file_endtime = end_datetime.strftime("%X")
                    file_starttime = start_datetime.strftime("%X")
                    if pointdate == filedate and pointtime >= file_starttime and pointtime <= file_endtime:
                            listpoints.append(point)
                    else:
                        listpoints_mis.append(point)
    if listpoints != []:
        for i in range(len(listpoints)):
            speed.append(listpoints[i].speed_between(listpoints[i-1]))
            if i == 0 or i == (len(listpoints)-1) or i == (len(listpoints)-1)/2 or i == len(listpoints)/2:
                geolocator = Nominatim(user_agent="gopro")
                location = geolocator.reverse(Point(listpoints[i].longitude,listpoints[i].latitude),language="en")
                place_tag.add(location.raw["address"]["road"])
                place_tag.add(location.raw["address"]["suburb"])
        return_dict = {"max_speed": "mxspd "+str(5*(round(max(speed)/5))),"average_speed":"avrgspd "+str(5*(round((sum(speed)/len(speed))/5)))}
        place_tag = list(place_tag)
        for i in range(len(place_tag)):
            return_dict.update({"place_tag_"+str(i):place_tag[i]})
    else:
        for i in range(len(listpoints_mis)):
            speed.append(listpoints_mis[i].speed_between(listpoints_mis[i-1]))
            if i == 0 or i == (len(listpoints_mis)-1) or i == (len(listpoints_mis)-1)/2 or i == len(listpoints_mis)/2:
                geolocator = Nominatim(user_agent="gopro")
                location = geolocator.reverse(Point(listpoints_mis[i].latitude,listpoints_mis[i].longitude),language="en")
                place_tag.add(location.raw["address"]["road"])
                place_tag.add(location.raw["address"]["suburb"])
        return_dict = {"max_speed": "mxspd "+str(5*(round(max(speed)/5))),"average_speed":"avrgspd "+str(5*(round((sum(speed)/len(speed))/5)))}
        place_tag = list(place_tag)
        for i in range(len(place_tag)):
            return_dict.update({"place_tag_"+str(i):place_tag[i]})
    return return_dict
def copy(MP4_files,GPX_files:list,weather_csv_files:list):
    for direct in MP4_files:
        tim_e = tag_time(direct)
        plac_e = tag_place_speed(GPX_files,tim_e["start_datetime"],tim_e["end_datetime"])
        weath_r = tag_weather(weather_csv_files,tim_e["start_datetime"],tim_e["end_datetime"])
        folder_datetime = "/home/duriandan/GOPRO/"+str(tim_e['year'])+","+str(tim_e['month'])+","+str(tim_e["day"])
        if not path.isdir(folder_datetime):
            mkdir(folder_datetime)
        tags = [tim_e["year"],tim_e["month"],tim_e["day"],tim_e["weekday"],tag_time(direct)["time"]]
        for i in weath_r:
            tags.append(weath_r[i])
        for i in plac_e:
            tags.append(plac_e[i])
        target_dir = folder_datetime+"/"
        for tag in tags:
            comma =","
            if tags[-1] == tag:
                comma = ".MP4"
            target_dir += tag+comma
        shutil.copyfile(direct,target_dir)

MP4_files = glob("/home/duriandan/GOPRO/unfiltered/*")
GPX_files = glob("/home/duriandan/GOPRO/GPX_GPS/*")
csv_files = glob("/home/duriandan/GOPRO/csv_weather/*")
test2 = copy(MP4_files,GPX_files,csv_files)