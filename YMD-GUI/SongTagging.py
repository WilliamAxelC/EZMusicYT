import eyed3

def tag_song(temp_title, temp_author, thumbnail_path, mp3_path):
    try:
        audiofile = eyed3.load(mp3_path)
        with open(thumbnail_path, "rb") as image_file:
            imagedata = image_file.read()
        clear_existing_tags(audiofile)
        audiofile.tag.images.set(3, imagedata, "image/jpeg", u"Cover")
        audiofile.tag.artist = temp_author
        audiofile.tag.title = temp_title
        audiofile.tag.save(max_padding=1)
        print(f"Song tagged: {temp_title}")
    except Exception as e:
        print(f"Failed to tag song: {e}")

def clear_existing_tags(audiofile):
    audioImageDescriptions = [audioImage.description for audioImage in audiofile.tag.images]
    for description in audioImageDescriptions:
        audiofile.tag.images.remove(description)
