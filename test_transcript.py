# test_transcript.py

from youtube_transcript_api import YouTubeTranscriptApi

video_id = "kqtD5dpn9C8"

try:
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)

    print("SUCCESS")

    for item in transcript[:5]:
        print(item.text)

except Exception as e:
    print("ERROR:")
    print(e)