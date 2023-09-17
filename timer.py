import pygame
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
        "--duration",
        required=True,
        type=float,
        help="duration of video (in seconds)"
    )
    parser.add_argument(
        "--output_path",
        required=True,
        widget="FileSaver",
        gooey_options = dict(wildcard="mp4|*.mp4"),
        help="path of output video"
    )
    parser.add_argument(
        "--font_path",
        required=True,
        widget="FileChooser",
        gooey_options = dict(wildcard="ttf|*.ttf"),
        help="path of font of text"
    )
    args = parser.parse_args()
    convert(args.fps, args.duration, args.output_path, args.font_path)

def convert(fps, duration, output_path, font_path):
    font = pygame.font.Font(font_path, 100)

    def draw_text(display, text, x, y, color="#000000", font=font):
        render = font.render(text, True, color)
        display.blit(render, (x, y))

    screen_width = 480
    screen_height = 120
    screen = pygame.Surface((screen_width, screen_height))

    counter = 0 
    play_time = 0

    last_time = 0

    for i in range(int(duration*fps)):
        screen.fill("#ffffff")
        play_time += 1/fps

        m, s = divmod(play_time, 60)
        draw_text(screen, f"{int(m)}:{round(s, 1)}", 10, 0)

        counter += 1
        pygame.image.save(screen, f"temp_images_folder/{counter}.png")

    video = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"XVID"), fps, (int(screen_width), int(screen_height)))

    for file in sorted(os.listdir("temp_images_folder"), key=len):
        image = cv2.imread(f"temp_images_folder/{file}")
        video.write(image)  

    cv2.destroyAllWindows()
    video.release()

    print("done!") 

main()