import json

def split_transcription(transcription):
    buffer = ""
    chunks = []

    for char in transcription:
        buffer += char

        if len(buffer) >= 350 and char in {'.', '!', '?'}:
            chunks.append(buffer.strip())
            buffer = ""

    if buffer:
        chunks.append(buffer.strip())

    return chunks

with open('./tools/json/raw.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

new_contents = []
current_video_sequence = 0
sequence_counter = 0

for content in data['contents']:
    if content["type_content"] == "video":
        current_video_sequence = content["sequence"]
        new_contents.append({
            "type_content": content["type_content"],
            "content": content["content"],
            "topic_reference": content["topic_reference"],
            "sequence": current_video_sequence
        })
        sequence_counter = current_video_sequence + 1
    elif content["type_content"] == "transcription":
        transcription_chunks = split_transcription(content["content"])
        for chunk in transcription_chunks:
            new_contents.append({
                "type_content": "transcription",
                "content": chunk,
                "topic_reference": content["topic_reference"],
                "sequence": sequence_counter
            })
            sequence_counter += 1

data['contents'] = new_contents
with open('tmp.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("Data processed and saved to data1.json.")
