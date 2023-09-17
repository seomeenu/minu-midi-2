import pygame
import sys
import json 
import cv2
import os
import shutil
from gooey import Gooey, GooeyParser

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
        "-f",
        "--font_path",
        required=True,
        widget="FileChooser",
        gooey_options = dict(wildcard="ttf|*.ttf"),
        help="path of font of text"
    )
    parser.add_argument(
        "--bg_color",
        required=True,
        default="#000000",
        help="bg color (in hex)"
    )
    parser.add_argument(
        "--fg_color",
        required=True,
        default="#ffffff",
        help="fg color (in hex)"
    )
    parser.add_argument(
        "--movement",
        required=True,
        default=20,
        type=float,
        help="strength of the movement"
    )
    args = parser.parse_args()
    convert(args.fps, args.input_path, args.output_path, args.font_path, args.bg_color, args.fg_color, args.movement)

def convert(fps, input_path, output_path, font_path, bg_color, fg_color, movement):
    font = pygame.font.Font(font_path, 200)

    def draw_text(display, text, x, y, color=fg_color, font=font):
        render = font.render(text, True, color)
        display.blit(render, (x-render.get_width()/2, y-render.get_height()/2))
        
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

    screen_width = 480
    screen_height =  480
    # screen_height = min(dist*height+100, 720)
    screen = pygame.Surface((screen_width, screen_height))
    
    play_time = 0

    for note in notes:
        note["anim"] = movement 

    for i in range(int(duration*fps)):
        screen.fill(bg_color)
        play_time += 1/fps

        for j, note in enumerate(notes):
            next_note = note
            if j+1 < len(notes):
                next_note = notes[j+1]
            if next_note["time"] >= play_time >= note["time"]:
                note["anim"] *= 0.8
                draw_text(screen, note["name"], 480/2, 480/2+note["anim"])
                    
        pygame.image.save(screen, f"temp_images_folder/{i}.png")

    video = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"XVID"), fps, (int(screen_width), int(screen_height)))

    for file in sorted(os.listdir("temp_images_folder"), key=len):
        image = cv2.imread(f"temp_images_folder/{file}")
        video.write(image)

    cv2.destroyAllWindows()
    video.release()

    print("done!")

main()