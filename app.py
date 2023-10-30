import streamlit as st
from pytube import Search
from datetime import datetime
import re
import assemblyai as aai
from bardapi import Bard
from urllib.parse import urlparse, parse_qs
import requests
from streamlit_chat import message
def get_best_videos(search_words):
    # Search for videos
    s = Search(search_words)

    # Get a list of videos
    videos = s.results

    # Calculate ratings for each video based on duration, likes, views, and time till date
    current_time = datetime.now()
    ratings = []
    i = 7  # extract the top 7
    for video in videos:
        i -= 1
        if i == 0:
            break
        duration = video.length
        like_template = r'[0-9]{1,3},?[0-9]{0,3},?[0-9]{0,3} like'
        str_likes = re.search(like_template, str(video.initial_data)).group(0)
        likes = int(str_likes.split(' ')[0].replace(',', ''))
        views = video.views
        time_diff = (current_time - video.publish_date).total_seconds() / 60 / 60 / 24
        rating = duration * likes / (views * time_diff)
        ratings.append(rating)

    # Sort the videos based on ratings
    sorted_videos = [video for _, video in sorted(zip(ratings, videos), reverse=True)]

    # Get the best five URLs with ratings
    best_five_urls = []
    for i in range(min(5, len(sorted_videos))):
        url = sorted_videos[i].watch_url
        rating = ratings[i]
        best_five_urls.append((url, rating))

    return best_five_urls

# Streamlit app title
st.title("YouTube Video Search")

# Get user input
query = st.text_input("Enter the search query")
search_results=get_best_videos(query)
# Execute search
if st.button("Search"):
    # Perform search
    search_results = Search(query)

    # Display video results
    for video in search_results.results:
        st.write(f"{video.title}")
        st.write(f"Watch URL: {video.watch_url}")
        st.write("---")
    st.write("Best 5 youtube links")
    for i in range(len(search_results)):
        st.write(search_results[i])
        st.write("---")




# getting the summary for a youtube video
def extract_video_id(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    video_id = query_params.get('v', [''])[0]
    return video_id
# def generate_summary(transcription):
    # summary = bard.get_answer(f"Generate a 3-line summary of the transcription: {transcription}")['content']
    # return summary
aai.settings.api_key = "d5a2915d27cc461893771f33f92f7142"

def main():
    st.title("YouTube Video Transcription and Summary")
    
    # User input for YouTube URL
    youtube_url = st.text_input("Enter the YouTube URL:")
    
    # Generate Transcription Button
    if st.button("Generate Transcription"):
        if youtube_url:
            with st.spinner("Generating Transcription..."):
                # Extract video ID from YouTube URL
                video_id = extract_video_id(youtube_url)

            # Get video details using the API
                url = "https://ytstream-download-youtube-videos.p.rapidapi.com/dl"
                querystring = {"id": video_id}
                headers = {
                    "X-RapidAPI-Key": "708f853664mshd62777f5ab94cdcp1096a1jsnee73e9c6207d",
                    "X-RapidAPI-Host": "ytstream-download-youtube-videos.p.rapidapi.com"
                }
                response = requests.get(url, headers=headers, params=querystring)
                dictt = response.json()

                # Extract relevant information from the response
                final_dict = {}
                get_link = dictt['formats']
                downloadable_url = 0
                for i in get_link:
                    if i['qualityLabel'] == '144p' or i['qualityLabel'] == '360p':
                        downloadable_url = i['url']
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
                    final_dict['url'] = downloadable_url
                else:
                    st.write("Our API is down. Please try again later.")
                # st.write("our final_dict is ",final_dict)
                # Transcribe the video
                video = final_dict['url']
                transcriber = aai.Transcriber()
                transcript = transcriber.transcribe(video)
                transcribed_text = transcript.text


                st.write("transcribed_text is",transcribed_text)
        else:
            st.warning("Please enter a valid YouTube URL.")
    
    # Generate Summary Button
    if st.button("Generate Summary"):
        if youtube_url:
            with st.spinner("Generating Summary..."):
                # Your existing code for generating the summary goes here
                summary_text = "Sample summary text..."  # Replace with actual summary text
                st.write("Summary:")
                st.write(summary_text)
        else:
            st.warning("Please enter a valid YouTube URL.")

if __name__ == "__main__":
    main()