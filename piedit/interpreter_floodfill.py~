#!/usr/bin/env python

"""Interpreter for the Piet programming language. Can be run directly or 
imported and used by the GUI"""

import sys
import gtk
import PIL.Image
import colors
import unionfind
import getchr

__author__ = "Steven Anderson"
__copyright__ = "Steven Anderson 2008"
__credits__ = ["Steven Anderson"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Steven Anderson"
__email__ = "steven.james.anderson@googlemail.com"
__status__ = "Production"

def print_usage():
    """Prints usage string for command line"""
    print "Usage: interpreter.py image"
        

class Interpreter:
    """The Piet interpreter class"""
    def __init__(self):
        """Sets up object properties"""
        self.current_pixel_coords = None
        self.dp = 0
        self.cc = 0
        self.switch_cc = True
        self.step = 0 #0 for just moved into color block, 1 for moved to edge
        self.times_stopped = 0
        self.max_steps = 1000000
        self.stack = []
        self.block_size = 0
        self.boundary_pixel_coords = None
        #Indexed by hue and light change
        self.operations = {
            (1,0):("Add",self.op_add),
            (2,0):("Divide",self.op_divide),
            (3,0):("Greater",self.op_greater),
            (4,0):("Duplicate",self.op_duplicate),
            (5,0):("IN(char)",self.op_in_char),
            (0,1):("Push",self.op_push),
            (1,1):("Subtract",self.op_subtract),
            (2,1):("Mod",self.op_mod),
            (3,1):("Pointer",self.op_pointer),
            (4,1):("Roll",self.op_roll),
            (5,1):("OUT(Number)",self.op_out_number),
            (0,2):("Pop",self.op_pop),
            (1,2):("Multiply",self.op_multiply),
            (2,2):("Not",self.op_not),
            (3,2):("Switch",self.op_switch),
            (4,2):("IN(Number)",self.op_in_number),
            (5,2):("OUT(Char)",self.op_out_char),
        }
    
    def run_program(self,path):
        """Runs a program at the given path"""
        print "Loading image"
        self.load_image(path)   
        print "Starting execution"
        self.start_execution()
        
    def load_image(self,path):
        """Loads an image and puts pixel data into self.pixels"""
        try:
            self.image = PIL.Image.open(path)
            if self.image.mode != "RGB":
                self.image = self.image.convert("RGB")
        except IOError:
            raise IOError, "IMAGE_NOT_LOADED"
        
        (self.width, self.height) = self.image.size
        rawpixels = self.image.getdata()
        self.pixels = dict([((x,y),colors.rgb_to_hex(rawpixels[y*(self.width)+x])) for x in range(self.width) for y in range(self.height)])
        #for x in range(self.width):
        #    for y in range(self.height):
        #        print "Pixel: (%s,%s) - %s" % (x,y,self.pixels[(x,y)])
        self.current_pixel_coords = (0,0)  
    
    def start_execution(self):
        """Starts the execution of the program"""
        for i in range(self.max_steps):
            self.do_next_step()
            
    def do_next_step(self):     
        """Executes a step in the program."""
        if self.step == 0:
            self.step = 1
            self.move_within_block()
            #print "DP: %s, CC:%s" % (self.dp, self.cc)            
            #print "Moved within block to %s,%s" % (self.current_pixel_coords[0],self.current_pixel_coords[1])
        elif self.step == 1:
            self.step = 0           
            self.move_out_of_block()  
            #print "DP: %s, CC:%s" % (self.dp, self.cc)             
            #print "Moved out of block to %s,%s" % (self.current_pixel_coords[0],self.current_pixel_coords[1])                     
        else:
            error_handler.handle_error("The step wasn't 0 or 1. That should never happen. This must be a bug in my code. Sorry")
            
    def move_within_block(self):
        """Moves to the border pixel within the current color block"""
        if colors.is_white(self.pixels[self.current_pixel_coords]):
            self.move_within_white()
        else:
            self.move_within_color()
    
    def move_within_white(self):
        """Slides through a white block until an obstruction or a
        new color block is found"""
        next_pixel = self.pixels[self.get_next_pixel_coords()]
        
        while colors.is_white(next_pixel):
            self.current_pixel_coords = self.get_next_pixel_coords()
            x,y = self.get_next_pixel_coords()
            
            if (x<0 or y<0 or x>=self.width or y>=self.height):
                self.hit_obstruction()
                return
            
            next_pixel = self.pixels[(x,y)]
            
    def move_within_color(self):
        """Moves within a color block to the required pixel
        at the max dp/cc direction"""
        coords = self.current_pixel_coords
        color = self.pixels[coords]
        #print "Start - looking for ",color
        self.block_size = 0
        self.boundary_pixel_coords = None
        self.floodfill(coords,color,"WTF")
        self.block_size = 0
        self.boundary_pixel_coords = None
        self.floodfill(coords,"WTF",color)
        self.current_pixel_coords = self.boundary_pixel_coords
        #print self.boundary_pixel_coords
        
    def floodfill(self,pixel_coords,from_color,to_color):
        """Recurively fills a color block with another color"""
        #print "Checking ",pixel_coords
        if pixel_coords[0] < 0\
            or pixel_coords[0] >= self.width\
            or pixel_coords[1] < 0\
            or pixel_coords[1] >= self.height:
                return
            
        pixel = self.pixels[pixel_coords]
        #print "Looking at ",pixel_coords,"Color = ",pixel,"From = ", from_color,"Target = ", to_color
        if pixel == to_color\
            or pixel != from_color: 
                #print "Nope"
                return
        else:
            #print "Yep"
            self.pixels[pixel_coords] = to_color
            self.block_size = self.block_size + 1
            self.update_boundary_pixel(pixel_coords)
            #print "Boundary: ",self.boundary_pixel_coords
            self.floodfill((pixel_coords[0]-1,pixel_coords[1]),from_color,to_color)
            self.floodfill((pixel_coords[0]+1,pixel_coords[1]),from_color,to_color)
            self.floodfill((pixel_coords[0],pixel_coords[1]-1),from_color,to_color)
            self.floodfill((pixel_coords[0],pixel_coords[1]+1),from_color,to_color)
            
    def update_boundary_pixel(self,pixel_coords):
        """Modifies the boundary pixel for the current dp and cc"""
        if self.boundary_pixel_coords == None:
            self.boundary_pixel_coords = pixel_coords
            return
        
        x,y = pixel_coords
        c_x,c_y = self.boundary_pixel_coords
        if self.dp == 0:
            if x > c_x:
                self.boundary_pixel_coords = (x,y)
            elif x == c_x:
                if (self.cc == 0 and y < c_y)\
                    or (self.cc == 1 and y > c_y):
                        self.boundary_pixel_coords = (x,y)
        elif self.dp == 1:
            if y > c_y:
                self.boundary_pixel_coords = (x,y)
            elif y == c_y:
                if (self.cc == 0 and x > c_x)\
                    or (self.cc == 1 and x < c_x):
                        self.boundary_pixel_coords = (x,y)
        elif self.dp == 2:
            if x < c_x:
                self.boundary_pixel_coords = (x,y)
            elif x == c_x:
                if (self.cc == 0 and y > c_y)\
                    or (self.cc == 1 and y < c_y):
                        self.boundary_pixel_coords = (x,y)
        elif self.dp == 3:
            if y < c_y:
                self.boundary_pixel_coords = (x,y)
            elif y == c_y:
                if (self.cc == 0 and x < c_x)\
                    or (self.cc == 1 and x > c_x):
                        self.boundary_pixel_coords = (x,y)
            
    def move_out_of_block(self):
        """Moves out of a color block and into the next color block, performing
        the operation if necessary"""
        
        #If we're at a wall
        x,y = self.current_pixel_coords
        if (self.dp == 0 and x >= self.width-1)\
            or (self.dp == 1 and y >= self.height-1)\
            or (self.dp == 2 and x <= 0)\
            or (self.dp == 3 and y <= 0):
                self.hit_obstruction()
                return
        
        current_pixel = self.pixels[(x,y)]
        next_pixel_coords = self.get_next_pixel_coords()
        next_pixel = self.pixels[next_pixel_coords]
        #If we're at a black pixel
        if colors.is_black(next_pixel):
            self.hit_obstruction()
            return
            
        if colors.is_white(current_pixel)\
            or colors.is_white(next_pixel):
                pass
        else:
            #Get the operation to do
            hue_light_diff = colors.hue_light_diff(current_pixel,next_pixel)
            op_name, op = self.operations[hue_light_diff]
            #print op_name
            op()
        self.current_pixel_coords = next_pixel_coords
        self.times_stopped = 0
        self.switch_cc = True
                    
            
    def get_next_pixel_coords(self):
        """Returns the next pixel in the direction of the dp"""
        x,y = self.current_pixel_coords
        if self.dp == 0:
            return (x+1,y)
        elif self.dp == 1:
            return (x,y+1)
        elif self.dp == 2:
            return (x-1,y)
        elif self.dp == 3:
            return (x,y-1)
        else:
            error_handler.handle_error("The DP managed to become none of 0,1,2,3. This is a bug. Sorry")
        
        
    def hit_obstruction(self):
        """Handles the case when an obstruction is the next pixel."""
        self.times_stopped = self.times_stopped + 1
        self.step = 0
        if (self.times_stopped >= 8):
            self.stop_execution()
        else:
            if self.switch_cc:
                self.toggle_cc()
                self.switch_cc = False
            else:
                self.rotate_dp(1)
                self.switch_cc = True
    
    def stop_execution(self):
        """Cancels execution of the program"""
        print "\nExecution finished"
        sys.exit(1)
        
    def toggle_cc(self):
        """Toggles the cc"""
        #print "Toggling cc"
        div,mod = divmod(1-self.cc,1)
        self.cc = div
    
    def rotate_dp(self,times=1):
        """Rotates the dp by the given number of times"""
        #print "Rotating dp"
        div,mod = divmod(self.dp+times,4)
        self.dp = mod
        
    #Below are the actual operation methods for the piet language.
    def op_add(self):
        """Piet Add operation"""
        if len(self.stack) >= 2:
            item1 = self.stack.pop()
            item2 = self.stack.pop()
            self.stack.append(item1+item2)
    
    def op_divide(self):
        """Piet Divide operation"""
        if len(self.stack) >= 2:
            top_item = self.stack.pop()
            second_item = self.stack.pop()
            self.stack.append(second_item//top_item)
    
    def op_greater(self):
        """Piet Greater operation"""
        if len(self.stack) >= 2:
            top_item = self.stack.pop()
            second_item = self.stack.pop()
            self.stack.append(int(second_item>top_item))
            
    def op_duplicate(self):
        """Piet Duplicate operation"""
        if len(self.stack) >=1:
            item = self.stack[-1]
            self.stack.append(item)
    
    def op_in_char(self):
        """Piet IN(CHAR) operation"""
        chr = getchr.get_chr()
        self.stack.append(ord(chr))
    
    def op_push(self):
        """Piet Push operation"""
        self.stack.append(self.block_size)
    
    def op_subtract(self):
        """Piet Subtract operation"""
        if len(self.stack) >= 2:
            top_item = self.stack.pop()
            second_item = self.stack.pop()
            self.stack.append(second_item-top_item)
    
    def op_mod(self):
        """Piet Mod operation"""
        if len(self.stack) >= 2:
            top_item = self.stack.pop()
            second_item = self.stack.pop()
            self.stack.append(second_item % top_item)
    
    def op_pointer(self):
        """Piet Pointer operation"""
        if len(self.stack) >= 1:
            item = self.stack.pop()
            self.rotate_dp(item)
    
    def op_roll(self):
        """Piet Roll operation"""
        if len(self.stack) >= 2:
            num_rolls = self.stack.pop()
            depth = self.stack.pop()    
            if depth >0:
                for i in range(abs(num_rolls)):
                    self.roll(depth,num_rolls<0)    
    
    def roll(self,depth,reverse):
        """Does a single roll"""
        if depth > len(self.stack):
            depth = len(self.stack)

        if reverse:
            bottom_item = self.stack[0]
            index = depth
            for i in range(index):
                self.stack[i] = self.stack[i+1]
            self.stack[index] = bottom_item
        else:
            top_item = self.stack[-1]
            index = len(self.stack)-depth
            for i in range(len(self.stack)-1,index,-1):
                self.stack[i] = self.stack[i-1]    
            self.stack[index] = top_item
    
    def op_out_number(self):
        """Piet OUT(NUM) operation"""
        if len(self.stack) >=1:
            item = self.stack.pop()
            sys.stdout.write(str(item))
    
    def op_pop(self):
        """Piet Pop operation"""
        if len(self.stack) >=1:
            self.stack.pop()
    
    def op_multiply(self):
        """Piet Multiply operation"""
        if len(self.stack) >= 2:
            item1 = self.stack.pop()
            item2 = self.stack.pop()
            self.stack.append(item1*item2)
    
    def op_not(self):
        """Piet Not operation"""
        if len(self.stack) >= 1:
            item = self.stack.pop()
            self.stack.append(int(not item))
    
    def op_switch(self):
        """Piet Switch operation"""
        if len(self.stack) >=1:
            item = self.stack.pop()
            for i in range(item):
                self.toggle_cc()
    
    def op_in_number(self):
        """Piet IN(NUM) operation"""
        char = getchr.get_chr()
        try:
            self.stack.append(int(char))
        except ValueError:
            pass      
    
    def op_out_char(self):
        """Piet OUT(CHAR) operation"""
        if len(self.stack) >=1:
            item = self.stack.pop()
            sys.stdout.write(chr(item))
        
    
class ErrorHandler:
    """Class that handles errors for the interpreter. Does it differently
    for UI and command line modes"""
    
    def __init__(self, isGUI=False):
        """Sets object properties"""
        self.isGUI = isGUI
        
    def handle_error(self,message):
        """Handles an error with the given message"""
        if not self.isGUI:
            raise SystemExit("\nError: "+message)
        else:
            pass
    
#Run the program if on command line
if __name__ == "__main__":
    error_handler = ErrorHandler(False)
    interpreter = Interpreter()
    if len(sys.argv)>1:
        interpreter.run_program(sys.argv[1])
    else:
        print_usage()