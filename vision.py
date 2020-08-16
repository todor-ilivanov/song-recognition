def extract_song_name(path):
    """Detects text in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    texts = response.text_annotations
    # TODO: Test and handle errors
    texts_descr = texts[0].description.split('\n')
    song = ''.join([text for text in texts_descr if "It's" in text])

    return song[5:].replace('by ', '')