from tkinter import *
from tkinter import ttk
from tkvideo import tkvideo
#from tkVideoPlayer import TkinterVideo
import random, math
from PIL import Image, ImageTk
import threading
import imageio
#print(f'sudo "{sys.executable}" -m pip install pillow')
#print(f'sudo "{sys.executable}" -m pip install requests')
#TODO: play the audio file asynchronously?
#print(os.environ['USER'])
#os.environ["IMAGEIO_FFMPEG_EXE"] = os.getcwd() + "/ffmpeg"

outputs = open('outputs', 'r')
output_lines = outputs.readlines()
Q_array = []
inf_vals = []

def parse_inf(s):
    res = []
    nums = s.split(" ")
    #print(nums)
    for num in nums:
        try:
            n = float(num)
            #print(n)
            res.append(n)
        except:
            pass
    return res


for line in output_lines:
    stripped_line = line.split("emotion ")[1].split(", ")
    q_val = stripped_line[0].strip()
    inf_val = stripped_line[1].split(": ")[1].split("]\n")[0][2:-1].strip(" \n")
    inf_val = parse_inf(inf_val)
    #print(q_val)
    Q_array.append(q_val)
    #print(inf_val)
    inf_vals.append(inf_val)

print(Q_array)
print(len(Q_array))
print(inf_vals)
print(len(inf_vals))


#################################################################
# Graphical code
#################################################################

video = imageio.get_reader('ricker_choi.mp4')

def display_video(label):
    # iterate through video data
   for image in video.iter_data():
      # convert array into image
      img = Image.fromarray(image)
      # Convert image to PhotoImage
      image_frame = ImageTk.PhotoImage(image = img)
      # configure video to the lable
      label.config(image=image_frame)
      label.image = image_frame

# Classes of shapes: circles, lines, swirls
class Circle(object):
    # Model
    def __init__(self, cx, cy, r, speed, angle, color):
        # A circle has a position, size, speed, direction, and color
        self.cx = cx
        self.cy = cy
        self.r = r
        self.speed = speed
        self.angle = angle
        self.color = color

    # View
    def draw(self, canvas):
        o = canvas.create_oval(self.cx - self.r, self.cy - self.r,
                           self.cx + self.r, self.cy + self.r,
                           fill=self.color,
                           width=0)
        return o

    # Controller
    def moveCircle(self):
        self.cx += math.cos(math.radians(self.angle))*self.speed
        self.cy -= math.sin(math.radians(self.angle))*self.speed

'''
class GrowingCircle(Circle):
    # Model
    def __init__(self, cx, cy, r, speed, direction):
        # Growing Circles also track how fast they grow
        super().__init__(cx, cy, r, speed, direction)
        self.growAmount = 5
'''

class MyLine(Circle):
    # We'll just override the draw() function from the circle
    def draw(self, canvas):
        canvas.create_line(self.cx, self.cy, self.cx+math.cos(math.radians(self.angle))*random.randint(1,10), self.cy-math.sin(math.radians(self.angle))*random.randint(1,10),
                           fill=self.color, width=self.r)

class MyRectangle(Circle):
    # We'll just override the draw() function from the circle
    def draw(self, canvas):
        canvas.create_rectangle(self.cx, self.cy, self.cx+self.r, self.cy-self.r, fill=self.color, width=0)

# Helper function: given a mode and a scaling number, generates a hex color for the shape 
def color_gen(mode, scale):
    if mode == "warm":
        r_lim = round(255*scale)
        b_lim = 255 - round(255*scale)
        g_lim = round((r_lim + b_lim) / 2)
        red = lambda: random.randint(0,r_lim)
        green = lambda: random.randint(0,g_lim)
        blue = lambda: random.randint(0,b_lim)
        return '#%02X%02X%02X' % (red(),green(),blue())
    elif mode == "cool":
        r_lim = 255 - round(255*scale)
        b_lim = round(255*scale)
        g_lim = round((r_lim + b_lim) / 2)
        red = lambda: random.randint(0,r_lim)
        green = lambda: random.randint(0,g_lim)
        blue = lambda: random.randint(0,b_lim)
        return '#%02X%02X%02X' % (red(),green(),blue())

def init(data):
    data.timer = 0
    data.shapes = []
    data.shrinkCutoff = 15
    data.lowerRad, data.upperRad = 20, 50
    data.lowerSpeed, data.upperSpeed = 30, 40
    data.circleTime = 10
    # infIndex goes from 0 to 25, indexing into inf_vals to grab us our array of inference values for each quadrant
    data.infIndex = 0
    data.updateInfTime = 100
    print("infIndex: " + str(data.infIndex))
    print("Quadrant: " + Q_array[data.infIndex])


def timerFired(data):
    data.timer += 1

    #Every second, a new circle is created and placed onto the board
    if(data.timer%data.circleTime == 0):
        # We know these values range between 0 to 1
        q1_val = inf_vals[data.infIndex][0]
        q2_val = inf_vals[data.infIndex][1]
        q3_val = inf_vals[data.infIndex][2]
        q4_val = inf_vals[data.infIndex][3]
        # 'quad' is the scaling factor
        quad = max(q1_val, q2_val, q3_val, q4_val)
        # How should these values be mapped based on the inference values?
        base_radius = random.randint(data.lowerRad, data.upperRad)
        base_speed = random.randint(data.lowerSpeed, data.upperSpeed)
        base_color = "white"
        base_shape = None

        # Arousal: approximately maps to 'frequency of note occurences and their strength...we measure them by note density, length and velocity'
        # Note density is defined as the number of notes per beat
        # Note length is defined as average note length in beat unit
        # Note velocity

        # Note lengths generally longer in the low-arousal group
        '''
        In note density, Q2
        has more dynamics than Q1, whereas Q3 is not distinguishable from Q4. In note length, Q1 has slightly longer notes
        than those of Q2, whereas Q3 is again not distinguishable
        from Q4. In velocity, Q2 have louder notes than those of
        Q1, and Q3 has slightly louder notes than Q4.
        '''
        # High valence: generally positive/major tonality (Q1, Q4)
        # Low valence: generally negative/minor tonality (Q2, Q3)

        # We can update circleTime (how often we place notes on the screen) based on current values

        # Q1: High Valence, High Arousal
        # Shapes should be BIGGER, FASTER, WARM-COLORED and should come out MORE OFTEN; shapes should be POINTIER
        if Q_array[data.infIndex] == 'Q1':
            base_radius = base_radius + 20*quad
            base_speed = base_speed + 20*quad
            base_color = color_gen("warm", quad)
            data.circleTime = round((5 + round(10*quad)) / 2)
            base_shape = random.choice([MyLine, MyRectangle])
        # Q2: Low Valence, High Arousal
        # Shapes should be BIGGER, FASTER, COOL-COLORED and should come out MORE OFTEN; shapes should be POINTIER
        elif Q_array[data.infIndex] == 'Q2':
            base_radius = base_radius + 20*quad
            base_speed = base_speed + 20*quad
            base_color = color_gen("cool", quad)
            data.circleTime = round((5 + round(10*quad)) / 2)
            base_shape = random.choice([MyLine, MyRectangle])
        # Q3: Low Valence, Low Arousal
        # Shapes should be SMALLER, SLOWER, COOL-COLORED and should come out LESS OFTEN; shapes should be ROUNDER
        elif Q_array[data.infIndex] == 'Q3':
            base_radius = base_radius - 20*quad
            base_speed = base_speed - 20*quad
            base_color = color_gen("cool", quad)
            data.circleTime = round((15 + round(10*quad)) / 2)
            base_shape = Circle
        # Q4: High Valence, Low Arousal
        # Shapes should be SMALLER, SLOWER, WARM-COLORED and should come out LESS OFTEN; shapes should be ROUNDER
        elif Q_array[data.infIndex] == 'Q4':
            base_radius = base_radius - 20*quad
            base_speed = base_speed - 20*quad
            base_color = color_gen("warm", quad)
            data.circleTime = round((15 + round(10*quad)) / 2)
            base_shape = Circle

        rRadius = round(base_radius)
        rSpeed = base_speed
        rColor = base_color

        # Position and direction of the note doesn't depend on inference values
        rX = random.randint(round(data.width/3), round(2*data.width/3))
        rY = random.randint(round(data.height/4), round(3*data.height/4))
        rDirection = random.randint(30, 150)

        rType = base_shape
        #data.shapes.append(rType(rX, rY, rRadius, rSpeed, rDirection))
        data.shapes.append(rType(rX, rY, rRadius, rSpeed, rDirection, rColor))

    # Moves shapes every call to timerFired
    for shape in data.shapes:
        shape.moveCircle()

    # Every 10 seconds, we increment data.infIndex by 1
    if(data.timer%data.updateInfTime == 0 and data.infIndex < 26):
        data.infIndex += 1
        print("infIndex: " + str(data.infIndex))
        curr_quad = Q_array[data.infIndex]
        debug_line = "Quadrant: " + curr_quad
        if curr_quad == 'Q1':
            debug_line += " High Valence, High Arousal "
        elif curr_quad == 'Q2':
            debug_line += " Low Valence, High Arousal "
        elif curr_quad == 'Q3':
            debug_line += " Low Valence, Low Arousal "
        elif curr_quad == 'Q4':
            debug_line += " High Valence, Low Arousal "
        debug_line += " Inference Val: " + str(max(inf_vals[data.infIndex]))
        print(debug_line)

def redrawAll(canvas, data):
    #canvas.create_rectangle(0, 0, data.width, data.height, fill="white")
    #canvas.create_rectangle(0, 0, data.width, data.height, fill='')
    #bg = ImageTk.PhotoImage(file="./test_image.png")
    #canvas.create_image(0,0,image=bg, anchor="nw")
    #w = canvas.create_window(0, 0, height=0, width=0)
    canvas.create_rectangle(0, 0, data.width, data.height, fill="gray", outline="gray")
    for shape in data.shapes:
        o = shape.draw(canvas)
        #canvas.itemconfigure(w, window = o)
    canvas.create_text(data.width/2, data.height, anchor="s", fill="yellow",
                       font="Arial 24 bold", text="Timer: " + str(data.timer))

def mousePressed(event, data):
    pass

def keyPressed(event, data):
    pass

#################################################################
# use the run function as-is
#################################################################

def run(width=1280, height=720):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        #canvas.create_rectangle(0, 0, data.width, data.height,
                                #fill='white', width=0)
        #canvas.create_rectangle(0, 0, data.width, data.height, width=0, fill='')
        #bg = ImageTk.PhotoImage(file="./test_image.png")
        #canvas.create_image(0,0,image=bg, anchor="nw")
        #w = canvas.create_window(0, 0, height=0, width=0)
        canvas.create_rectangle(0, 0, data.width, data.height, fill="gray", outline="gray", width=0)                      
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    # The variable data.timerDelay is referenced in timerFiredWrapper
    # Change it to affect how often timerFired is called
    data.timerDelay = 100 # milliseconds
    root = Tk()
    root.title("Performance Visualizer")
    init(data)
    # create the root and the canvas

    root.lift()
    root.wm_attributes("-topmost", True)

    # The below code is for macOS
    root.configure(bg="systemTransparent")
    root.wm_attributes("-transparent", True)

    '''
    # The below code is for Windows
    root.wm_attributes("-transparentcolor", 'gray')
    root.wait_visibility()
    '''

    #Code for the video to play
    video_label = Label(root)
    #video_label.place(x = 0, y = 0, height = 720, width = 1280)
    video_label.pack()
    player = tkvideo("ricker_choi.mp4", video_label, loop = 0, size = (1280, 720))
    player.play()

    canvas = Canvas(root, width=data.width, height=data.height, bg='gray')
    canvas.configure(bd=0, highlightthickness=0)
    canvas.place(x = 0, y = 0, width = 1280, height = 720)
    #canvas.pack()

    '''
    video_label = canvas
    video_label.place(x = 0, y = 0, height = 720, width = 1280)
    #video_label.pack(fill=BOTH, expand=True)
    player = tkvideo("ricker_choi.mp4", video_label, loop = 0, size = (1280, 720))
    player.play()
    '''

    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app

    #root.overrideredirect(True)
    # Make the root window always on top

    #root.attributes('-alpha', 0.8)
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1280, 720)