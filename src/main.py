import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import matplotlib.text as text
import random

import csv
import os
# get all the lines representing the level from a csv
def get_lines_from_csv(filepath):
    x_lines = []
    y_lines = []

    # very lazy approach
    # csv needs to alternate between blank row, x row, and y row
    with open(filepath, "r") as file:
        reader = csv.reader(file)
        type = "blank"
        for row in reader:
            if type == "blank":
                type = "x"
            elif type == "x":
                type = "y"
                x_vals = []
                for val in row:
                    if val:
                        x_vals.append(int(val))
                x_lines.append(x_vals)
            else:
                type = "blank"
                y_vals = []
                for val in row:
                    if val:
                        y_vals.append(int(val))
                y_lines.append(y_vals)

    return x_lines, y_lines

# gets x, y coords at each frame from a csv file
def get_frames_from_csv(filepath):
    frame_list = []
    with open(filepath, "r") as file:
        reader = csv.reader(file)
        name = next(reader)[0]
        for row in reader:
            frame_list.append([int(float(row[0])), int(float(row[1]))])

    return frame_list, name

# gets x, y coords at each frame from multiple players listed in target folder
def get_all_frames(filepath):
    csv_paths = os.listdir(filepath)
    total_frame_list = []
    name_list = []
    for path in csv_paths:
        frames, name = get_frames_from_csv((os.path.join(filepath, path)))
        total_frame_list.append(frames)
        name_list.append(name)

    return total_frame_list, name_list

# draws all the lines passed in onto the axis
def draw_lines(x_lines, y_lines, ax, line_color="black"):
    for i in range(0, len(x_lines)):
        ax.plot(x_lines[i], y_lines[i], color=line_color)

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
            ax.set_xlim(x-500, x+500)
            ax.set_ylim(y-500, y+500)

    # for blitting
    artist_list = player_list[:]
    artist_list += text_list[:]
    artist_list.append(ax)
    return artist_list

matplotlib.rcParams["animation.ffmpeg_path"] = "/usr/bin/ffmpeg"
# get the outline and values for each frame
x_lines, y_lines = get_lines_from_csv("tower.csv")
frame_list, name_list = get_all_frames("frames")
spectate_index = name_list.index("TAS")

fig, ax = plt.subplots()

# setup axis
ax.set_aspect("equal", adjustable="box")
ax.set_xlim(0, 500)
ax.set_ylim(0, 500)
ax.set_axis_off()

PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30

# add all player objects with a random color
player_list = []
text_list = []
for i in range(0, len(frame_list)):
    random_color = (random.random(), random.random(), random.random())
    player_list.append(patches.Rectangle((30*i, 0), PLAYER_WIDTH, PLAYER_HEIGHT, color=random_color))
    text_list.append(text.Text(30*i-10, 50, name_list[i], fontsize=8, horizontalalignment="center", verticalalignment="center"))
    ax.add_patch(player_list[i])
    ax.add_artist(text_list[i])

draw_lines(x_lines, y_lines, ax)

# run the animation :)
Writer = animation.writers["ffmpeg"]
anim_writer = Writer(fps=60)
anim = animation.FuncAnimation(fig, draw_frame, frames=5000, interval=17, blit=False, repeat=False, fargs=(frame_list, spectate_index, player_list))
anim.save("test.mp4", writer=anim_writer)
