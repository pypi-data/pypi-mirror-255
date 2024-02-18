from youtube_transcript_api import (
    YouTubeTranscriptApi as Api,
    TranscriptsDisabled,
    NoTranscriptFound,
    CouldNotRetrieveTranscript,
    VideoUnavailable,
    NotTranslatable,
    TranslationLanguageNotAvailable,
    NoTranscriptAvailable,
    CookiePathInvalid,
    CookiesInvalid
)


class Extractor:
    def __init__(self, videi_id, callback=None):
        self.video_id = videi_id
        self.callback = callback

    def extract(self) -> dict:
        try:
            transcript_list = Api.list_transcripts(self.video_id)
            for transcript in transcript_list:
                # transcripts = Api.get_transcript(self.video_id)
                return transcript.fetch()
        except (TranscriptsDisabled,
                NoTranscriptFound,
                CouldNotRetrieveTranscript,
                VideoUnavailable,
                NotTranslatable,
                TranslationLanguageNotAvailable,
                NoTranscriptAvailable) as err:
            print(err.__class__)
            print("Transcripts unavailable.")
            
            return [{"error": 1}]
        except Exception as err:
            print("[OUTER EXCEPTION]" + str(type(err)), str(err)[:80])
            return [{"error": 3}]
        
    def cancel(self):
        pass
