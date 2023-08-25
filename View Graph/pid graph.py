import tkinter as tk
from tkinter import ttk


class PID:
    def __init__(self, Kp=0, Ki=0, Kd=0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.previous_error = 0
        self.integral = 0

    def compute(self, input_val, setpoint):
        error = setpoint - input_val
        P = self.Kp * error
        self.integral += error
        I = self.Ki * self.integral
        derivative = error - self.previous_error
        D = self.Kd * derivative
        self.previous_error = error
        return P + I + D

class GraphPlotter:
    def __init__(self, root):
        self.canvas = tk.Canvas(root, bg='white', width=600, height=400)
        self.canvas.grid(row=8, column=0, columnspan=2, pady=20)
        # self.canvas.pack(fill=tk.BOTH, expand=True)

        # some sample data and initial values for xMin, xMax, yMin, yMax
        self.data = [10, 20, 30, 40, 50]
        self.xMin = 0
        self.xMax = len(self.data)
        self.yMin = min(self.data)
        self.yMax = max(self.data)

        # Bind the mouse wheel event
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan)

        self.plot_data(self.data)

    def plot_data(self, data):
        self.canvas.delete("all")  # Clear previous plot
        width = float(self.canvas['width'])
        height = float(self.canvas['height'])

        for i in range(len(data) - 1):
            x1 = (i - self.xMin) / (self.xMax - self.xMin) * width
            y1 = height - (data[i] - self.yMin) / (self.yMax - self.yMin) * height
            x2 = (i + 1 - self.xMin) / (self.xMax - self.xMin) * width
            y2 = height - (data[i + 1] - self.yMin) / (self.yMax - self.yMin) * height
            self.canvas.create_line(x1, y1, x2, y2)

    def zoom(self, event):
        width = float(self.canvas['width'])
        height = float(self.canvas['height'])

        mouseX, mouseY = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        scaleFactor = 1.1
        zoomFactor = 1 / scaleFactor if event.delta > 0 else scaleFactor

        if event.state & 1:  # Shift key is pressed, zoom on Y-axis
            mouseYPercent = (1 - (mouseY / height)) * (self.yMax - self.yMin) + self.yMin

            self.yMin = mouseYPercent - (mouseYPercent - self.yMin) * zoomFactor
            self.yMax = mouseYPercent + (self.yMax - mouseYPercent) * zoomFactor
        else:  # zoom on X-axis
            mouseXPercent = (mouseX / width) * (self.xMax - self.xMin) + self.xMin

            self.xMin = mouseXPercent - (mouseXPercent - self.xMin) * zoomFactor
            self.xMax = mouseXPercent + (self.xMax - mouseXPercent) * zoomFactor

        self.plot_data(self.data)

    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def pan(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

class App:
    def __init__(self, root):
        self.zoom_scale = 1.0
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.last_x = 0
        self.last_y = 0

        self.root = root
        self.root.title("Line Graph")

        self.target_var = tk.DoubleVar(value=100)
        self.kp_var = tk.DoubleVar(value=0.003)
        self.ki_var = tk.DoubleVar(value=0)
        self.kd_var = tk.DoubleVar(value=0.1)
        self.max_acceleration_var = tk.DoubleVar(value=0.1)
        self.max_velocity_var = tk.DoubleVar(value=1000)
        self.num_iterations_var = tk.IntVar(value=1000)

        self.graph = GraphPlotter(root)

        ttk.Label(root, text="Target:").grid(row=0, column=0)
        ttk.Entry(root, textvariable=self.target_var).grid(row=0, column=1)

        ttk.Label(root, text="Kp:").grid(row=1, column=0)
        ttk.Scale(
            root, from_=0, to_=0.01, orient="horizontal", variable=self.kp_var
        ).grid(row=1, column=1)

        ttk.Label(root, text="Ki:").grid(row=2, column=0)
        ttk.Scale(
            root, from_=0, to_=0.01, orient="horizontal", variable=self.ki_var
        ).grid(row=2, column=1)

        ttk.Label(root, text="Kd:").grid(row=3, column=0)
        ttk.Scale(
            root, from_=0, to_=0.2, orient="horizontal", variable=self.kd_var
        ).grid(row=3, column=1)

        ttk.Label(root, text="Max Acceleration:").grid(row=4, column=0)
        ttk.Entry(root, textvariable=self.max_acceleration_var).grid(row=4, column=1)

        ttk.Label(root, text="Max Velocity:").grid(row=5, column=0)
        ttk.Entry(root, textvariable=self.max_velocity_var).grid(row=5, column=1)

        ttk.Label(root, text="Num Iterations:").grid(row=6, column=0)
        ttk.Entry(root, textvariable=self.num_iterations_var).grid(row=6, column=1)

        self.run_button = ttk.Button(
            root, text="Run Simulation", command=self.run_simulation
        )
        self.run_button.grid(row=7, column=0, columnspan=2)


        self.output_text = tk.Text(root, width=80, height=20)
        self.output_text.grid(row=9, column=0, columnspan=2, pady=20)
        

    def run_simulation(self):
        pid = PID(self.kp_var.get(), self.ki_var.get(), self.kd_var.get())
        position = 0
        velocity = 0
        max_acceleration = self.max_acceleration_var.get()
        max_velocity = self.max_velocity_var.get()
        num_iterations = self.num_iterations_var.get()
        self.data = []

        for _ in range(num_iterations):
            acceleration = pid.compute(position, self.target_var.get())
            acceleration = max(-max_acceleration, min(max_acceleration, acceleration))

            velocity += acceleration
            velocity = max(-max_velocity, min(velocity, max_velocity))

            position += velocity
            self.data.append(position)

        self.graph.plot_data(self.data)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "\n".join(map(str, self.data)))


root = tk.Tk()
app = App(root)
root.mainloop()


