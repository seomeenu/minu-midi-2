import pygame
import sys
import json 
import cv2
import os
import shutil
from gooey import Gooey, GooeyParser

pygame.init()

pygame.init()
if os.path.exists("temp_images_folder"):
    shutil.rmtree("temp_images_folder")
os.mkdir("temp_images_folder")

@Gooey(
    program_name="minu midi 2",
    program_description="midi visualizera"
)
def main():
    parser = GooeyParser()
    parser.add_argument(
        "--fps",
        default=30,
        type=float,
        required=True,
        help="framerate of video"
    )
    parser.add_argument(
        "-o",
        "--output_path",
        required=True,
        widget="FileSaver",
        gooey_options = dict(wildcard="mp4|*.mp4"),
        help="path of output video"
    )
    parser.add_argument(
        "-i",
        "--input_path",
        required=True,
        widget="FileChooser",
        gooey_options = dict(wildcard="json|*.json"),
        help="path of input json"
    )
    parser.add_argument(
        "-bg_color",
        required=True,
        default="#000000",
        help="bg color (in hex)"
    )
    parser.add_argument(
        "-fg_color",
        required=True,
        default="#ffffff",
        help="fg color (in hex)"
    )
    args = parser.parse_args()
    convert(args.fps, args.input_path, args.output_path, args.bg_color, args.fg_color)

def convert(fps, input_path, output_path, bg_color, fg_color):
    clock = pygame.time.Clock()

    bpm = 120
    notes = []
    duration = 0
    with open(input_path) as file:
        data = json.load(file)
        bpm = data["header"]["bpm"]
        track_index = 0
        #finds the track with notes
        for i, track in enumerate(data["tracks"]):
            if track["notes"] != []:
                track_index = i
        notes = data["tracks"][track_index]["notes"]
        duration = data["duration"]

    bar_duration = 60/bpm*16
    last_time = 0

    max_note = max(notes, key=lambda x: x["midi"])["midi"]
    min_note = min(notes, key=lambda x: x["midi"])["midi"]
    middle = (max_note+min_note)//2
    height = 10
    dist = max_note-min_note

    screen_width = bar_duration*100+210
    screen_height = min(dist*height+100, 720)
    screen = pygame.Surface((screen_width, screen_height))

    for note in notes:
        note["anim"] = 25

    play_time = 0
    offset = 0
    offset_vel = 0
    scroll = -bar_duration*100

    for i in range(int(duration*fps)):
        screen.fill(bg_color)
        play_time += 1/fps

        for note in notes:
            if play_time >= note["time"]:
                if bar_duration*100-10 >= note["time"]*100-scroll >= -10:
                    note["anim"] *= 0.7
                    pygame.draw.rect(screen, fg_color, 
                        [
                            note["time"]*100+100-note["anim"]/4-scroll-offset,
                            (middle-note["midi"])*height+screen_height/2,
                            note["duration"]*100-note["anim"]/6,
                            10
                        ]
                    )
        
        if play_time >= last_time:
            last_time += bar_duration
            offset = 100 
            scroll += bar_duration*100

        if play_time >= last_time-bar_duration/15.7:
            offset -= offset_vel/20
            offset_vel *= 1.7
        else:
            offset_vel = 1

        offset *= 0.9
        
        pygame.image.save(screen, f"temp_images_folder/{i}.png")

    video = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"XVID"), fps, (int(screen_width), int(screen_height)))

    for file in sorted(os.listdir("temp_images_folder"), key=len):
        image = cv2.imread(f"temp_images_folder/{file}")
        video.write(image)

    cv2.destroyAllWindows()
    video.release()

    print("done!")

main()