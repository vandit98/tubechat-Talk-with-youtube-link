from fastapi import FastAPI, HTTPException
from pytube import Search
from datetime import datetime
import re
import uvicorn
import assemblyai as aai
from urllib.parse import urlparse, parse_qs
import requests
from utils import extract_video_id
from db_utils import *
from gpt_utils import *
from flask_cors import CORS
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
aai.settings.api_key = "d5a2915d27cc461893771f33f92f7142"

# cors error removal

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=['*']
)

@app.get("/get_best_5_videos")
async def get_best_5_videos(search_words: str):
    # Search for videos
    s = Search(search_words)

    # Get a list of videos
    videos = s.results

    # Calculate ratings for each video based on duration, likes, views, and time till date
    current_time = datetime.now()
    ratings = []

    for video in videos:
        duration = video.length
        like_template = r'[0-9]{1,3},?[0-9]{0,3},?[0-9]{0,3} like'
        str_likes = re.search(like_template, str(video.initial_data)).group(0)
        likes = int(str_likes.split(' ')[0].replace(',', ''))
        views = video.views
        time_diff = (current_time - video.publish_date).total_seconds() / 60 / 60 / 24
        rating = duration * likes / (views * time_diff)
        ratings.append((video.watch_url, rating))

    # Sort the videos based on ratings in descending order
    sorted_videos = sorted(ratings, key=lambda x: x[1], reverse=True)

    # Get the best five URLs with ratings
    best_five_urls = sorted_videos[:5]

    return best_five_urls

# 2nd Api to get transcription and other results

@app.get("/generate_transcription_and&other_details")
async def generate_transcript_and_other_details(video_url: str):
    try:
        # Extract video ID from YouTube URL
        video_id = extract_video_id(video_url)
        if fetch_video_data_by_id(youtube_video_id=video_id):
            return fetch_video_data_by_id(youtube_video_id=video_id)

        url = "https://ytstream-download-youtube-videos.p.rapidapi.com/dl"
        querystring = {"id": video_id}
        headers = {
            "X-RapidAPI-Key": "708f853664mshd62777f5ab94cdcp1096a1jsnee73e9c6207d",
            "X-RapidAPI-Host": "ytstream-download-youtube-videos.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        dictt = response.json()

        final_dict = {}
        downloadable_links=[]
        get_link = dictt['formats']
        for i in dictt['formats']:
            quality_label = i.get('qualityLabel', '')
            url = i.get('url', '')
            downloadable_links.append({quality_label: url})
        for i in get_link:
            if i['qualityLabel'] == '144p' or i['qualityLabel'] == '360p':
                downloadable_url_min_quality = i['url']
        if dictt['status'] == 'OK':
            try:
                final_dict['id'] = dictt['id']
            except:
                final_dict['id'] = None
            try:
                final_dict['title'] = dictt['title']
            except:
                final_dict['title'] = None
            try:
                final_dict['lengthSeconds'] = dictt['lengthSeconds']
            except:
                final_dict['lengthSeconds'] = None
            try:
                final_dict['keywords'] = dictt['keywords']
            except:
                final_dict['keywords'] = None
            try:
                final_dict['channelTitle'] = dictt['channelTitle']
            except:
                final_dict['channelTitle'] = None
            try:
                final_dict['description'] = dictt['description']
            except:
                final_dict['description'] = None
            try:
                final_dict['thumbnail_link'] = dictt['thumbnail'][-1]['url']
            except:
                final_dict['thumbnail_link'] = None
            final_dict['min_quality_url'] = downloadable_url_min_quality
            final_dict["all_urls"]=downloadable_links

        else:
            return {"error": "API is down. Please try again later."}

        video = final_dict['min_quality_url']
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(video)
        transcribed_text = transcript.text

        # Generate the summary (You need to implement this part)
        summary_text = "Sample summary text..."  # Replace with your actual summary generation code
        final_dict["transcribed_text"] = transcribed_text
        final_dict["summary_text"] = summary_text
        # return {"transcribed_text": transcribed_text, "summary_text": summary_text}
        insert_video_data(final_dict)
        return final_dict
    except Exception as e:
        return {"error": str(e)}


@app.post("/generate_summary")
async def generate_summary(video_url: str):
    result_dict = await generate_transcript_and_other_details(video_url)  # await here
    print("*"*100)
    # call gpt function to generate summary
    # summary = await get_response(model="gpt-3.5-turbo-16k", query="generate a summary for the given context", context=result_dict['transcribed_text'])
    summary=get_response(model="gpt-3.5-turbo-16k", query="generate a summary for the this video", context=result_dict['transcribed_text'])
    # summary = summary_generator(result_dict['transcribed_text'])
    print(summary)
    return {"summary": summary}

@app.post("/Qna_talk")
async def normal_talk(query: str, video_url: str):
    result_dict = await generate_transcript_and_other_details(video_url)
    print("*" * 100)
    summary = get_response(model="gpt-3.5-turbo-16k", query=query, context=result_dict['transcribed_text'])
    
    return {"Bot_response": summary}

@app.get("/check-url")
async def check_url(video_url: str):
    try:
        # Extract video ID from YouTube URL
        video_id = extract_video_id(video_url)
        if fetch_video_data_by_id(youtube_video_id=video_id):
            return "Video Present in Database"
        else:
            return "Video not present in database"
    except Exception as e:
        return {"error": str(e)}