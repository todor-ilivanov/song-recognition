class Error:
    message = None

    def __init__(self, message): 
        self.message = message

class TextAnnotations:
    description = None

    def __init__(self, description): 
        self.description = description

class AnnotateImageResponse:
    text_annotations = []
    error = Error(None)

    def __init__(self, text_annotations): 
        self.text_annotations = text_annotations

class PlaylistsResponse:
    items = []
    
