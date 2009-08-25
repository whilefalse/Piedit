#!/usr/bin/env python

"""Interpreter for the Piet programming language. Can be run directly or 
imported and used by the GUI."""

import sys
import getopt
import gtk
import PIL.Image
import colors
import unionfind
import getchr
import debug

__author__ = "Steven Anderson"
__copyright__ = "Steven Anderson 2008"
__credits__ = ["Steven Anderson"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Steven Anderson"
__email__ = "steven.james.anderson@googlemail.com"
__status__ = "Production"


class Interpreter:
    """The Piet interpreter class"""
    def __init__(self, max_steps=1000000, thread=None):
        """Initalizes new Interpreter."""
        self.current_pixel = None
        self.dp = 0
        self.cc = 0
        self.switch_cc = True
        self.step = 0 #0 for just moved into color block, 1 for moved to edge
        self.times_stopped = 0
        self.max_steps = max_steps
        self.current_step = 0
        self.stack = []
        self.color_blocks = {}
        self.finished = False
        self.thread = thread
        self.debug = debug.Debug(False)
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
    
    def init(self):
        self.__init__()
        
    def set_opt(self,o,a):
        """Sets an option from the command line."""
        if o in ["-d", "--debug"]:
            self.debug.DEBUG = True
        elif o in ["-m","--maxsteps"]:
            self.max_steps = int(a)
    
    def run_program(self,path=None,pixels=None,width=None,height=None,start=True):
        """Runs a program at the given path."""
        self.debug.writeln("---LOADING IMAGE %s...---" % (path))
        if pixels != None:
            self.width = width
            self.height = height
            self.pixels = [[Pixel(x,y,pixels[y*(self.width)+x]) for y in xrange(self.height)] for x in xrange(self.width)]
            self.current_pixel = self.pixels[0][0]
        else:
            self.load_image(path)   
        self.debug.writeln("---IMAGE LOADED---\n")
        self.debug.writeln("---SCANNING COLOR BLOCKS---")
        self.find_color_blocks()
        self.debug.writeln("---COLOR BLOCKS SCANNED---\n")
        self.debug.writeln("---STARTING EXECUTION---")
        self.debug.writeln("AT (%s,%s), COLOR=%s, DP=%d, CC=%s"\
            % (self.current_pixel.x,self.current_pixel.y,self.current_pixel.color,\
            self.dp, self.cc))
        if start:
            self.start_execution()
        else:
            pass
        
    def load_image(self,path):
        """Loads an image and puts pixel data into self.pixels."""
        try:
            self.image = PIL.Image.open(path)
            if self.image.mode != "RGB":
                self.image = self.image.convert("RGB")
        except IOError:
            raise IOError, "IMAGE_NOT_LOADED"
        
        (self.width, self.height) = self.image.size
        rawpixels = self.image.getdata()
        self.pixels = [[Pixel(x,y,colors.rgb_to_hex(rawpixels[y*(self.width)+x])) for y in xrange(self.height)] for x in xrange(self.width)]
        self.current_pixel = self.pixels[0][0]
        
    def find_color_blocks(self):
        """Uses the connected component algorithm to build the program color blocks."""
        next_label = 0
        #Pass 1
        for y in xrange(self.height):
            for x in xrange(self.width):
                pixel = self.pixels[x][y]
                if not self.is_background(pixel.color):
                    neighbours = self.neighbours(pixel)
                    
                    if neighbours == []:
                        pixel.parent = self.pixels[x][y]
                        pixel.set_label = next_label
                        next_label = next_label + 1
                    else:
                        for n in neighbours:
                            unionfind.union(n,pixel)
        
        #Pass 2
        for y in xrange(self.height):
            for x in xrange(self.width):
                pixel = self.pixels[x][y]
                if not self.is_background(pixel.color):
                    root = unionfind.find(pixel)
                    pixel.set_size = root.set_size
                    pixel.set_label = root.set_label
                    #Build color block object
                    if not self.color_blocks.has_key(pixel.set_label):
                        self.color_blocks[pixel.set_label] = ColorBlock(pixel.set_size)
                    self.color_blocks[pixel.set_label].update_boundaries(pixel)
    
        #Debug
        for i,color_block in self.color_blocks.items():
            bounds = color_block.boundary_pixels
            self.debug.writeln("Color Block %s: Size=%s, \n\tmaxRL=(%s,%s), maxRR=(%s,%s), \n\tmaxDL=(%s,%s), maxDR=(%s,%s), \n\tmaxLL=(%s,%s), maxLR=(%s,%s), \n\tmaxUL=(%s,%s), maxUR=(%s,%s)" \
                % (i, color_block.size, 
                   bounds[0][0].x,bounds[0][0].y, bounds[0][1].x, bounds[0][1].y,
                   bounds[1][0].x,bounds[1][0].y, bounds[1][1].x, bounds[1][1].y,
                   bounds[2][0].x,bounds[2][0].y, bounds[2][1].x, bounds[2][1].y,
                   bounds[3][0].x,bounds[3][0].y, bounds[3][1].x, bounds[3][1].y))
                    
    def is_background(self,color):
        """Tells us if the given color is black or white."""
        if  colors.is_white(color) or colors.is_black(color):
            return True
        else:
            return False
        
    def neighbours(self,pixel):
        """Finds the neighbours of the given pixel with the same label."""
        neighbours = []
        index = 0;
        x = pixel.x
        y = pixel.y
            
        if y !=0 and self.pixels[x][y-1].color == pixel.color:
            #Add above pixel
            index = index + 1
            neighbours.append(self.pixels[x][y-1])
        
        if x != 0 and self.pixels[x-1][y].color == pixel.color:
            #Add left pixel
            neighbours.append(self.pixels[x-1][y])
            index = index + 1
            
        return neighbours      
    
    def start_execution(self):
        """Starts the execution of the program."""
        if self.max_steps == -1:
            while not self.finished:
                self.do_next_step()
        else:
            for i in xrange(self.max_steps):
                self.do_next_step()
                if self.finished:
                    return
            self.debug.writeln("---EXECUTION FINISHED (Max Steps Reached)---")
            
    def do_next_debug_step(self):
        if self.max_steps == -1:
            self.do_next_step()
        else:
            if self.current_step < self.max_steps:
                self.do_next_step()
            else:
                return False
                self.debug.writeln("---EXECUTION FINISHED (Max Steps Reached)---")
        if self.finished:
            return False
        else:
            return True
            
    def do_next_step(self,step=None):     
        """Executes a step in the program."""
        if self.thread != None:
            if self.thread.should_stop:
                self.debug.writeln()
                self.debug.writeln("---EXECUTION FINISHED (Thread was stopped)---")
                self.finished = True
                return
        self.current_step = self.current_step + 1
        if self.step == 0:
            self.debug.writeln("  -> Moving within color block...")
            self.step = 1
            self.move_within_block()         
        elif self.step == 1:
            self.debug.writeln("  -> Moving out of color block...")
            self.step = 0           
            self.move_out_of_block()               
        else:
            error_handler.handle_error("The step wasn't 0 or 1. That should never happen. This must be a bug in my code. Sorry")
        if not self.finished:
            self.debug.writeln()
            self.debug.writeln("AT (%s,%s), COLOR=%s, DP=%d, CC=%s"\
                % (self.current_pixel.x,self.current_pixel.y,self.current_pixel.color,\
                self.dp, self.cc))
            
    def move_within_block(self):
        """Moves to the border pixel within the current color block."""
        if colors.is_white(self.current_pixel.color):
            self.move_within_white()
        else:
            self.move_within_color()
    
    def move_within_white(self):
        """Slides through a white block until an obstruction or a
        new color block is found."""
        x,y = self.next_pixel_coords()
        if not self.is_pixel_obstruction(x,y):
            return
        next_pixel = self.pixels[x][y]
        
        while colors.is_white(next_pixel.color):
            self.current_pixel = next_pixel
            x,y = self.next_pixel_coords()
            if not self.is_pixel_obstruction(x,y):
                return
            next_pixel = self.pixels[x][y]
            
    def is_pixel_obstruction(self,x,y):
        """Tells us whether the pixel at the given x and y is an obstruction."""
        if (x<0 or y<0 or x>=self.width or y>=self.height):
            self.hit_obstruction()
            return False
        return True
            
    def move_within_color(self):
        """Moves within a color block to the required pixel
        at the max dp/cc direction."""
        self.current_pixel = self.color_blocks\
            [self.current_pixel.set_label].boundary_pixels\
            [self.dp][self.cc]
            
    def move_out_of_block(self):
        """Moves out of a color block and into the next color block, performing
        the operation if necessary."""
        x,y = self.current_pixel.x, self.current_pixel.y
        n_x,n_y = self.next_pixel_coords()
        
        self.debug.writeln("  -> Trying to cross from (%s,%s) to (%s,%s)"\
            %(x,y,n_x,n_y))
        
        #If we're at a wall
        if (self.dp == 0 and x >= self.width-1)\
            or (self.dp == 1 and y >= self.height-1)\
            or (self.dp == 2 and x <= 0)\
            or (self.dp == 3 and y <= 0):
                self.hit_obstruction()
                return
        
        current_pixel = self.current_pixel
        next_pixel = self.pixels[n_x][n_y]
        #If we're at a black pixel
        if colors.is_black(next_pixel.color):
            self.hit_obstruction()
            return
            
        if colors.is_white(current_pixel.color)\
            or colors.is_white(next_pixel.color):
                pass
        else:
            #Get the operation to do
            hue_light_diff = colors.hue_light_diff(current_pixel.color,next_pixel.color)
            op_name, op = self.operations[hue_light_diff]
            self.debug.writeln("  -> Crossing from (%s,%s), color=%s to (%s,%s), color=%s"\
                % (current_pixel.x, current_pixel.y, current_pixel.color,\
                next_pixel.x, next_pixel.y, next_pixel.color))
            self.debug.writeln("  -> Stack before %s = %s" % (op_name.upper(),self.stack))
            self.debug.writeln("  -> Performing %s" % (op_name.upper()))
            op()
            self.debug.writeln("  -> Stack after %s = %s" % (op_name.upper(),self.stack))
        self.current_pixel = next_pixel
        self.times_stopped = 0
        self.switch_cc = True
    
    def next_pixel_coords(self):
        """Returns the coordinates of the next pixel in the direction of the dp."""
        x,y = self.current_pixel.x, self.current_pixel.y
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
        self.debug.writeln("  -> Hit an obstruction")
        self.times_stopped = self.times_stopped + 1
        self.debug.writeln("  -> Obstructions Hit = %i" % (self.times_stopped))
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
        """Cancels execution of the program."""
        self.debug.writeln("---EXECUTION FINISHED---")
        self.finished = True
        
    def toggle_cc(self):
        """Toggles the cc."""
        self.debug.writeln("  -> Toggling CC")
        div,mod = divmod(1-self.cc,1)
        self.cc = div
    
    def rotate_dp(self,times=1):
        """Rotates the dp by the given number of times."""
        self.debug.writeln("  -> Rotating DP by %s" % times)
        div,mod = divmod(self.dp+times,4)
        self.dp = mod
        
    #Below are the actual operation methods for the piet language.
    def op_add(self):
        """Piet Add operation."""
        if len(self.stack) >= 2:
            item1 = self.stack.pop()
            item2 = self.stack.pop()
            self.stack.append(item1+item2)
    
    def op_divide(self):
        """Piet Divide operation."""
        if len(self.stack) >= 2:
            top_item = self.stack.pop()
            second_item = self.stack.pop()
            self.stack.append(second_item/top_item)
    
    def op_greater(self):
        """Piet Greater operation."""
        if len(self.stack) >= 2:
            top_item = self.stack.pop()
            second_item = self.stack.pop()
            self.stack.append(int(second_item>top_item))
            
    def op_duplicate(self):
        """Piet Duplicate operation."""
        if len(self.stack) >=1:
            item = self.stack[-1]
            self.stack.append(item)
    
    def op_in_char(self):
        """Piet IN(CHAR) operation."""
        chr = getchr.get_chr()
        self.stack.append(ord(chr))
    
    def op_push(self):
        """Piet Push operation."""
        self.stack.append(self.current_pixel.set_size)
    
    def op_subtract(self):
        """Piet Subtract operation."""
        if len(self.stack) >= 2:
            top_item = self.stack.pop()
            second_item = self.stack.pop()
            self.stack.append(second_item-top_item)
    
    def op_mod(self):
        """Piet Mod operation."""
        if len(self.stack) >= 2:
            top_item = self.stack.pop()
            second_item = self.stack.pop()
            self.stack.append(second_item % top_item)
    
    def op_pointer(self):
        """Piet Pointer operation."""
        if len(self.stack) >= 1:
            item = self.stack.pop()
            self.rotate_dp(item)
    
    def op_roll(self):
        """Piet Roll operation."""
        if len(self.stack) >= 2:
            num_rolls = self.stack.pop()
            depth = self.stack.pop()    
            if depth >0:
                for i in xrange(abs(num_rolls)):
                    self.roll(depth,num_rolls<0)    
    
    def roll(self,depth,reverse):
        """Does a single roll."""
        if depth > len(self.stack):
            depth = len(self.stack)

        if reverse:
            bottom_item = self.stack[0]
            index = depth
            for i in xrange(index):
                self.stack[i] = self.stack[i+1]
            self.stack[index] = bottom_item
        else:
            top_item = self.stack[-1]
            index = len(self.stack)-depth
            for i in xrange(len(self.stack)-1,index,-1):
                self.stack[i] = self.stack[i-1]    
            self.stack[index] = top_item
    
    def op_out_number(self):
        """Piet OUT(NUM) operation."""
        if len(self.stack) >=1:
            item = self.stack.pop()
            sys.stdout.write(str(item))
            sys.stdout.flush()
    
    def op_pop(self):
        """Piet Pop operation."""
        if len(self.stack) >=1:
            self.stack.pop()
    
    def op_multiply(self):
        """Piet Multiply operation."""
        if len(self.stack) >= 2:
            item1 = self.stack.pop()
            item2 = self.stack.pop()
            self.stack.append(item1*item2)
    
    def op_not(self):
        """Piet Not operation."""
        if len(self.stack) >= 1:
            item = self.stack.pop()
            self.stack.append(int(not item))
    
    def op_switch(self):
        """Piet Switch operation."""
        if len(self.stack) >=1:
            item = self.stack.pop()
            for i in xrange(item):
                self.toggle_cc()
    
    def op_in_number(self):
        """Piet IN(NUM) operation."""
        char = getchr.get_chr()
        try:
            self.stack.append(int(char))
        except ValueError:
            pass      
    
    def op_out_char(self):
        """Piet OUT(CHAR) operation."""
        if len(self.stack) >=1:
            item = self.stack.pop()
            sys.stdout.write(chr(item))
            sys.stdout.flush()
    
    
class ColorBlock:
    """Class that represents a color block in a Piet program."""
    def __init__(self,size):
        """Initializes new ColorBlock."""
        self.size = size
        #boundary_pixels = [[DPR_CCL,DPR_CCR],[DPD_CCL,DPD,CCR] ... etc.
        self.boundary_pixels = [[None,None] for i in xrange(4)]
        
    def update_boundaries(self,pixel):
        """Updates the boundary pixels of the current color block given a new pixel."""
        #If a new maximum (right, left)
        if self.boundary_pixels[0][0] == None or pixel.x > self.boundary_pixels[0][0].x:
            self.boundary_pixels[0][0] = pixel
            
        #If a new maximum (right, right)
        if self.boundary_pixels[0][1] == None or pixel.x >= self.boundary_pixels[0][1].x:
            self.boundary_pixels[0][1] = pixel
            
        #If a new maximum (down, right)
        if self.boundary_pixels[1][1] == None or pixel.y > self.boundary_pixels[1][1].y:
            self.boundary_pixels[1][1]= pixel
        
        #If a new maximum (down, left)
        if self.boundary_pixels[1][0] == None or pixel.y >= self.boundary_pixels[1][0].y:
            self.boundary_pixels[1][0] = pixel
            
        #If a new maximum (left, right)
        if self.boundary_pixels[2][1] == None or pixel.x < self.boundary_pixels[2][1].x:
            self.boundary_pixels[2][1] = pixel
        
        #If a new maximum (left, left)
        if self.boundary_pixels[2][0] == None or pixel.x <= self.boundary_pixels[2][0].x:
            self.boundary_pixels[2][0] = pixel
            
        #If a new maximum (up,left)
        if self.boundary_pixels[3][0] == None:
            self.boundary_pixels[3][0] = pixel
            
        #If a new maximum (up,right)
        if self.boundary_pixels[3][1] == None or pixel.y == self.boundary_pixels[3][1].y:
            self.boundary_pixels[3][1] = pixel
                
             
class Pixel:
    """Class that represents a pixel in a Piet program (stricly a codel, but 
    the convention is 1 pixel per codel."""
    
    def __init__(self,x,y,color):
        """Initializes new Pixel."""
        self.x = x
        self.y = y
        self.color = color
        self.parent = self   
        self.set_size = 1
        self.set_label = -1
        
    
class ErrorHandler:
    """Class that handles errors for the interpreter. Does it differently
    for UI and command line modes."""
    
    def __init__(self, isGUI=False):
        """Initalizes new ErrorHandler."""
        self.isGUI = isGUI
        
    def handle_error(self,message):
        """Handles an error with the given message"""
        if not self.isGUI:
            raise SystemExit("\nError: "+message)
        else:
            pass


def print_usage():
    """Prints usage string for command line."""
    print "Piedit v0.0.1 - Python Piet IDE\n"
    print "Usage: interpreter.py [<options>] <filename>"
    print "options:"
    print "\t-h (--help)\t- Prints this help"
    print "\t-d (--debug)\t- Prints debug information"
    print "\t-m (--maxsteps)\t- Sets maximum steps to execute. This is 10^6 by default. Set to -1 for infinite."

def getopts():
    """Parses the command line options."""
    try:
       return getopt.getopt(sys.argv[1:], "hdm:", ["help","debug","maxsteps="])
    except getopt.GetoptError, err:
        print str(err)
        print_usage()
        sys.exit(2)

#Run the program if on command line
if __name__ == "__main__":
    try:
        error_handler = ErrorHandler(False)
        interpreter = Interpreter()
        if len(sys.argv)>1:
        
            opts,args = getopts()
            for o,a in opts:
                if o in ["-h","--help"]:
                    print_usage()
                    sys.exit(1)
                else:
                    interpreter.set_opt(o,a)
            if len(args) != 1:
                print_usage()
                sys.exit(2)
            interpreter.run_program(args[0])
        else:
            print_usage()
    except KeyboardInterrupt:
        print "\n\nTerminated"
