import csv

def list_from_csv(filepath):
    input_list = []
    with open(filepath, "r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            input_list.append(row)
            
    return input_list

def get_processed_list(input_list):
    processed_list = [[] for row in input_list]
    time_tolerance = 0.50
    x_tolerance = 300.0
    y_tolerance = 100.0
    for i in range(0, len(input_list)):
        time = input_list[i][0]
        x = input_list[i][1]
        y = input_list[i][2]
        
        if i == 0:
            processed_list[i] = [time, x, y]
            continue
        
        try:
            time_float = float(time)
            last_time = float(processed_list[i-1][0])
            if abs(time_float - last_time) > time_tolerance:
                raise Exception
        except Exception:
            time = str(last_time + 0.01)
        
        try:
            x_float = float(x)
            last_x = float(processed_list[i-1][1])
            if abs(x_float - last_x) > x_tolerance:
                raise Exception
        except Exception:
            last_x = float(processed_list[i-1][1])
            last_last_x = float(processed_list[i-2][1])
            x = str(last_x + (last_x - last_last_x))
        
        try:
            y_float = float(y)
            last_y = float(processed_list[i-1][2])
            if abs(y_float - last_y) > y_tolerance:
                raise Exception
        except Exception:
            last_y = float(processed_list[i-1][2])
            last_last_y = float(processed_list[i-2][2])
            y = str(last_y + (last_y - last_last_y))
        
        processed_list[i] = [time, x, y]  
    
    return processed_list

def get_frame_list(input_list, fps=60):
    frame_list = [[None, None] for i in range(0, fps*len(input_list))]
    last_index = 0
    for row in input_list:
        index = int(float(row[0]) / (1/float(fps)))
        frame_list[index] = row[1:]
        last_index = index
    
    i = 0
    while i < len(frame_list):
        if frame_list[i] == [None, None]:
            if i < last_index:
                frame_list[i] = frame_list[i-1] # i think a reference is fine prob
            else:
                del frame_list[i]
                i -= 1
        i += 1
    
    return frame_list

def pack_frame_list_to_csv(filepath, frame_list):
    with open(filepath, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(frame_list)
    
input_list = list_from_csv("unprocessed_frames.csv")
processed_list = get_processed_list(input_list)
frame_list = get_frame_list(processed_list)
pack_frame_list_to_csv("frames.csv", frame_list)
