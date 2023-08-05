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
    program_description="midi visualizer"
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
    parser.add_argument(
        "-outlined",
        required=True,
        default="yes",
        help="outlined or not (yes/no)"
    )
    parser.add_argument(
        "-pulse",
        required=True,
        default=30,
        help="pulse strength"
    )
    args = parser.parse_args()
    convert(args.fps, args.input_path, args.output_path, args.bg_color, args.fg_color, args.outlined, args.pulse)

def convert(fps, input_path, output_path, bg_color, fg_color, outlined, pulse):
    clock = pygame.time.Clock()

    outline = True
    if outlined.lower() == "no":
        outline = False

    if pulse < 0:
        pulse = 0

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

    last_time = 0

    screen_width = 480
    screen_height = 480
    screen = pygame.Surface((screen_width, screen_height))

    for note in notes:
        note["anim"] = pulse

    play_time = 0

    for i in range(int(duration*fps)):
        screen.fill(bg_color)
        play_time += 1/fps

        for j, note in enumerate(notes):
            next_note = note
            if j+1 < len(notes):
                next_note = notes[j+1]
            if next_note["time"] >= play_time >= note["time"]:
                note["anim"] *= 0.7
                if outline:
                    border = (int(note["anim"]))
                    if border > 0:
                        pygame.draw.rect(screen, fg_color, [40+note["anim"]/2, 40+note["anim"]/2, 400-note["anim"], 400-note["anim"]], border)
                else:
                    pygame.draw.rect(screen, fg_color, [40+note["anim"]/2, 40+note["anim"]/2, 400-note["anim"], 400-note["anim"]])
            
        pygame.image.save(screen, f"temp_images_folder/{i}.png")

    video = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"XVID"), fps, (int(screen_width), int(screen_height)))

    for file in sorted(os.listdir("temp_images_folder"), key=len):
        image = cv2.imread(f"temp_images_folder/{file}")
        video.write(image)

    cv2.destroyAllWindows()
    video.release()

    print("done!")

main()