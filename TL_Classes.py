import pygame, os, sys

img_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
def get_file(file):
    return os.path.abspath(os.path.join(img_dir, "img", file))

cell_size = (100, 100)
minimum_signal_strength = {'PAM': 10, 'PWM': 5}
# combinations = [('None'), ('left'), ('up'), ('right'), ('down'),
#                ('left', 'up'), ('left', 'right'), ('left', 'down'), ('up', 'right'), ('up', 'down'), ('right', 'down')]
opposite = {'left': 'right', 'right': 'left', 'up': 'down', 'down': 'up'}


class block():
    def __init__(self, id, name, image_file_names):
        self.name = name
        self.id = id
        self.connected_block = [None, None]
        self.image_sprites = []
        for image in image_file_names:
            self.image_sprites.append(pygame.transform.scale(
                pygame.image.load(get_file(image)).convert_alpha(),
                cell_size))
        self.image = self.image_sprites[0]

    def connect_block(self, next_block, direction):
        if None in self.connected_block and None in next_block.connected_block:
            index = self.connected_block.index(None)
            self.connected_block[index] = direction
            self.refresh_image()

            index = next_block.connected_block.index(None)
            next_block.connected_block[index] = opposite[direction]
            next_block.refresh_image()


class factory(block):
    def __init__(self):
        super().__init__(0, 'factory', ('factory.png',))
        self.connected_block = [None]

    def output(self, data, direction):
        return data, self.connected_block[0]

    def refresh_image(self):
        pass


class home(block):
    def __init__(self):
        super().__init__(1, 'home', ('home.png',))
        self.connected_block = [None]

    def output(self, data, direction):
        signal_strength, frequency, modulation_technique = data
        if signal_strength > minimum_signal_strength[modulation_technique]:
            output = "Signal has been received"
        else:
            output = 'Not enough strength in signal'

        return None, [output,data]

    def refresh_image(self):
        pass


class wire(block):
    def __init__(self):
        super().__init__(2, 'wire', ('wire.png', 'wire2.png'))

    def output(self, data, direction):
        signal_strength, frequency, modulation_technique = data
        if signal_strength > 0:
            signal_strength -= 1
        else:
            signal_strength = 0

        temp = self.connected_block.copy()
        temp.pop(temp.index(opposite[direction]))
        return (signal_strength, frequency, modulation_technique), temp[0]

    def refresh_image(self):
        if None in self.connected_block:
            image = self.image_sprites[0]
            if 'up' in self.connected_block or 'down' in self.connected_block:
                angle = 90
            else:
                angle = 0
        elif 'up' in self.connected_block and 'down' in self.connected_block:
            image = self.image_sprites[0]
            angle = 90
        elif 'right' in self.connected_block and 'left' in self.connected_block:
            image = self.image_sprites[0]
            angle = 0
        else:
            image = self.image_sprites[1]
            if 'up' in self.connected_block:
                if 'left' in self.connected_block:
                    angle = 0
                elif 'right' in self.connected_block:
                    angle = 90
                else:
                    raise Exception('Unknown error')
            elif 'down' in self.connected_block:
                if 'right' in self.connected_block:
                    angle = 180
                elif 'left' in self.connected_block:
                    angle = 270
                else:
                    raise Exception('Unknown error')

        self.image = pygame.transform.rotate(image, -angle)


class repeater(block):
    def __init__(self):
        super().__init__(3, 'repeater', ('repeater.png',))

    def output(self, data, direction):
        signal_strength, frequency, modulation_technique = data
        if signal_strength > minimum_signal_strength[modulation_technique]:
            signal_strength = 15
        else:
            signal_strength = 0

        temp = self.connected_block.copy()
        temp.pop(temp.index(opposite[direction]))
        return (signal_strength, frequency, modulation_technique), temp[0]

    def refresh_image(self):
        pass


class_list = (factory, home, wire, repeater)


class level():
    def __init__(self, level_data):
        self.rows = len(level_data['stage'])
        self.columns = len(level_data['stage'][0])
        self.stage = level_data['stage']
        self.modulation_technique = level_data['modulation_technique']
        self.frequency = level_data['frequency']
        self.signal_strength = level_data['signal_strength']
        self.start = None
        self.menu_bar = level_data['menu_bar']
        self.cost_limit = level_data['cost_limit']
        self.screen = level_data['screen']
        self.current_frame = 'start'
        self.output = ''

        self.run_image = pygame.transform.scale(
            pygame.image.load(get_file('run.jpg')).convert_alpha(),
            cell_size)
        
        self.frame = pygame.transform.scale(
            pygame.image.load(get_file('frame.png')).convert_alpha(),
            (800,400))

        for row in range(self.rows):
            for column in range(self.columns):
                data = self.stage[row][column]

                if data == -1:
                    continue
                elif data in [1, 2, 3]:
                    self.stage[row][column] = class_list[data]()
                elif data == 0:
                    self.start = (row, column)
                    self.stage[row][column] = class_list[0]()
                else:
                    print('error in stage unknown block specified')

    def update_tile(self, row, column, data):
        if row >= self.rows or column >= self.columns:
            run = False
        elif self.stage[row][column] == -1:
            run = True
        elif self.stage[row][column].name in ['home', 'factory']:
            run = False
        else:
            run = True
            level.delete_tile(self, row, column)
        if run:
            new_block = class_list[data]()
            self.stage[row][column] = new_block

            if row-1 >= 0:
                if type(self.stage[row - 1][column]) != int:
                    new_block.connect_block(
                        self.stage[row - 1][column], 'up')
            if column-1 >= 0:
                if type(self.stage[row][column - 1]) != int:
                    new_block.connect_block(
                        self.stage[row][column - 1], 'left')
            if row+1 < self.rows:
                if type(self.stage[row + 1][column]) != int:
                    new_block.connect_block(
                        self.stage[row + 1][column], 'down')
            if column+1 < self.columns:
                if type(self.stage[row][column + 1]) != int:
                    new_block.connect_block(
                        self.stage[row][column + 1], 'right')

    def delete_tile(self, row, column):
        tile = self.stage[row][column]
        if 'up' in tile.connected_block:
            index = self.stage[row - 1][column].connected_block.index('down')
            self.stage[row - 1][column].connected_block[index] = None
        if 'down' in tile.connected_block:
            index = self.stage[row + 1][column].connected_block.index('up')
            self.stage[row + 1][column].connected_block[index] = None
        if 'left' in tile.connected_block:
            index = self.stage[row][column - 1].connected_block.index('right')
            self.stage[row][column - 1].connected_block[index] = None
        if 'right' in tile.connected_block:
            index = self.stage[row][column + 1].connected_block.index('left')
            self.stage[row][column + 1].connected_block[index] = None
        self.stage[row][column] = -1

    def run_circuit(self):
        if self.start == None:
            raise Exception('error factory not initilized')
        else:
            row, column = self.start

        signal_data = (self.signal_strength, self.frequency,
                       self.modulation_technique)

        direction = None
        while signal_data:
            signal_data, direction = self.stage[row][column].output(
                signal_data, direction)

            if direction == 'up':
                row -= 1
            elif direction == 'down':
                row += 1
            elif direction == 'left':
                column - + 1
            elif direction == 'right':
                column += 1
            elif direction == None:
                self.output = ['Signal not detected',(0,None,None)]
                break
            else:
                self.output = direction
        self.current_frame = 'output'

    def display_output(self):
        self.screen.fill('#00ff00')
        self.screen.blit(self.frame,(100,100))
        font = pygame.font.Font('freesansbold.ttf', 64)

        text = font.render('Circuit Analysis', True, '#000000')
        rect = text.get_rect()
        rect.center = (500, 50)
        self.screen.blit(text, rect)

        font = pygame.font.Font('freesansbold.ttf', 32)
        cost = self.update_cost()
        if cost > self.cost_limit:
            color = '#ff0000'
            val_cost = True
        else:
            color = '#000000'
            val_cost = False
        text = font.render('Cost: '+ str(cost) + '/' + str(self.cost_limit) + ' Rs', True, color)
        self.screen.blit(text, (150, 150))

        snr = self.output[1][0]
        min_snr = minimum_signal_strength[self.modulation_technique]
        if snr <= min_snr:
            color = '#ff0000'
        else:
            color = '#000000'
        text = font.render('Minimum SNR: '+ str(snr) + '/' + str(min_snr) + ' dB', True, color)
        self.screen.blit(text, (150, 200))

        text = font.render('Modulation Technique: ' + self.modulation_technique, True, '#000000')
        self.screen.blit(text, (150, 250))

        text = font.render('Modulation Frequency: ' + str(self.frequency/1000) + ' KHz', True, '#000000')
        self.screen.blit(text, (150, 300))

        if val_cost:
            color = '#ff0000'
            self.output[0] = 'Circuit cost is to high'
        elif self.output[0] == "Signal has been received":
            color = '#3d43e3'
        else:
            color = '#ff0000'
        text = font.render(self.output[0], True, color)
        self.screen.blit(text, (200, 370))

        font = pygame.font.Font('freesansbold.ttf', 16)
        text = font.render('tap anywhere to continue', True, '#000000')
        self.screen.blit(text, (700, 500))

    def display_menu(self):
        pygame.draw.rect(self.screen, '#00bda0',
                        pygame.Rect(100, 500, 1000, 100))
        pygame.draw.rect(self.screen, '#ffffff',
                        pygame.Rect(105, 505, 890, 90))
        pygame.draw.rect(self.screen, '#00bda0',
                        pygame.Rect(0, 500, 100, 100))
        pygame.draw.rect(self.screen, '#ffffff',
                        pygame.Rect(5, 505, 95, 90))

        font = pygame.font.Font('freesansbold.ttf', 16)
        text = font.render('Cost:', True, '#000000')
        self.screen.blit(text, (5, 505))

        cost = self.update_cost()
        if cost > self.cost_limit:
            color = '#ff0000'
        else:
            color = '#000000'

        text = font.render(str(cost) + ' / ' +
                        str(self.cost_limit), True, color)
        self.screen.blit(text, (5, 530))

        self.screen.blit(self.run_image, (900, 500))
        for index in range(len(self.menu_bar)):
            self.screen.blit(class_list[self.menu_bar[index]]
                            ().image, (100*(index+1), 500))

    def select_block(self, pos):
        for index in range(len(self.menu_bar)):
            if 100*(index+1) < pos[0] < 100*(index+2) and 500 < pos[1] < 600:
                return self.menu_bar[index]

        if 900 < pos[0] < 1000 and 500 < pos[1] < 600:
            self.run_circuit()

        elif 0 < pos[0] < 900 and 0 < pos[1] < 500:
            if type(self.stage[pos[1]//100][pos[0]//100]) != int:
                if self.stage[pos[1]//100][pos[0]//100].name not in ['home', 'factory']:
                    data = self.stage[pos[1]//100][pos[0]//100].id
                    self.delete_tile(pos[1]//100, pos[0]//100)
                    return data

    def update_cost(self):
        cost = 0
        for row in range(self.rows):
            for column in range(self.columns):
                data = self.stage[row][column]

                if data == -1:
                    continue
                elif data.name in ['factory', 'home']:
                    continue
                elif data.name == 'wire':
                    cost += 10
                elif data.name == 'repeater':
                    cost += 100
        return cost
