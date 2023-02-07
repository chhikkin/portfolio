#!/usr/bin/env python
# coding: utf-8


#import needed libraries
import requests
import pandas as pd
from pandas.io import gbq
import time as t




#define API key and channel id of Le Sserafim's youtube channel
api_key = 'AIzaSyB3x8NXaGA-5kHyWY6If1h7LRPcOIoD84M'
channel_id = 'UCs-QBT4qkj_YiQw1ZntDO3g'



#make empty dataframe using pandas
info_df = pd.DataFrame(columns=['Id','Title','Published_Date','Published_Time','View_Count','Like_Count','Comment_Count'])




#function to get channel's statistics such as view, like and comment count
def get_stats():
    stats_link = 'https://www.googleapis.com/youtube/v3/videos'
    stats_params = {'key': api_key,
                    'id': videoId,
                    'part': 'statistics',
                    'order':'date'}
    stats_response= requests.get(stats_link, params=stats_params).json()
    stats = stats_response['items'][0]['statistics']
    view = stats['viewCount']
    like = stats['likeCount']
    comment = stats['commentCount']
    return view, like, comment




#request channel data from Youtube Data API
link = 'https://www.googleapis.com/youtube/v3/search'
params = {'key': api_key,
          'channelId': channel_id,
          'part': 'snippet', #snippet contains data needed for this project such as title, published datetime and video ID
          'maxResults': 1000,
          'order':'date'}
response = requests.get(link, params=params).json()
videos = response['items']
try:
    page_token = response['nextPageToken'] #request is limited to only 50 videos, nextPageToken needed as parameter to access more videos
except KeyError:
    page_token = None

#append data row by row into pandas dataframe
for vid in videos:
    if vid['id']['kind']== 'youtube#video':
        channelId = vid['snippet']['channelId']
        title = vid['snippet']['title']
        videoId = vid['id']['videoId']

        publishedAt = vid['snippet']['publishedAt'].split('T')
        date = publishedAt[0]
        time = publishedAt[1].split('Z')[0]
        view, like, comment = get_stats()
        info_df=info_df.append({'Id':videoId,'Title':title,'Published_Date':date,'Published_Time':time,'View_Count':view,'Like_Count':like,'Comment_Count':comment}, ignore_index=True)

#next page, more videos
while page_token:
    link = 'https://www.googleapis.com/youtube/v3/search'
    params = {'key': api_key,
              'channelId': channel_id,
              'part': 'snippet',
              'maxResults': 1000,
              'pageToken': page_token,
              'order':'date'}
    response = requests.get(link, params=params).json()
    t.sleep(5)
    videos = response['items']
#continue to append data in next page row by row into pandas dataframe
    for vid in videos:
        if vid['id']['kind']== 'youtube#video':
            channelId = vid['snippet']['channelId']
            title = vid['snippet']['title']
            videoId = vid['id']['videoId']

            publishedAt = vid['snippet']['publishedAt'].split('T')
            date = publishedAt[0]
            time = publishedAt[1].split('Z')[0]
            view, like, comment = get_stats() 
            info_df=info_df.append({'Id':videoId,'Title':title,'Published_Date':date,'Published_Time':time,'View_Count':view,'Like_Count':like,'Comment_Count':comment}, ignore_index=True)
            t.sleep(5)
    try:
        page_token = response['nextPageToken']
    except KeyError:
        break




#change data type from string to the appropriate data type
info_df['Published_Date'] = info_df['Published_Date'].astype('datetime64')
info_df['Published_Time'] = info_df['Published_Time'].astype('datetime64')
info_df['View_Count'] = info_df['View_Count'].astype('int64')
info_df['Like_Count'] = info_df['Like_Count'].astype('int64')
info_df['Comment_Count'] = info_df['Comment_Count'].astype('int64')





#import to bigquery table
info_df.to_gbq(destination_table='api-project-375215.lesserafim_yt.ft_statistics',
              project_id='api-project-375215',
              if_exists='replace')





#request data for subscriber and view count
subs_link = 'https://www.googleapis.com/youtube/v3/channels'
subs_params = {'key': api_key,
          'id': channel_id,
          'part': 'statistics'}
subs_response = requests.get(subs_link, params=subs_params).json()




#get data and append to pandas dataframe
subs=subs_response['items'][0]['statistics']['subscriberCount']
vid_count=subs_response['items'][0]['statistics']['videoCount']
cinfo_df = pd.DataFrame(columns=['Datetime','Subscriber_Count','Video_Count'])
cinfo_df=cinfo_df.append({'Datetime':pd.to_datetime('today').date(),'Subscriber_Count':subs,'Video_Count':vid_count}, ignore_index=True)
#change data type from string to the appropriate data type
cinfo_df['Datetime']=cinfo_df['Datetime'].astype('datetime64')
cinfo_df['Subscriber_Count']=cinfo_df['Subscriber_Count'].astype('int64')
cinfo_df['Video_Count']=cinfo_df['Video_Count'].astype('int64')




#import to bigquery table
cinfo_df.to_gbq(destination_table='api-project-375215.lesserafim_yt.channel_info',
              project_id='api-project-375215',
              if_exists='replace')

