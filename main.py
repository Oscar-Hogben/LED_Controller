import pygame, time, datetime, threading

title_font_to_use = 'arialblack.ttf'

def alarm_function(led_activation, weather_announcement):
    print('ALARM')
    print('LED Activation:',led_activation)
    print('Weather Announcement:',weather_announcement)

class ColorPicker:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.image = pygame.Surface((w, h))
        self.image.fill((0, 0, 0))
        self.rad = h//2
        self.pwidth = w-self.rad*2
        for i in range(self.pwidth):
            color = pygame.Color(0)
            color.hsla = (int(360*i/self.pwidth), 100, 50, 100)
            pygame.draw.rect(self.image, color, (i+self.rad, h//3, 1, h-2*h//3))
        self.p = 0

    def get_color(self):
        color = pygame.Color(0)
        color.hsla = (int(self.p * 360), 100, 50, 100)
        return color

    def update(self):
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if mouse_buttons[0] and self.rect.collidepoint(mouse_pos):
            self.p = (mouse_pos[0] - self.rect.left - self.rad) / self.pwidth
            self.p = (max(0, min(self.p, 1)))

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        center = self.rect.left + self.rad + self.p * self.pwidth, self.rect.centery
        pygame.draw.circle(surf, self.get_color(), center, self.rect.height // 2)

class Slider:
    def __init__(self,x,y,w,h):
        self.x = x
        self.y = y 

        self.mag = 1

        self.slider_icon_font = pygame.font.SysFont(title_font_to_use, 20, bold=False)

        self.slider_width = w
        self.slider_height = h

        self.slider_border = pygame.Rect(x, y, self.slider_width, self.slider_height)
        self.slider_background = pygame.Rect(x+2, y+2, self.slider_width-4, self.slider_height-4)

    def update(self):
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if mouse_buttons[0] and self.slider_border.collidepoint(mouse_pos):
            self.mag = min(max(mouse_pos[0] - self.x - self.slider_width//10,0) / (self.slider_width-self.slider_width//5),1)

    def get_value(self):
        return int(self.mag * 100)

    def draw(self,surface):
        pygame.draw.rect(surface, (255, 255, 255), self.slider_border)
        pygame.draw.rect(surface, (50, 50, 50), self.slider_background)

        self.slider = pygame.Rect(self.x+2+(self.mag)*(self.slider_width-self.slider_width//5-4)//1, self.y+2, self.slider_width//5, self.slider_height-4)
        pygame.draw.rect(surface, (255, 255, 255), self.slider)

        self.slider_icon = self.slider_icon_font.render('| | |', True, (0, 0, 0))
        surface.blit(self.slider_icon, (self.x+12+(self.mag)*(self.slider_width-self.slider_width//5-4)//1+(self.slider_width//5 - 40)//2, self.y+2+(self.slider_height-20)//2))

    def set_value(self, value):
        self.mag = value/100

class Button:
    def __init__(self,x,y,w,h,colour,function):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.colour = colour
        self.function = function

        self.__debounce = False

        self.frame = pygame.Rect(x, y, w, h)
    
    def update(self):
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if mouse_buttons[0] and self.frame.collidepoint(mouse_pos) and not self.__debounce:
            self.__debounce = True
            self.function()
        elif not mouse_buttons[0]:
            self.__debounce = False

    def draw(self,surface):
        pygame.draw.rect(surface, self.colour, self.frame)

class user_interface():
    def __init__(self, dimensions=(800, 480)):
        pygame.init()
        pygame.font.init()
        self.__screen = pygame.display.set_mode(dimensions)
        pygame.display.set_caption("LED Controller")

        self.__running = True
        self.__dimensions = dimensions

        self.__picker = ColorPicker(290,90,220,30)
        self.__brightness_slider = Slider(40, 110, 200, 25)
        self.__brightness_slider.set_value(100)
        self.__white_slider = Slider(300,150,200,25)
        self.__white_slider.set_value(0)

        self.__alarm_hour = 0
        self.__alarm_minute = 0

        self.led_on_off = False

        self.__LED_activation = True
        self.__weater_announcement = True
        self.__alarming = False

        self.__red_activated = True
        self.__green_activated = True
        self.__blue_activated = True
        self.__white_activated = True

        self.__alarm = False

        self.__on_off_button = Button(self.__dimensions[0]-50, 10, 40, 40, (0, 0, 0), self.toggle_led_on_off)
        self.__alarm_on_button = Button(120, 190, 50, 30, (0, 0, 0), self.alarm_on)
        self.__alarm_off_button = Button(180, 190, 50, 30, (0, 0, 0), self.alarm_off)
        self.__alarm_hour_up_button = Button(99, 242, 25, 23, (0, 0, 0), self.increase_alarm_hour)
        self.__alarm_hour_down_button = Button(99, 305, 25, 23, (0, 0, 0), self.decrease_alarm_hour)
        self.__alarm_minute_up_button = Button(163, 242, 25, 23, (0, 0, 0), self.increase_alarm_minute)
        self.__alarm_minute_down_button = Button(163, 305, 25, 23, (0, 0, 0), self.decrease_alarm_minute)
        self.__LED_activation_button = Button(220, 359, 20, 20, (0, 0, 0), self.toggle_LED_activation)
        self.__weater_announcement_button = Button(220, 404, 20, 20, (0, 0, 0), self.toggle_weather_announcement)
        self.__red_activation_button = Button(478, 308, 20, 20, (0, 0, 0), self.toggle_red_activation)
        self.__green_activation_button = Button(478, 343, 20, 20, (0, 0, 0), self.toggle_green_activation)
        self.__blue_activation_button = Button(478, 378, 20, 20, (0, 0, 0), self.toggle_blue_activation)
        self.__white_activation_button = Button(478, 413, 20, 20, (0, 0, 0), self.toggle_white_activation)

        self.colour = (0, 0, 0, 0)

    def get_brightness(self):
        return self.__brightness_slider.get_value()

    def update(self):
        if self.__white_slider.get_value() == 100 and self.__white_activated:
            white_value = 255
        elif self.__white_activated:
            white_value = int(self.__white_slider.get_value() * 2.55)
        else:
            white_value = 0
        if self.__red_activated:
            red_value = int(self.__picker.get_color().r)
        else:
            red_value = 0
        if self.__green_activated:
            green_value = int(self.__picker.get_color().g)
        else:
            green_value = 0
        if self.__blue_activated:
            blue_value = int(self.__picker.get_color().b)
        else:
            blue_value = 0
        self.colour = (red_value, green_value, blue_value, white_value)

        background = pygame.surface.Surface(self.__dimensions)
        background.fill((0, 0, 0))
        self.__screen.blit(background, (0, 0))

        title_font = pygame.font.SysFont(title_font_to_use, 32, bold=True)
        title_font_bigger = pygame.font.SysFont(title_font_to_use, 34, bold=True)
        title_font_smaller = pygame.font.SysFont(title_font_to_use, 30, bold=False)

        # Top left title
        if True:
            name = title_font.render("ATLAS", True, (255, 255, 255))
            L_title = title_font.render("L", True, (255, 0, 0))
            E_title = title_font.render("E", True, (0, 255, 0))
            D_title = title_font.render("D", True, (0, 0, 255))

            L_title_bigger = title_font_bigger.render("L", True, (255, 255, 255))
            E_title_bigger = title_font_bigger.render("E", True, (255, 255, 255))
            D_title_bigger = title_font_bigger.render("D", True, (255, 255, 255))

            self.__screen.blit(L_title_bigger, (80,1))
            self.__screen.blit(E_title_bigger, (95,1))
            self.__screen.blit(D_title_bigger, (112,1))

            self.__screen.blit(name,(1,1))
            self.__screen.blit(L_title, (80,1))
            self.__screen.blit(E_title, (95,1))
            self.__screen.blit(D_title, (112,1))

        # On/off button
        if True:
            self.__on_off_button.update()
            self.__on_off_button.draw(self.__screen)
            on_off_icon = pygame.image.load('power_icon.png')
            on_off_icon = pygame.transform.scale(on_off_icon, (40, 40))
            self.__screen.blit(on_off_icon, (self.__dimensions[0]-50, 10))

        # Brightness Section
        if True:
            border_width = 240
            border_length = 120
            brightness_border = pygame.Rect(20, 40, border_width, border_length)
            slider_border = pygame.Rect(22, 42, border_width-4, border_length-4)
            pygame.draw.rect(self.__screen, (255, 255, 255), brightness_border)
            pygame.draw.rect(self.__screen, (0, 0, 0), slider_border)

            brightness_title = title_font_smaller.render("Brightness", True, (255, 255, 255))
            self.__screen.blit(brightness_title, (25, 45))

            self.__brightness_slider.update()
            self.__brightness_slider.draw(self.__screen)

            brightness_icon = pygame.image.load('brightness_icon.png')
            brightness_icon_big = pygame.transform.scale(brightness_icon, (30, 30))
            self.__screen.blit(brightness_icon_big, (10+200,75))

            brightness_icon_small = pygame.transform.scale(brightness_icon, (20, 20))
            self.__screen.blit(brightness_icon_small, (40,85))

        # Alarm section
        if True:
            border_width = 240
            border_length = 270
            brightness_border = pygame.Rect(20, 180, border_width, border_length)
            slider_border = pygame.Rect(22, 182, border_width-4, border_length-4)
            pygame.draw.rect(self.__screen, (255, 255, 255), brightness_border)
            pygame.draw.rect(self.__screen, (0, 0, 0), slider_border)

            alarm_title = title_font_smaller.render("Alarm", True, (255, 255, 255))
            self.__screen.blit(alarm_title, (25, 190))

            self.__alarm_on_button.update()
            self.__alarm_on_button.draw(self.__screen)
            alarm_on_button_icon = pygame.Rect(120, 190, 50, 30)
            self.__alarm_off_button.update()
            self.__alarm_off_button.draw(self.__screen)
            alarm_off_button_icon = pygame.Rect(180, 190, 50, 30)
            if self.__alarm:
                pygame.draw.rect(self.__screen, (130, 130, 130), alarm_on_button_icon)
                pygame.draw.rect(self.__screen, (90, 90, 90), alarm_off_button_icon)
            else:
                pygame.draw.rect(self.__screen, (90, 90, 90), alarm_on_button_icon)
                pygame.draw.rect(self.__screen, (130, 130, 130), alarm_off_button_icon)
            on_button_text = title_font_smaller.render("ON", True, (255, 255, 255))
            self.__screen.blit(on_button_text, (129, 196))
            off_button_text = title_font_smaller.render("OFF", True, (255, 255, 255))
            self.__screen.blit(off_button_text, (185, 196))

            arrowhead = pygame.image.load('arrowhead.png')
            alarm_hour_background = pygame.Rect(86, 270, 50, 30)
            pygame.draw.rect(self.__screen, (101, 100, 100), alarm_hour_background)
            arrowhead = pygame.transform.scale(arrowhead, (25, 23))
            arrowhead_rotated = pygame.transform.rotate(arrowhead, 180)
            self.__alarm_hour_up_button.update()
            self.__alarm_hour_up_button.draw(self.__screen)
            self.__screen.blit(arrowhead, (99, 242))
            self.__alarm_hour_down_button.update()
            self.__alarm_hour_down_button.draw(self.__screen)
            self.__screen.blit(arrowhead_rotated, (99, 305))
            colon = title_font_smaller.render(":", True, (255, 255, 255))
            self.__screen.blit(colon, (140, 275))

            alarm_minute_background = pygame.Rect(150, 270, 50, 30)
            pygame.draw.rect(self.__screen, (100, 100, 100), alarm_minute_background)
            self.__alarm_minute_up_button.update()
            self.__alarm_minute_up_button.draw(self.__screen)
            self.__alarm_minute_down_button.update()
            self.__alarm_minute_down_button.draw(self.__screen)
            self.__screen.blit(arrowhead, (163, 242))
            self.__screen.blit(arrowhead_rotated, (163, 305))
            if self.__alarm_hour < 10:
                hour = "0"+str(self.__alarm_hour)
            else:
                hour = self.__alarm_hour
            if self.__alarm_minute < 10:
                minute = "0"+str(self.__alarm_minute)
            else:
                minute = self.__alarm_minute
            hour_text = title_font_smaller.render(str(hour), True, (255, 255, 255))
            minute_text = title_font_smaller.render(str(minute), True, (255, 255, 255))
            self.__screen.blit(hour_text, (100, 276))
            self.__screen.blit(minute_text, (163, 276))

            led_activation_text = title_font_smaller.render("LED Activation:", True, (255, 255, 255))
            self.__screen.blit(led_activation_text, (30, 360))
            led_activation_box = pygame.Rect(220, 359, 20, 20)
            self.__LED_activation_button.update()
            self.__LED_activation_button.draw(self.__screen)
            pygame.draw.rect(self.__screen, (100, 100, 100), led_activation_box)
            if self.__LED_activation:
                led_activation_x_text = title_font_smaller.render("X", True, (255, 255, 255))
                self.__screen.blit(led_activation_x_text, (223, 361)) 
            weather_announcement_text = title_font_smaller.render("Weather Update:", True, (255, 255, 255))
            self.__screen.blit(weather_announcement_text, (30, 405))
            weather_announcement_box = pygame.Rect(220, 404, 20, 20)
            self.__weater_announcement_button.update()
            self.__weater_announcement_button.draw(self.__screen)
            pygame.draw.rect(self.__screen, (100, 100, 100), weather_announcement_box)
            if self.__weater_announcement:
                weather_announcement_x_text = title_font_smaller.render("X", True, (255, 255, 255))
                self.__screen.blit(weather_announcement_x_text, (223, 406))

        # Colour section
        if True:
            border_width = 240
            border_length = 410
            brightness_border = pygame.Rect(280, 40, border_width, border_length)
            slider_border = pygame.Rect(282, 42, border_width-4, border_length-4)
            pygame.draw.rect(self.__screen, (255, 255, 255), brightness_border)
            pygame.draw.rect(self.__screen, (0, 0, 0), slider_border)
            colour_title = title_font_smaller.render("Colour", True, (255, 255, 255))
            self.__screen.blit(colour_title, (285, 45))

            self.__picker.update()
            self.__picker.draw(self.__screen)

            self.__white_slider.update()
            self.__white_slider.draw(self.__screen)

            red_value_background = pygame.Rect(296, 240, 40, 40)
            red_value_title = title_font_smaller.render("R", True, (255, 255, 255))
            self.__screen.blit(red_value_title, (308, 218))
            pygame.draw.rect(self.__screen, (100,100,100),red_value_background)
            if len(str(self.colour[0])) == 1:
                red_value = title_font_smaller.render("00"+str(self.colour[0]), True, (255, 60, 60))
            elif len(str(self.colour[0])) == 2:
                red_value = title_font_smaller.render("0"+str(self.colour[0]), True, (255, 60, 60))
            else:
                red_value = title_font_smaller.render(str(self.colour[0]), True, (255, 60, 60))
            self.__screen.blit(red_value, (300, 250))

            green_value_background = pygame.Rect(352, 240, 40, 40)
            green_value_title = title_font_smaller.render("G", True, (255, 255, 255))
            self.__screen.blit(green_value_title, (364, 218))
            pygame.draw.rect(self.__screen, (100,100,100),green_value_background)
            if len(str(self.colour[1])) == 1:
                green_value = title_font_smaller.render("00"+str(self.colour[1]), True, (60, 255, 60))
            elif len(str(self.colour[1])) == 2:
                green_value = title_font_smaller.render("0"+str(self.colour[1]), True, (60, 255, 60))
            else:
                green_value = title_font_smaller.render(str(self.colour[1]), True, (60, 255, 60))
            self.__screen.blit(green_value, (356, 250))

            blue_value_background = pygame.Rect(408, 240, 40, 40)
            blue_value_title = title_font_smaller.render("B", True, (255, 255, 255))
            self.__screen.blit(blue_value_title, (420, 218))
            pygame.draw.rect(self.__screen, (100,100,100),blue_value_background)
            if len(str(self.colour[2])) == 1:
                blue_value = title_font_smaller.render("00"+str(self.colour[2]), True, (0, 0, 255))
            elif len(str(self.colour[2])) == 2:
                blue_value = title_font_smaller.render("0"+str(self.colour[2]), True, (0, 0, 255))
            else:
                blue_value = title_font_smaller.render(str(self.colour[2]), True, (0, 0, 255))
            self.__screen.blit(blue_value, (412, 250))

            white_value_background = pygame.Rect(464, 240, 40, 40)
            white_value_title = title_font_smaller.render("W", True, (255, 255, 255))
            self.__screen.blit(white_value_title, (476, 218))
            pygame.draw.rect(self.__screen, (100,100,100),white_value_background)

            if len(str(self.colour[3])) == 1:
                white_value = title_font_smaller.render("00"+str(self.colour[3]), True, (255, 255, 255))
            elif len(str(self.colour[3])) == 2:
                white_value = title_font_smaller.render("0"+str(self.colour[3]), True, (255, 255, 255))
            else:
                white_value = title_font_smaller.render(str(self.colour[3]), True, (255, 255, 255))
            
            self.__screen.blit(white_value, (468, 250))

            red_toggle_title = title_font_smaller.render("Red Activated:", True, (255, 255, 255))
            self.__screen.blit(red_toggle_title, (290, 310))
            red_toggle_background = pygame.Rect(478, 308, 20, 20)
            self.__red_activation_button.update()
            self.__red_activation_button.draw(self.__screen)
            pygame.draw.rect(self.__screen, (100, 100, 100), red_toggle_background)
            red_toggle_x = title_font_smaller.render("X", True, (255, 255, 255))
            if self.__red_activated:
                self.__screen.blit(red_toggle_x, (481, 310))

            green_toggle_title = title_font_smaller.render("Green Activated:", True, (255, 255, 255))
            self.__screen.blit(green_toggle_title, (290, 345))
            green_toggle_background = pygame.Rect(478, 343, 20, 20)
            self.__green_activation_button.update()
            self.__green_activation_button.draw(self.__screen)
            pygame.draw.rect(self.__screen, (100, 100, 100), green_toggle_background)
            green_toggle_x = title_font_smaller.render("X", True, (255, 255, 255))
            if self.__green_activated:
                self.__screen.blit(green_toggle_x, (481, 345))

            blue_toggle_title = title_font_smaller.render("Blue Activated:", True, (255, 255, 255))
            self.__screen.blit(blue_toggle_title, (290, 380))
            blue_toggle_background = pygame.Rect(478, 378, 20, 20)
            self.__blue_activation_button.update()
            self.__blue_activation_button.draw(self.__screen)
            pygame.draw.rect(self.__screen, (100, 100, 100), blue_toggle_background)
            blue_toggle_x = title_font_smaller.render("X", True, (255, 255, 255))
            if self.__blue_activated:
                self.__screen.blit(blue_toggle_x, (481, 380))

            white_toggle_title = title_font_smaller.render("White Activated:", True, (255, 255, 255))
            self.__screen.blit(white_toggle_title, (290, 415))
            white_toggle_background = pygame.Rect(478, 413, 20, 20)
            self.__white_activation_button.update()
            self.__white_activation_button.draw(self.__screen)
            pygame.draw.rect(self.__screen, (100, 100, 100), white_toggle_background)
            white_toggle_x = title_font_smaller.render("X", True, (255, 255, 255))
            if self.__white_activated:
                self.__screen.blit(white_toggle_x, (481, 415))
            
        # Extras section
        if True:
            border_width = 240
            border_length = 380
            brightness_border = pygame.Rect(540, 70, border_width, border_length)
            slider_border = pygame.Rect(542, 72, border_width-4, border_length-4)
            pygame.draw.rect(self.__screen, (255, 255, 255), brightness_border)
            pygame.draw.rect(self.__screen, (0, 0, 0), slider_border)

        pygame.display.update()
    
    def increase_alarm_hour(self):
        if self.__alarm_hour == 23:
            self.__alarm_hour = 0
        else:
            self.__alarm_hour += 1

    def decrease_alarm_hour(self):
        if self.__alarm_hour == 0:
            self.__alarm_hour = 23
        else:
            self.__alarm_hour -= 1

    def increase_alarm_minute(self):
        if self.__alarm_minute == 59:
            self.__alarm_minute = 0
        else:
            self.__alarm_minute += 1
    
    def decrease_alarm_minute(self):
        if self.__alarm_minute == 0:
            self.__alarm_minute = 59
        else:
            self.__alarm_minute -= 1

    def toggle_weather_announcement(self):
        self.__weater_announcement = not self.__weater_announcement

    def toggle_LED_activation(self):
        self.__LED_activation = not self.__LED_activation

    def toggle_led_on_off(self):
        self.led_on_off = not self.led_on_off

    def alarm_on(self):
        self.__alarm = True
    
    def alarm_off(self):
        self.__alarm = False

    def toggle_red_activation(self):
        self.__red_activated = not self.__red_activated

    def toggle_green_activation(self):
        self.__green_activated = not self.__green_activated

    def toggle_blue_activation(self):
        self.__blue_activated = not self.__blue_activated

    def toggle_white_activation(self):
        self.__white_activated = not self.__white_activated

    def get_alarm_status(self):
        return self.__alarm

    def get_alarm_time(self):
        return self.__alarm_hour, self.__alarm_minute

    def get_weather_announcement(self):
        return self.__weater_announcement

    def get_LED_activation(self):
        return self.__LED_activation

class led_controller():
    def __init__(self):
        self.__colour = (0, 0, 0, 0)
        self.__brightness = 100
        self.__on_off = False

    def on(self):
        self.__on_off = True
        print('ON')

    def off(self):
        self.__on_off = False
        print('OFF')
    
    def __calculate_colour(self,colour=None,brightness=None):
        if colour == None:
            colour = self.__colour
        if brightness == None:
            brightness = self.__brightness
        return (int(colour[0] * (brightness/100)),int(colour[1] * (brightness/100)),int(colour[2] * (brightness/100)),int(colour[3] * (brightness/100)))


    def colour(self,colour):
        self.__colour = colour
        print(colour)
        if self.__on_off:
            pass # Change the live led colour using self.__calculate_colour
    
    def brightness(self,brightness):
        print(brightness)
        self.__brightness = brightness

class alarm_controller():
    def __init__(self, function, UI, pre_warning=0):
        self.__UI = UI
        self.__enabled = False
        self.__time = 0 #Number of mins after midnight
        self.__function = function
        self.__pre_warning = pre_warning
        self.__buffer = 5
        self.__activated = False
        self.__weather_announcement = False
        self.__led_activation = False
    
    def alarm(self,mins_past_midnight):
        time.sleep(self.__buffer)
        if mins_past_midnight == self.__time:
            self.__function(self.__led_activation,self.__weather_announcement)
    
    def update(self):
        self.__led_activation = self.__UI.get_LED_activation()
        self.__weather_announcement = self.__UI.get_weather_announcement()
        self.__enabled = self.__UI.get_alarm_status()
        hours, mins = self.__UI.get_alarm_time()
        self.__time = hours * 60 + mins - self.__pre_warning

        if self.__time < 0:
            self.__time += 1440
            
        if self.__enabled:
            current_time = datetime.datetime.now()
            mins_past_midnight = current_time.hour * 60 + current_time.minute
            if mins_past_midnight == self.__time and not self.__activated:
                self.__activated = True
                t = threading.Thread(target=self.alarm,args=(mins_past_midnight,))
                t.start()
            elif mins_past_midnight != self.__time:
                self.__activated = False       

UI = user_interface()
LED = led_controller()
alarm = alarm_controller(alarm_function, UI)

on_off = False
colour = (0,0,0,0)
brightness = 100

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    
    UI.update()
    alarm.update()

    if colour != UI.colour:
        colour = UI.colour
        LED.colour(colour)
    
    if brightness != UI.get_brightness():
        brightness = UI.get_brightness()
        LED.brightness(brightness)

    if UI.led_on_off != on_off and UI.led_on_off:
        on_off = UI.led_on_off
        LED.on()
    elif UI.led_on_off != on_off and not UI.led_on_off:
        on_off = UI.led_on_off
        LED.off()