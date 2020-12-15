import pygame , sys
from pygame.locals import *

from math import sin, cos, tan, pi, atan as arctan, exp, log
from time import sleep, time
from random import uniform, randint

# general informations and other help functions which does not deserve their own class
class Misc():

    # varibles :
    window_width = int(1300)
    window_length = int(800)
    last_time = float(0)
    framerate = int(60)
    skiped_frames = int(0)
    death_counter = int(0)
    statistics_circle_size = int(2)

    # report each frame
    def report(self,frame):
        
        # world wide mass (everything)
        world_wide_mass = 0
        
        # calculates combined mass for blobs
        blob_total_mass = 0
        for blob in population:

            blob_total_mass += blob.mass
        
        world_wide_mass += blob_total_mass
        
        # calculates combined mass for plants
        plant_total_mass = 0
        for plant in plant_pop:

            plant_total_mass += plant.mass

        world_wide_mass += plant_total_mass
        
        # calculates combined mass for chunks
        biomass = 0
        for x in range(0,13):
            for y in range(0,8):
                biomass += ENV.chunks[x][y].biomass
        
        world_wide_mass += biomass


        print("frame : ", frame, end = '')
        print("  blobs mass : ", int(blob_total_mass) / 1000, "k  plants mass : ", int(plant_total_mass) / 1000, "k  chunks mass : ", int(biomass) / 1000, "k  world mass : ", int ( ENV.world_mass ), "  total world wide mass : ", int ( world_wide_mass ), "  death counter : ", self.death_counter, end = '')
        print('')
    
    # simply return the biggest number in an array
    def get_biggest_num(array):

        biggest = 0
        for num in array:

            if num > biggest:

                biggest = num

        return biggest

# conatins a few RGB presets
class Colors:
    # colors are determend by the RGB pricipal, ranging from 0 to 255 [red,green,blue]
    black = [0,0,0]
    blue = [0,0,255]
    green = [0,128,0]
    lime = [0,255,0]
    teal = [0,128,128]
    red = [255,0,0]

# deals with the Collision such as plants/blobs and blobs/blobs
class Collision():

    # collision detection betwen planrs and blob
    # if blob is in eating distance of a plant, return index for plant
    def check_overlap(blob, plant_pop): 

        eating = -1
        timer = 0
        for plant in plant_pop:

            dx = plant.x - blob.x
            dy = plant.y - blob.y

            distance = ((dx ** 2) + (dy ** 2)) ** 0.5
            total_r = blob.radius + plant.radius

            if distance < total_r / 2:
        
                eating = timer 

            timer += 1

        return eating


    # only checks when a blob is searching for a mate
    # returns "__true__" if the partner is in range for reproduction
    def check_sex(blob, mate):

        reproduction = "__false__"

        dx = mate.x - blob.x
        dy = mate.y - blob.y

        distance = ((dx ** 2) + (dy ** 2)) ** 0.5
        total_r = blob.radius + mate.radius
        if distance < total_r:
    
            reproduction = "__true__"

        return reproduction

# the ai class is only used by blob objects, also it's spaghetti code
class Ai():

    # standard ai stance, will go towards nearest food source
    def hungry(self,blob):


        if blob.target_plant == 0:
            # tries to find food within a cetain radius
            timer = 0
            best_distance = blob.sight
            food = "__N/A__"
            for plant in plant_pop:

                dx = plant.x - blob.x
                dy = plant.y - blob.y

                distance = ((dx ** 2) + (dy ** 2)) ** 0.5

                if distance < best_distance:




                    best_distance = distance
                    food = timer

                timer += 1

            if food != "__N/A__":


                plant = plant_pop[food]
                blob.target_plant = plant


                dx = plant.x - blob.x
                dy = plant.y - blob.y




                alpha = arctan(dy/dx)




                if dx < 0:
                
                    alpha += pi


                blob.angle = pi/2 -alpha


            else:
                self.friend_search(blob)
            
        self.move(blob)


    # reproduce ai stance, will go towards nearest blob with the same stance
    def mate_search(self,blob):

        if blob.target_mate == 0:
            # tries to find love within a cetain radius
            timer = 0
            best_distance = blob.sight
            bride = "__N/A__"
            for partner in population:


                if partner is blob:
                
                    pass
                elif partner.ai_stance == "__mate_search__":




                    dx = partner.x - blob.x
                    dy = partner.y - blob.y




                    distance = ((dx ** 2) + (dy ** 2)) ** 0.5




                    if distance < best_distance:




                        best_distance = distance
                        bride = timer




                timer += 1

            #-----

            if bride != "__N/A__":



                partner = population[bride]
                blob.target_mate = partner


                dx = partner.x - blob.x
                dy = partner.y - blob.y


                alpha = arctan(dy/dx)




                if dx < 0:
                
                    alpha += pi


                blob.angle = pi/2 -alpha


            else:

                self.friend_search(blob)


        elif Collision.check_sex(blob, blob.target_mate) ==  "__true__":
            #child making
            blob.reproduce( blob.target_mate )




        self.move(blob)
    
    # boid ai stance, prevents blobs from going
    def friend_search(self, blob):
        timer = 0
        best_distance = blob.sight
        BFF = -1
        for friend in population:

            if friend is not blob:

                dx = friend.x - blob.x
                dy = friend.y - blob.y
                distance = ((dx ** 2) + (dy ** 2)) ** 0.5

                if distance < best_distance:

                    best_distance = distance
                    BFF = timer


            timer += 1


        if BFF != -1:
            blob.angle = population[BFF].angle + uniform(-0.2,0.2)
        else:
            blob.angle += uniform(-0.2,0.2)
            

    # move function, changes the position of the blob depending on the direction it's going and it's speed
    def move(self,blob):
        blob.x += blob.velocity * sin( blob.angle )
        blob.y += blob.velocity * cos ( blob.angle )

# the class from which the blob objects are created, comes with alot of blob exsclusive function
class Blob():

    def __init__(self): # when created


        # varibles - standard
        self.x = uniform(0,float(Misc.window_width))
        self.y = uniform(0,float(Misc.window_length))
        self.mass = float(500)
        self.energi_drain_konstant = float(0.00125)
        self.radius = int( ( self.mass / pi ) ** 0.5 )
        self.velocity = float(1)
        self.angle = float(pi / 2)
        self.ai_stance_update_rate = int(50)
        self.ai_stance_update_frame = randint(0, self.ai_stance_update_rate - 1)
        self.ai_stance = "__hungry__"
        
        self.target_plant = 0
        self.target_mate = 0

        self.age = 0 # in frames
        self.effciency = float ( 1 / ( 1 + self.age * 0.001  ) )


        # genes
        self.minimal_mass = float(100) # minimal mass before death
        self.hungry_bias = float(500) # not yet used
        self.sight = float(600)
        self.agility = float(1) # not yet used
        self.reproduce_child_size = float(0.2) # perentage of mass given to child during birth
        #self.reproduce_maximal_mass = float(1500)
        self.mass_to_reproduce = float(1000)
        self.speed_modifier = float(1)
        self.color = [100,100,100]


    def update(self, frame): # each frame

        mass_before_update = self.mass
        self.age += 1
        self.effciency = float ( 1 / ( 1 + self.age * 0.001  ) )

        self.mass -=  self.energi_drain_konstant * ( (self.mass * self.velocity ** 2)) * ( 1 / self.effciency  )  # lowers mass depending on energy used to move
        self.mass -= 0.01 * self.energi_drain_konstant * self.sight * ( 1 / self.effciency  ) # lowers mass depending on sight
        if self.mass < 0:
            self.mass = float(0)
        self.radius = int( ( self.mass / pi ) ** 0.5 )
        self.velocity = self.speed_modifier * ( 1000 / ( self.mass + 500 ) )

        # the mass lost will return to the worlds mass pool
        ENV.world_mass += mass_before_update - self.mass
        
        # coalitions
        food = Collision.check_overlap(self, plant_pop)
        if food != -1:

            self.eat(plant_pop[food])

        # refresh stance (ai)
        if frame % self.ai_stance_update_rate == self.ai_stance_update_frame:

            self.refresh_stance()

        # movement (ai)
        if self.ai_stance == "__hungry__":

            Ai().hungry(self)

        # repruduce (ai)
        elif self.ai_stance == "__mate_search__":

            Ai().mate_search(self)
        
            
    def reproduce(self, partner):
        
        # creates the child
        child = Blob()
        child.mass = self.mass * self.reproduce_child_size + partner.mass * partner.reproduce_child_size


        child.x = ( self.x + partner.x ) * 0.5
        child.y = ( self.y + partner.y ) * 0.5

        # modifies the genes

        # color gene
        child.color[0] = int ( ( self.color[0] + partner.color[0] ) / 2 + randint(-25,25) )
        child.color[1] = int ( ( self.color[1] + partner.color[1] ) / 2 + randint(-25,25) )
        child.color[2] = int ( ( self.color[2] + partner.color[2] ) / 2 + randint(-25,25) )
        timer = 0
        for pigment in child.color:

            if pigment > 255:
                child.color[timer] = 255
            elif pigment < 0:
                child.color[timer] = 0
            
            timer += 1

        # reproduction desire gene   
        child.mass_to_reproduce = ( self.mass_to_reproduce + partner.mass_to_reproduce ) / 2 + uniform(-150,150)
        
        # repruction child size gene
        child.reproduce_child_size = (self.reproduce_child_size + partner.reproduce_child_size ) / 2 + uniform(-0.5,0.5)
        if child.reproduce_child_size < 0:
            child.reproduce_child_size = 0

        # sight gene
        child.sight = (self.sight + partner.sight) / 2 + uniform(-100, 100)
        if child.sight < 1:
            child.sight = 1

        # speed gene
        child.speed_modifier = (self.speed_modifier + partner.speed_modifier) / 2 + uniform(-0.15, 0.15)
        if child.speed_modifier < 0:
            speed_modifier = 0

        # adds the child to the population
        population.append( child )

        # removes mass from parents equal
        self.mass -= self.mass * self.reproduce_child_size
        partner.mass -= partner.mass * partner.reproduce_child_size

        # change ai stance for both partners
        self.refresh_stance()
        partner.refresh_stance()

        self.target_mate = 0
        partner.target_mate = 0

        for blob in population:
            if blob.target_mate == partner or blob.target_mate == self:
                blob.target_mate = 0


    def refresh_stance(self): #changes behaviour depending on mass
        ratio = self.mass / self.mass_to_reproduce
        num = 2 / (1+exp(-ratio))-1
        if num > uniform(0,1):
            self.ai_stance = "__mate_search__"

        else:
            self.ai_stance = "__hungry__"
    
        self.target_plant = 0
        self.target_mate = 0

    # consume a plant
    def eat(self, plant):

        self.mass += plant.mass
        ENV.chunks[plant.chunk_x][plant.chunk_y].plants -= 1
        self.refresh_stance()
        
        # why is this code here???
        for blob in population:

            if blob.target_plant == plant:

                blob.target_plant = 0
        # ------------------------
        
        plant_pop.remove(plant)


    # draws a circle into the window
    def draw(self, window):

        try:

            pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius)
        except:

            print("error with colors:", self.color)
            pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius)
        
# the class from which the blob objects are created, comes with alot of plants exsclusive function
class Plant():


    def __init__(self):


        self.x = uniform(0,float(Misc.window_width))
        self.y = uniform(0,float(Misc.window_length))
        self.mass = float(20)
        self.max_mass = float(1000)
        self.radius = int( ( self.mass / pi ) ** 0.5 )
        self.photosynthesis = float(10)
        self.age = 0
        self.children = 0

        self.chunk_x = 0
        self.chunk_y = 0

        self.minimal_mass = 10

        #genes
        self.seed_spread = uniform(0,150) # for reproduction
        self.mass_to_reproduce = float(750)
        self.reproduce_child_size = float(0.2)


    def update(self):
        new_mass = self.photosynthesis * (1 - self.mass/self.max_mass) * ENV.chunks[self.chunk_x][self.chunk_y].biomass/1000
        #calculates mass based on current mass, max mass, biomass in chunk and photosynthesis

        self.mass += new_mass #adds mass to plant
        self.age += 1

        ENV.chunks[self.chunk_x][self.chunk_y].biomass -= new_mass #removes mass from chunk

        self.radius = int( ( self.mass / pi ) **  0.5 )

        if self.mass > self.mass_to_reproduce:
            self.reproduce()


    def draw(self, window): # draws a circle into the window

        pygame.draw.circle(window, Colors.green, (int(self.x), int(self.y)), self.radius)


    def reproduce(self):

        angle = uniform(0,2*pi)
        sapling = Plant()
        sapling.mass = self.mass * self.reproduce_child_size

        sapling.x = self.x + self.seed_spread * sin(angle)
        sapling.y = self.y + self.seed_spread * cos(angle)

        # makes sure the plant does not spawn outside the window
        if sapling.x < 0:

            sapling.x  = 0
        elif sapling.x > Misc.window_width:
            
            sapling.x  = Misc.window_width

        if sapling.y < 0:

            sapling.y = 0
        elif sapling.y > Misc.window_length:

            sapling.y = Misc.window_length
        
        sapling.find_chunk(ENV)
        ENV.chunks[sapling.chunk_x][sapling.chunk_y].plants += 1


        #Copies genes to sapling (+ mutation)
        sapling.seed_spread = self.seed_spread * uniform(0.99,1.01)
        sapling.mass_to_reproduce = self.mass_to_reproduce * uniform(0.99,1.01)
        sapling.reproduce_child_size = self.reproduce_child_size * uniform(0.99,1.01)
        sapling.max_mass = self.max_mass * uniform( 0.99,1.01)


        self.mass -= sapling.mass + self.seed_spread/2
        plant_pop.append(sapling)


        self.children += 1


    def find_chunk(self, Environment):
        for x in range(0,13):
            for y in range(0,8):
                if self.x < Environment.chunks[x][y].x +100 and self.y < Environment.chunks[x][y].y+100:
                    self.chunk_x = x
                    self.chunk_y = y
                    return

# the class from which the chunk objects are created, comes with alot of chunk exsclusive function
class Chunk():


    def __init__(self):

        self.width = int(100)
        self.biomass = int(0)
        self.max_biomass = int(10000)
        self.growth = float(0.25)
        self.x = 0
        self.y = 0
        self.color = [51,0,0]
        self.plants = 0  # to be revisited


    def update(self):

        # ENV is the envorment object, which should not have been made an object in the first place but were stuck with it

        self.biomass += int ( self.growth * (1 - self.biomass/self.max_biomass) * ENV.world_mass / ENV.chunks_amount )
        ENV.mass_given_this_frame += int ( self.growth * (1 - self.biomass/self.max_biomass) * ENV.world_mass / ENV.chunks_amount )

        # Update color to see biomass
        self.color[1] = int( 230 * self.biomass / self.max_biomass + 25)
        self.color[0] = int( 51 - 26 * (self.biomass / self.max_biomass) - 25 )
        
    def draw(self,window):

        pygame.draw.rect(window,self.color,(self.x,self.y,self.width, self.width))

# the class which manages the environment the blobs and plants inhibits
class Environment():

    def __init__(self):


        self.chunks = []
        for x in range(0,13): # window_length / chunk.width
            temp = []
            for y in range(0,8): # window_width / chunk.width
                TC = Chunk()
                TC.x = x*( TC.width )
                TC.y = y*( TC.width )
                temp.append(TC)
            self.chunks.append(temp)

        self.chunks_amount = len(self.chunks) # the amount of chunks in the world
        self.world_mass = 100000 # the biomass which exist at the start of the game
        self.mass_given_this_frame = 0 # a counter to keep track of how much mass is given to the chunks

    def update(self):
        pass

    def decrease_world_mass(self):

        # removes mass given to chunks this frame
        self.world_mass -= self.mass_given_this_frame
        self.mass_given_this_frame = 0

    
    # planned :
    # day and night cycle
    # summer and winter cycle
                        
# deals with gathering data during the simulation and defines functions to display the same data
class Statistics():


    index_length = 0
    frame_array = []

    # blob stats:

    blob_total_mass = []
    blob_average_mass = []
    blob_average_speed = []
    blob_average_sight = []
    blob_average_mass_to_reproduce = []
    blob_average_child_size = []
    blob_population_size = []
    blob_average_age = []
    blob_death_counter = []

    # plant stats:
    
    plant_total_mass = []
    plant_pop_size = []
    plant_average_age = []

    def get_info(self, frame):

        # calculate the stats for the frame

        blob_population_size = len( population )
        total_mass = 0
        speed = 0
        sight = 0
        mass_to_reproduce = 0
        child_size = 0
        blob_combined_age = 0

        for blob in population:

            total_mass += blob.mass
            speed += blob.speed_modifier
            sight += blob.sight
            mass_to_reproduce += blob.mass_to_reproduce
            child_size += blob.reproduce_child_size
            blob_combined_age += blob.age
        
        plant_pop_size = len( plant_pop )
        total_mass_plants = 0
        plant_combined_age = 0

        for plant in plant_pop:

            total_mass_plants += plant.mass
            plant_combined_age += plant.age

            

        # blob stats:

        self.blob_total_mass.append( total_mass )
        self.blob_average_mass.append( total_mass / blob_population_size )
        self.blob_average_speed.append( speed / blob_population_size )
        self.blob_average_sight.append( sight / blob_population_size )
        self.blob_average_mass_to_reproduce.append( mass_to_reproduce / blob_population_size )
        self.blob_average_child_size.append( child_size / blob_population_size )
        self.blob_population_size.append( blob_population_size )
        self.blob_death_counter.append( Misc.death_counter )
        self.blob_average_age.append( blob_combined_age / blob_population_size )

        # plant stats:

        self.plant_total_mass.append( total_mass_plants )
        self.plant_pop_size.append( plant_pop_size )
        self.plant_average_age.append( plant_combined_age / blob_population_size )

        # other 
        self.frame_array.append( frame )

        self.index_length += 1

    def visualize_total_mass(self):

        # important :
        # ratio_y most be given two values representing the minimal and max value, the minimal value will be origo and the max will be the top of the y axis
        
        pygame.init() # creates all the important event which we don't need to program ourself
        pygame.font.init() # enbles the use of text in pygame
        self.window = pygame.display.set_mode(( Misc().window_width , Misc().window_length )) # creates the window
        pygame.display.set_caption('Evo Stats') # the window title

        # draw on the surface (only needs to be done once)
        spacing = 50
        pygame.draw.line(self.window, Colors.teal, ( spacing, Misc.window_length - spacing ) , ( Misc.window_width - spacing , Misc.window_length - spacing ) , 5 )
        pygame.draw.line(self.window, Colors.teal, ( spacing, Misc.window_length - spacing ) , ( spacing , spacing ) , 5 )
        pygame.display.update()
        
        # writes the graph

        # y axis will be for all the data points
        # x axis will be the frames

        # gets the biggest value
        biggest_blob_total_mass = Misc.get_biggest_num(self.blob_total_mass)
        biggest_plant_total_mass = Misc.get_biggest_num(self.plant_total_mass)
        biggest_y_value = Misc.get_biggest_num( [ biggest_blob_total_mass, biggest_plant_total_mass ] )

        data_points = len( self.frame_array )
        print(data_points, len(self.blob_total_mass))
        x_axis_length = ( Misc.window_width - spacing ) - spacing
        y_axis_length = ( Misc.window_length - spacing ) - spacing
        x_spacing = x_axis_length / data_points
        y_spacing = y_axis_length / data_points
        timer = 0
        while timer < data_points:

            # the y_cord calculation are made by calculating how much percantage of the biggest value a value holds then multiply that with the length of the axis

            x_cord = timer * x_spacing + spacing # x is the same for all data points
            print("x : ", x_cord)
            
            # draws a dot for the blob data
            y_cord = y_axis_length - ( ( self.blob_total_mass[timer] * ( 1 / biggest_y_value ) ) * y_axis_length ) + spacing
            pygame.draw.circle(self.window, Colors.red, (int(x_cord), int(y_cord)), Misc.statistics_circle_size)
            print("y : ", y_cord)
            
            # draws a dot for the blob plant
            y_cord = y_axis_length - ( ( self.plant_total_mass[timer] * ( 1 / biggest_y_value ) ) * y_axis_length ) + spacing
            pygame.draw.circle(self.window, Colors.lime, (int(x_cord), int(y_cord)), Misc.statistics_circle_size)

            timer += 1
        

        # draws text
        font = pygame.font.SysFont('Comic Sans MS',15) # define the style of the text

        textsurface_0 = font.render('Y = mass , X = time', False, (200, 200, 0)) # creates the text object
        textsurface_1 = font.render(str( int ( biggest_y_value ) ), False, (200, 200, 0)) # creates the text object
        textsurface_2 = font.render("0", False, (200, 200, 0)) # creates the text object

        
        self.window.blit( textsurface_0,(0,0) )
        self.window.blit( textsurface_1,( int ( spacing / 2 ), int ( Misc.window_length - y_axis_length - spacing * 1.5 ) ) )
        self.window.blit( textsurface_2,( int ( spacing / 2 ), Misc.window_length - spacing) )

        pygame.display.update()


        self.timer = 0 # for counting frames
        self.running = True

        while self.running == True: # infinite loop

            for event in pygame.event.get(): # this allows the program to end the loop if the x buttom is pressed

                if event.type == QUIT:

                    self.running = False

        
            sleep(0.05)
  
    def visualize_pop_size(self):

        # important :
        # ratio_y most be given two values representing the minimal and max value, the minimal value will be origo and the max will be the top of the y axis
        
        pygame.init() # creates all the important event which we don't need to program ourself
        pygame.font.init() # enbles the use of text in pygame
        self.window = pygame.display.set_mode(( Misc().window_width , Misc().window_length )) # creates the window
        pygame.display.set_caption('Evo Stats') # the window title

        # draw on the surface (only needs to be done once)
        spacing = 50
        pygame.draw.line(self.window, Colors.teal, ( spacing, Misc.window_length - spacing ) , ( Misc.window_width - spacing , Misc.window_length - spacing ) , 5 )
        pygame.draw.line(self.window, Colors.teal, ( spacing, Misc.window_length - spacing ) , ( spacing , spacing ) , 5 )
        pygame.display.update()
        
        # writes the graph

        # y axis will be for all the data points
        # x axis will be the frames

        # gets the biggest value
        biggest_blob_total_mass = Misc.get_biggest_num(self.blob_population_size)
        biggest_plant_total_mass = Misc.get_biggest_num(self.plant_pop_size)
        biggest_y_value = Misc.get_biggest_num( [ biggest_blob_total_mass, biggest_plant_total_mass ] )

        data_points = len( self.frame_array )
        print(data_points, len(self.blob_population_size))
        x_axis_length = ( Misc.window_width - spacing ) - spacing
        y_axis_length = ( Misc.window_length - spacing ) - spacing
        x_spacing = x_axis_length / data_points
        y_spacing = y_axis_length / data_points
        timer = 0
        while timer < data_points:

            # the y_cord calculation are made by calculating how much percantage of the biggest value a value holds then multiply that with the length of the axis

            x_cord = timer * x_spacing + spacing # x is the same for all data points
            print("x : ", x_cord)
            
            # draws a dot for the blob data
            y_cord = y_axis_length - ( ( self.blob_population_size[timer] * ( 1 / biggest_y_value ) ) * y_axis_length ) + spacing
            pygame.draw.circle(self.window, Colors.red, (int(x_cord), int(y_cord)), Misc.statistics_circle_size)
            print("y : ", y_cord)
            
            # draws a dot for the blob plant
            y_cord = y_axis_length - ( ( self.plant_pop_size[timer] * ( 1 / biggest_y_value ) ) * y_axis_length ) + spacing
            pygame.draw.circle(self.window, Colors.lime, (int(x_cord), int(y_cord)), Misc.statistics_circle_size)

            timer += 1
        

        # draws text
        font = pygame.font.SysFont('Comic Sans MS',15) # define the style of the text

        textsurface_0 = font.render('Y = pop size , X = time', False, (200, 200, 0)) # creates the text object
        textsurface_1 = font.render(str( int ( biggest_y_value ) ), False, (200, 200, 0)) # creates the text object
        textsurface_2 = font.render("0", False, (200, 200, 0)) # creates the text object

        
        self.window.blit( textsurface_0,(0,0) )
        self.window.blit( textsurface_1,( int ( spacing / 2 ), int ( Misc.window_length - y_axis_length - spacing * 1.5 ) ) )
        self.window.blit( textsurface_2,( int ( spacing / 2 ), Misc.window_length - spacing) )

        pygame.display.update()


        self.timer = 0 # for counting frames
        self.running = True

        while self.running == True: # infinite loop

            for event in pygame.event.get(): # this allows the program to end the loop if the x buttom is pressed

                if event.type == QUIT:

                    self.running = False

        
            sleep(0.05)

    def visualize_gene(self, gene_data, y_string):


        # important :
        # ratio_y most be given two values representing the minimal and max value, the minimal value will be origo and the max will be the top of the y axis
        
        pygame.init() # creates all the important event which we don't need to program ourself
        pygame.font.init() # enbles the use of text in pygame
        self.window = pygame.display.set_mode(( Misc().window_width , Misc().window_length )) # creates the window
        pygame.display.set_caption('Evo Stats') # the window title

        # draw on the surface (only needs to be done once)
        spacing = 50
        pygame.draw.line(self.window, Colors.teal, ( spacing, Misc.window_length - spacing ) , ( Misc.window_width - spacing , Misc.window_length - spacing ) , 5 )
        pygame.draw.line(self.window, Colors.teal, ( spacing, Misc.window_length - spacing ) , ( spacing , spacing ) , 5 )
        pygame.display.update()
        
        # writes the graph

        # y axis will be for all the data points
        # x axis will be the frames

        # gets the biggest value
        biggest_y_value = Misc.get_biggest_num(gene_data)

        data_points = len( self.frame_array )
        print(data_points, len(gene_data))
        x_axis_length = ( Misc.window_width - spacing ) - spacing
        y_axis_length = ( Misc.window_length - spacing ) - spacing
        x_spacing = x_axis_length / data_points
        y_spacing = y_axis_length / data_points
        timer = 0
        while timer < data_points:

            # the y_cord calculation are made by calculating how much percantage of the biggest value a value holds then multiply that with the length of the axis

            x_cord = timer * x_spacing + spacing # x is the same for all data points
            print("x : ", x_cord)
            
            # draws a dot for the gene_data
            y_cord = y_axis_length - ( ( gene_data[timer] * ( 1 / biggest_y_value ) ) * y_axis_length ) + spacing
            pygame.draw.circle(self.window, Colors.red, (int(x_cord), int(y_cord)), Misc.statistics_circle_size)
            print("y : ", y_cord)

            timer += 1
        

        # draws text
        font = pygame.font.SysFont('Comic Sans MS',15) # define the style of the text

        textsurface_0 = font.render('Y = %s , X = time' % (y_string), False, (200, 200, 0)) # creates the text object
        if y_string == "average_child_size":
            textsurface_1 = font.render(str( int ( biggest_y_value * 100 ) ) + "%", False, (200, 200, 0)) # creates the text object
        elif y_string == "blob_average_speed":
            textsurface_1 = font.render(str( int ( biggest_y_value * 100 ) ) + "%", False, (200, 200, 0)) # creates the text object
        else:
            textsurface_1 = font.render(str( int ( biggest_y_value) ), False, (200, 200, 0)) # creates the text object
        textsurface_2 = font.render("0", False, (200, 200, 0)) # creates the text object

        
        self.window.blit( textsurface_0,(0,0) )
        self.window.blit( textsurface_1,( int ( spacing / 2 ), int ( Misc.window_length - y_axis_length - spacing * 1.5 ) ) )
        self.window.blit( textsurface_2,( int ( spacing / 2 ), Misc.window_length - spacing) )

        pygame.display.update()


        self.timer = 0 # for counting frames
        self.running = True

        while self.running == True: # infinite loop

            for event in pygame.event.get(): # this allows the program to end the loop if the x buttom is pressed

                if event.type == QUIT:

                    self.running = False

        
            sleep(0.05)

    def visualize_ratio(self, blob_population_size, plant_pop_size, y_string):

        # important :
        # ratio_y most be given two values representing the minimal and max value, the minimal value will be origo and the max will be the top of the y axis
        
        pygame.init() # creates all the important event which we don't need to program ourself
        pygame.font.init() # enbles the use of text in pygame
        self.window = pygame.display.set_mode(( Misc().window_width , Misc().window_length )) # creates the window
        pygame.display.set_caption('Evo Stats') # the window title

        # draw on the surface (only needs to be done once)
        spacing = 50
        pygame.draw.line(self.window, Colors.teal, ( spacing, Misc.window_length - spacing ) , ( Misc.window_width - spacing , Misc.window_length - spacing ) , 5 )
        pygame.draw.line(self.window, Colors.teal, ( spacing, Misc.window_length - spacing ) , ( spacing , spacing ) , 5 )
        pygame.display.update()
        
        # writes the graph

        # y axis will be for all the data points
        # x axis will be the frames

        # stats data:
        ratio_data = []
        len_of_data = len(blob_population_size)
        timer_0 = 0
        while timer_0 < len_of_data:

            data_point = float ( ( blob_population_size[timer_0] / plant_pop_size[timer_0] ) )  # this will be in %

            ratio_data.append(data_point)

            timer_0 += 1

        # gets the biggest value
        biggest_y_value = Misc.get_biggest_num(ratio_data)

        data_points = len( self.frame_array )
        print(data_points, len(ratio_data))
        x_axis_length = ( Misc.window_width - spacing ) - spacing
        y_axis_length = ( Misc.window_length - spacing ) - spacing
        x_spacing = x_axis_length / data_points
        y_spacing = y_axis_length / data_points
        timer = 0
        while timer < data_points:

            # the y_cord calculation are made by calculating how much percantage of the biggest value a value holds then multiply that with the length of the axis

            x_cord = timer * x_spacing + spacing # x is the same for all data points
            print("x : ", x_cord)
            
            # draws a dot for the gene_data
            y_cord = y_axis_length - ( ( ratio_data[timer] * ( 1 / biggest_y_value ) ) * y_axis_length ) + spacing
            pygame.draw.circle(self.window, Colors.red, (int(x_cord), int(y_cord)), Misc.statistics_circle_size)
            print("y : ", y_cord)

            timer += 1
        

        # draws text
        font = pygame.font.SysFont('Comic Sans MS',15) # define the style of the text

        textsurface_0 = font.render('Y = %s , X = time' % (y_string), False, (200, 200, 0)) # creates the text object
        if y_string == "average_child_size":
            textsurface_1 = font.render(str( int ( biggest_y_value * 100 ) ) + "%", False, (200, 200, 0)) # creates the text object
        elif y_string == "blob_average_speed":
            textsurface_1 = font.render(str( int ( biggest_y_value * 100 ) ) + "%", False, (200, 200, 0)) # creates the text object
        elif y_string == "blob_to_plant_ratio":
            textsurface_1 = font.render(str( int ( biggest_y_value * 100 ) ) + "%", False, (200, 200, 0)) # creates the text object
        else:
            textsurface_1 = font.render(str( int ( biggest_y_value) ), False, (200, 200, 0)) # creates the text object
        textsurface_2 = font.render("0", False, (200, 200, 0)) # creates the text object

        
        self.window.blit( textsurface_0,(0,0) )
        self.window.blit( textsurface_1,( int ( spacing / 2 ), int ( Misc.window_length - y_axis_length - spacing * 1.5 ) ) )
        self.window.blit( textsurface_2,( int ( spacing / 2 ), Misc.window_length - spacing) )

        pygame.display.update()


        self.timer = 0 # for counting frames
        self.running = True

        while self.running == True: # infinite loop

            for event in pygame.event.get(): # this allows the program to end the loop if the x buttom is pressed

                if event.type == QUIT:

                    self.running = False

        
            sleep(0.05)

# effectivly our main function
class Visual():

    def __init__(self):


        pygame.init() # creates all the important event which we don't need to program ourself
        self.window = pygame.display.set_mode(( Misc().window_width , Misc().window_length )) # creates the window
        pygame.display.set_caption('Evo Simulator') # the window title


        Misc.last_time = time() # recieves the time since the epoch the program started
        self.timer = 0 # for counting frames
        self.running = True

        # our main loop
        while self.running == True:

            for event in pygame.event.get(): # this allows the program to end the loop if the x buttom is pressed

                if event.type == QUIT:

                    self.running = False

            self.window.fill(Colors.black) # clears the screen


            # uppdates and draws objects
            if self.timer % 10 == 0:
                PL = Plant()
                PL.find_chunk(ENV)
                plant_pop.append(PL)

            for x in range(0,13):
                for y in range(0,8):
                    ENV.chunks[x][y].update()
                    ENV.chunks[x][y].draw(self.window)

            ENV.decrease_world_mass()

            for plant in plant_pop:

                plant.update()
                if plant.mass < plant.minimal_mass:

                    ENV.world_mass += plant.mass
                    ENV.chunks[plant.chunk_x][plant.chunk_y].plants -= 1
                    plant_pop.remove(plant)

                plant.draw(self.window)

            for blob in population:

                blob.update(self.timer)
                if blob.mass < blob.minimal_mass:

                    ENV.world_mass += blob.mass
                    population.remove(blob)
                    Misc.death_counter += 1

                blob.draw(self.window)
                  
    
            pygame.display.update() # display the new frame
            
            Misc().report(self.timer)
            if self.timer % 10 == 0:

                Statistics().get_info(self.timer)

            # the following code makes sure theres will always be 60 fps
            dt = time() - Misc.last_time
            desired_frames = dt * Misc.framerate

            # if theres more frames displayed then wanted
            if desired_frames < self.timer:
                
                frames_ahead = self.timer - desired_frames
                sleep( 0.0166 * frames_ahead )
            # if theres less displayed frames then wanted 
            elif desired_frames - Misc.skiped_frames > self.timer + 1:

                Misc.skiped_frames += ( desired_frames - Misc.skiped_frames ) - ( self.timer + 1 )

            
            # counts the frames
            self.timer += 1


        print("---end---")


# --- hardcoded --- #


ENV = Environment()
plant_pop = []
population = []
for i in range(0,50):
    PL = Plant()
    PL.find_chunk(ENV)
    plant_pop.append(PL)

# our starting population
for i in range(0,5):
    population.append(Blob())


# --- --------- --- #
# this code runs the simulation


try:

    Visual() # start the game mode

except:
    print("the evolution was terminated either due to an unexpected error or the blob population died out")

pygame.quit() # exit properly (pygame)

# --- -------- --- #
# this code displays the statistics

run = True
while run == True:
  
    print("options : ")
    print("mass_graph : shows mass for blobs, plants and chunks")
    print("pop_graph : shows the populations over time")
    print("birth_gene_1_graph : shows the gene that determens how much mass you wan't to create a child")
    print("birth_gene_2_graph : shows the gene which determen how much mass is tranfered to child during reproduction")
    print("speed_gene_graph : shows the gene which multiplies the blobs speed")
    print("sight_gene_graph : shows the gene which decides how far the blob can se")
    print("blob_to_plant_ratio : shows the ratio of blobs per plant")
    print("death_graph : shows a graph of the total death count")
    print("blob_age_graph : shows a graph of the average age of blobs")
    print("plant_age_graph : shows a graph of the average age of plant")

    show_stat = input("enter command : ")
    show_stat = str(show_stat)

    if show_stat == "mass_graph":

        Statistics().visualize_total_mass()
        pygame.quit()

    elif show_stat == "pop_graph":

        Statistics().visualize_pop_size()
        pygame.quit()

    elif show_stat == "birth_gene_1_graph":

        Statistics().visualize_gene( Statistics.blob_average_mass_to_reproduce, "mass_to_reproduce"  )
        pygame.quit()

    elif show_stat == "birth_gene_2_graph":

        Statistics().visualize_gene( Statistics.blob_average_child_size, "average_child_size" )
        pygame.quit()


    elif show_stat == "speed_gene_graph":

        Statistics().visualize_gene( Statistics.blob_average_speed, "blob_average_speed" )
        pygame.quit()

    elif show_stat == "sight_gene_graph":

        Statistics().visualize_gene( Statistics.blob_average_sight, "blob_average_sight" )
        pygame.quit() 

    elif show_stat == "blob_to_plant_ratio":

        Statistics().visualize_ratio(Statistics.blob_population_size, Statistics.plant_pop_size, "blob_to_plant_ratio")
        pygame.quit()

    elif show_stat == "death_graph":

        Statistics().visualize_gene( Statistics.blob_death_counter, "blob_death_counter" )
        pygame.quit() 

    elif show_stat == "blob_age_graph":

        Statistics().visualize_gene( Statistics.blob_average_age, "blob_age_graph" )
        pygame.quit() 

    elif show_stat == "plant_age_graph":

        Statistics().visualize_gene( Statistics.plant_average_age, "plant_age_graph" )
        pygame.quit() 

    elif show_stat == "end":

        break

    else:

        print("unknown command - plz retry")

print("end of thread")
