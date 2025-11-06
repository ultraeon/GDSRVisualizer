import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches

import csv

fig, ax = plt.subplots()

ax.set_aspect("equal", adjustable="box")
ax.set_axis_off()

player_x = 0
player_y = 0
player_width = 30
player_height = 30

player = patches.Rectangle((player_x, player_y), player_width, player_height, color="blue")
ax.add_patch(player)

def get_lines_from_csv(filepath, color="black"):
    x_lines = []
    y_lines = []

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

def get_frames_from_csv(filepath):
    frame_list = []
    with open(filepath, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            frame_list.append([int(float(row[0])), int(float(row[1]))])

    return frame_list
    
def draw_lines(x_lines, y_lines, ax):
    for i in range(0, len(x_lines)):
        ax.plot(x_lines[i], y_lines[i], color="black")

def draw_frame(frame, frame_list, player):
    x = frame_list[frame][0]
    y = frame_list[frame][1]
    player.set_xy((x, y))
    ax.set_xlim(x-500, x+500)
    ax.set_ylim(y-500, y+500)
    return player, ax

# draw_frame function ends here
x_lines, y_lines = get_lines_from_csv("Tower.csv")
frame_list = get_frames_from_csv("Frames.csv")
draw_lines(x_lines, y_lines, ax)

anim = animation.FuncAnimation(fig, draw_frame, frames=3850, interval=17, blit=True, repeat=False, fargs=(frame_list, player))
plt.show()
