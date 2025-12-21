import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import matplotlib.text as text
import matplotlib.image as mpimg
import random

import csv
import os

def add_image(filepath, bounds):
    image = mpimg.imread(filepath)
    plt.imshow(image, extent=bounds)

def load_images():
    with open(os.path.join("images", "image_info.csv"), "r") as file:
        reader = csv.reader(file)
        for row in reader:
            filepath = os.path.join("images", row[0])
            x_left = float(row[1])
            x_right = float(row[2])
            y_bottom = float(row[3])
            y_top = float(row[4])
            add_image(filepath, (x_left, x_right, y_bottom, y_top))

# gets x, y coords at each frame from a csv file
def get_frames_from_csv(filepath):
    frame_list = []
    with open(filepath, "r") as file:
        reader = csv.reader(file)
        header = next(reader)
        name = header[0]
        color = int(header[1])
        for row in reader:
            frame_list.append([int(float(row[0])), int(float(row[1]))])

    return frame_list, name, color

# gets x, y coords at each frame from multiple players listed in target folder
def get_all_frames(filepath):
    csv_paths = os.listdir(filepath)
    total_frame_list = []
    name_list = []
    color_list = []
    for path in csv_paths:
        frames, name, color = get_frames_from_csv((os.path.join(filepath, path)))
        total_frame_list.append(frames)
        name_list.append(name)
        color_list.append(color)

    return total_frame_list, name_list, color_list

# redraws at each frame to incorporate new positions of each player and the camera
def draw_frame(frame, frame_list, spectate_index, player_list):
    for i in range(0, len(player_list)):
        if frame < len(frame_list[i]):
            x = frame_list[i][frame][0]
            y = frame_list[i][frame][1]
        else:
            x = frame_list[i][-1][0]
            y = frame_list[i][-1][1]

        player_list[i].set_xy((x, y))
        text_list[i].set_position((x+15, y+50))
        if i == spectate_index:
            ax.set_xlim(x-192, x+192)
            ax.set_ylim(y-56, y+160)

    # for blitting
    artist_list = player_list[:]
    artist_list += text_list[:]
    artist_list.append(ax)
    return artist_list

matplotlib.rcParams["animation.ffmpeg_path"] = "/usr/bin/ffmpeg"
matplotlib.rcParams["figure.facecolor"] = "black"
matplotlib.rcParams["axes.facecolor"] = "black"
# get the outline and values for each frame

frame_list, name_list, color_list = get_all_frames("frames")
spectate_index = name_list.index("TAS")

fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)

# setup axis
ax.set_aspect("equal")
ax.set_axis_off()

PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30

# add all player objects with a random color
player_list = []
text_list = []
interval = 1.0 / (len(frame_list)-1)
for i in range(0, len(frame_list)):
    player_color = (color_list[i]*interval, 1.0-(color_list[i]*interval), 0)
    player_list.append(patches.Rectangle((30*i, 0), PLAYER_WIDTH, PLAYER_HEIGHT, facecolor=player_color, edgecolor="black", linewidth=1))
    text_list.append(text.Text(30*i-10, 50, name_list[i], fontsize=8, horizontalalignment="center", verticalalignment="center"))
    ax.add_patch(player_list[i])
    #ax.add_artist(text_list[i])

load_images()

# run the animation :)
Writer = animation.writers["ffmpeg"]
anim_writer = Writer(fps=60)
anim = animation.FuncAnimation(fig, draw_frame, frames=50, interval=17, blit=False, repeat=False, fargs=(frame_list, spectate_index, player_list))
anim.save("tower_comparison.mp4", writer=anim_writer)
