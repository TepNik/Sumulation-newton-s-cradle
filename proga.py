import tkinter as tk
import math
import time
from PIL import Image, ImageTk
import base64
from my_image_base64 import *
from icon_base64 import *
#import os, sys

koef_radius = 50
delta_radius = 1

class SetValueFrame(tk.Frame):
    def __init__(self, master, width=30, value=0.0, text=""):
        super().__init__(master, width=width)

        self.value = value

        self.text = tk.Label(self, text=text, width=width)
        self.text.pack(side=tk.TOP)

        self.input = tk.Text(self, width=width, height=1)
        self.input.pack(side=tk.TOP)

        self.output_str_var = tk.StringVar(self)
        self.output_str_var.set(str(value))
        self.output_value = tk.Label(
            self, textvar=self.output_str_var, width=width)
        self.output_value.pack(side=tk.TOP)

        self.input.bind("<Return>", self.change_value)

    def change_value(self, event=None):
        text = self.input.get(1.0, tk.END).strip()

        if len(text) > 0:
            try:
                new_value = float(text)
                self.value = new_value
                self.output_str_var.set(str(new_value))
            except BaseException:
                pass

        self.input.delete(1.0, tk.END)


class LabelWithStrVar(tk.Frame):
    def __init__(self, master, width, text="", default_value="0.0"):
        super().__init__(master, width=width)
        self.str_var = tk.StringVar(master)
        self.str_var.set(str(default_value))
        self.str = tk.Label(
            master, textvar=self.str_var)
        self.label = tk.Label(master, text=text)
        self.label.pack(side=tk.TOP)
        self.str.pack(side=tk.TOP)

    def set(self, value):
        self.str_var.set(str(value))


class DrawingCanvas(tk.Canvas):
    def __init__(self, master, image=None):
        super().__init__(master, bg="white")
        self.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
        if image:
            self.create_image(0, 0, image=image, anchor=tk.NW)
        self.line_1 = 0
        self.line_2 = 0
        self.oval_1 = 0
        self.oval_2 = 0
        self.angle_line_1 = 0
        self.angle_line_2 = 0
        self.is_moving = False

    def draw_initial_picture(self, angle1=0.0, angle2=0.0, color="white", delete_angle_lines=False):
        tk.Tk.update(self)
        x = self.winfo_width()
        y = self.winfo_height()
        self.x = x
        self.y = y
        length = y/2
        delta_y_1 = math.cos(math.radians(angle1))*length
        delta_x_1 = math.sin(math.radians(angle1))*length
        delta_y_2 = math.cos(math.radians(angle2))*length
        delta_x_2 = math.sin(math.radians(angle2))*length
        radius = min(x, y)/koef_radius
        self.radius = radius
        radius += delta_radius

        self.delete_all_lines(angle_line_1=delete_angle_lines, angle_line_2=delete_angle_lines)

        self.line_1 = self.create_line(
            x/2 - radius, 0, x/2 - radius - delta_x_1, delta_y_1, fill=color)
        self.oval_1 = self.create_oval(x/2 - 2*radius - delta_x_1, delta_y_1 - radius,
                                       x/2 - delta_x_1, delta_y_1 + radius,
                                       fill=color, outline=color)

        self.line_2 = self.create_line(
            x/2 + radius, 0, x/2 + radius + delta_x_2, delta_y_2, fill=color)
        self.oval_2 = self.create_oval(x/2 + delta_x_2, delta_y_2 - radius,
                                       x/2 + 2*radius + delta_x_2, delta_y_2 + radius,
                                       fill=color, outline=color)

        self.ball1_x = x/2 - radius - delta_x_1
        self.ball1_y = delta_y_1
        self.ball2_x = x/2 + radius + delta_x_2
        self.ball2_y = delta_y_2
        self.angle1 = angle1
        self.angle2 = angle2

    def drop_ball(self, angle1_begin, angle2_begin, m1, m2, loss, G, fun1, fun2):
        w1 = 0
        w2 = 0
        is_skip_next = True
        mistake = 0.05
        mistake2 = G*self.y/15000000
        self.is_moving = True
        while (abs(angle1_begin) > mistake or abs(w1) > mistake or\
               abs(angle2_begin) > mistake or abs(w2) > mistake) and self.is_moving:
            if is_skip_next:
                time_begin = time.process_time()
                is_skip_next = False
            time_end = time.process_time()
            time_delta = time_end - time_begin
            a1 = G*math.sin(math.radians(angle1_begin))*self.y/2
            a2 = G*math.sin(math.radians(angle2_begin))*self.y/2
            angle1_end = angle1_begin - (a1*time_delta/2 + w1)*time_delta
            angle2_end = angle2_begin - (a2*time_delta/2 + w2)*time_delta
            if w1 * (w1 + a1*time_delta) <= 0:
                fun1(str(max(angle1_begin, angle1_end)))
                self.draw_angle_for_1(max(angle1_begin, angle1_end))
            if w2 * (w2 + a2*time_delta) <= 0:
                fun2(str(max(angle2_begin, angle2_end)))
                self.draw_angle_for_2(max(angle2_begin, angle2_end))
            w1 += a1*time_delta
            w2 += a2*time_delta
            w1 *= (1 - mistake2)
            w2 *= (1 - mistake2)
            delta_x = self.ball1_x - self.ball2_x
            delta_y = self.ball1_y - self.ball2_y
            distance = math.sqrt(delta_x*delta_x + delta_y*delta_y)
            if distance < 2*self.radius or delta_x > 0:
                distance_for_one = self.radius - distance/2 + delta_radius
                if delta_x > 0:
                    distance_for_one += distance
                delta_for_one_angle = distance_for_one*180/(math.pi*self.y/2)
                angle1_end += delta_for_one_angle
                angle2_end += delta_for_one_angle
                v1 = w1*self.y/2
                v2 = -w2*self.y/2
                v1, v2 = self.calculate_v_after_crash(v1, v2, m1, m2)
                w1 = v1*2/self.y
                w2 = -v2*2/self.y
                w1 *= (1 - loss)
                w2 *= (1 - loss)
                is_skip_next = True
            if angle1_end > 90:
                angle1_end = 90
                w1 = 0
            elif angle1_end < -90:
                angle1_end = -90
                w1 = 0
            if angle2_end > 90:
                angle2_end = 90
                w2 = 0
            elif angle2_end < -90:
                angle2_end = -90
                w2 = 0
            self.draw_initial_picture(angle1_end, angle2_end)
            angle1_begin = angle1_end
            angle2_begin = angle2_end
            time_begin = time_end
        self.is_moving = False

    def calculate_v_after_crash(self, v1, v2, m1, m2):
        u1 = ((m1 - m2)*v1 + 2*m2*v2)/(m1 + m2)
        u2 = ((m2 - m1)*v2 + 2*m1*v1)/(m1 + m2)
        return u1, u2

    def draw_angle_for_1(self, angle, color="blue"):
        tk.Tk.update(self)
        x = self.winfo_width()
        y = self.winfo_height()
        length = y/2.5
        delta_y = math.cos(math.radians(angle))*length
        delta_x = math.sin(math.radians(angle))*length
        radius = min(x, y)/koef_radius + delta_radius

        if self.angle_line_1 != 0:
            self.delete(self.angle_line_1)

        self.angle_line_1 = self.create_line(
            x/2 - radius, 0, x/2 - radius - delta_x, delta_y, fill=color, width=2)

    def draw_angle_for_2(self, angle, color="blue"):
        tk.Tk.update(self)
        x = self.winfo_width()
        y = self.winfo_height()
        length = y/2.5
        delta_y = math.cos(math.radians(angle))*length
        delta_x = math.sin(math.radians(angle))*length
        radius = min(x, y)/koef_radius + delta_radius

        if self.angle_line_2 != 0:
            self.delete(self.angle_line_2)

        self.angle_line_2 = self.create_line(
            x/2 + radius, 0, x/2 + radius + delta_x, delta_y, fill=color, width=2)

    def delete_all_lines(self, line_1=True, line_2=True, oval_1=True, oval_2=True, angle_line_1=True, angle_line_2=True):
        if self.line_1 != 0 and line_1:
            self.delete(self.line_1)
            self.line_1 = 0
        if self.line_2 != 0 and line_2:
            self.delete(self.line_2)
            self.line_2 = 0
        if self.oval_1 != 0 and oval_1:
            self.delete(self.oval_1)
            self.oval_1 = 0
        if self.oval_2 != 0 and oval_2:
            self.delete(self.oval_2)
            self.oval_2 = 0
        if self.angle_line_1 != 0 and angle_line_1:
            self.delete(self.angle_line_1)
            self.angle_line_1 = 0
        if self.angle_line_2 != 0 and angle_line_2:
            self.delete(self.angle_line_2)
            self.angle_line_2 = 0


class MainWindow(tk.Tk):
    def __init__(self, right_width=20, geometry="1200x800+200+10"):
        super().__init__()

        self.title("Phisics")
        self.geometry(geometry)
        self.resizable(False, False)

        self.icon_64 = tk.PhotoImage(data=icon_data_base64_encoded_string)
        self.tk.call('wm', 'iconphoto', self._w, self.icon_64)

        self.right_frame = tk.Frame(self)

        self.frame_ball1 = SetValueFrame(
            self.right_frame, width=right_width,
            text="Mass for first ball", value=2.0)
        self.frame_ball1.pack(side=tk.TOP, pady=10, padx=10)

        self.frame_ball2 = SetValueFrame(
            self.right_frame, width=right_width,
            text="Mass for second ball", value=10.0)
        self.frame_ball2.pack(side=tk.TOP, pady=10, padx=10)

        self.frame_angle1 = SetValueFrame(
            self.right_frame, width=right_width,
            text="Angle for 1 (in degrees)", value=80.0)
        self.frame_angle1.pack(side=tk.TOP, pady=10, padx=10)

        self.frame_angle2 = SetValueFrame(
            self.right_frame, width=right_width,
            text="Angle for 2 (in degrees)", value=0.0)
        self.frame_angle2.pack(side=tk.TOP, pady=10, padx=10)

        self.frame_loss = SetValueFrame(
            self.right_frame, width=right_width,
            text="Loss energy after crash", value=0.1)
        self.frame_loss.pack(side=tk.TOP, pady=10, padx=10)

        self.frame_G = SetValueFrame(
            self.right_frame, width=right_width,
            text="G", value=9.81)
        self.frame_G.pack(side=tk.TOP, pady=10, padx=10)

        self.max_angle1_frame = LabelWithStrVar(
            self.right_frame, right_width, "Max angle for 1")
        self.max_angle2_frame = LabelWithStrVar(
            self.right_frame, right_width, "Max angle for 2")

        self.max_angle1_frame.pack(side=tk.TOP)
        self.max_angle2_frame.pack(side=tk.TOP)

        self.button_frame = tk.Frame(self.right_frame, width=right_width)

        self.draw_button = tk.Button(
            self.button_frame, text="Draw", command=self.draw_picture)
        self.draw_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.drop_button = tk.Button(
            self.button_frame, text="Drop", command=self.drop_ball)
        self.drop_button.pack(side=tk.RIGHT, padx=10, pady=10)
        self.stop_button = tk.Button(
            self.button_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.RIGHT, padx=10, pady=10)
        self.stop_button['state'] = tk.DISABLED

        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.photo_for_canvas = tk.PhotoImage(data=image_data_base64_encoded_string)

        self.canvas = DrawingCanvas(self, image=self.photo_for_canvas)
        self.canvas.draw_initial_picture(
            self.frame_angle1.value, self.frame_angle2.value)

    def get_values(self, event=None):
        self.frame_angle1.change_value()
        self.frame_angle2.change_value()
        self.frame_ball1.change_value()
        self.frame_ball2.change_value()
        self.frame_loss.change_value()
        self.frame_G.change_value()

    def stop(self, event=None):
        self.canvas.is_moving = False
        self.drop_button['state'] = tk.NORMAL
        self.stop_button['state'] = tk.DISABLED
        self.draw_button['state'] = tk.NORMAL

    def draw_picture(self, event=None):
        self.canvas.is_moving = False
        self.canvas.delete_all_lines()
        self.get_values()
        self.canvas.draw_initial_picture(
            self.frame_angle1.value, self.frame_angle2.value, delete_angle_lines=True)

    def drop_ball(self, event=None):
        self.canvas.is_moving = False
        self.get_values()
        self.drop_button['state'] = tk.DISABLED
        self.stop_button['state'] = tk.NORMAL
        self.draw_button['state'] = tk.DISABLED
        self.canvas.drop_ball(self.frame_angle1.value, self.frame_angle2.value, self.frame_ball1.value, self.frame_ball2.value,
                              self.frame_loss.value, self.frame_G.value, self.max_angle1_frame.set, self.max_angle2_frame.set)


if __name__ == "__main__":
    window = MainWindow()
    window.mainloop()
