'''
AtariMDPClass.py: Contains implementation for MDPs of the Atari Learning Environment.
'''

# Local imports.
from MDPClass import MDP
from grid_world.GridWorldStateClass import GridWorldState
from atari.AtariStateClass import AtariState

# Python imports.
import numpy
import random
import sys
import os
import random
import ale_python_interface as ale_interface

class AtariMDP(MDP):
    ''' Class for a Atari MDPs '''

    def __init__(self, rom="breakout", display_game_screen=False, grayscale=False, image_to_object=False):
        '''
        Args:
            rom (str): path to a rom file. Put roms in the "/roms/" dir.
        '''
        self.image_to_object = image_to_object
        self.grayscale = grayscale
        self._setup_ale(rom, display_game_screen)
        MDP.__init__(self, self.actions, self._transition_func, self._reward_func, init_state=self.init_state)

    def _setup_ale(self, rom, display_game_screen):
        '''
        Args:
            rom (str): path to Atari rom.
            display_game_screen (bool): true iff the Atari screen should be displayed.

        Summary:
            Initializes the Atari Learning Environment.
        '''
        # Create ALE Interface and set the seed.
        self.ale = ale_interface.ALEInterface()
        self.ale.setInt('random_seed', 123)
        
        # Setup visuals and sound depending on os.
        if display_game_screen:
            if sys.platform == 'darwin':
                import pygame
                pygame.init()
                self.ale.setBool('sound', False) # Sound doesn't work on OSX
            elif sys.platform.startswith('linux'):
                self.ale.setBool('sound', True)
            self.ale.setBool('display_screen', True)
        
        # Load the ROM.
        self.rom = rom.replace(".bin","")
        full_rom_path = os.path.dirname(os.path.realpath(__file__)) + "/roms/" + self.rom + ".bin"
        self.ale.loadROM(full_rom_path)

        # Grab game details.
        self.ram_size = self.ale.getRAMSize()
        self.screen_width, self.screen_height = self.ale.getScreenDims()
        self.actions = self.ale.getLegalActionSet()

        # Get Ram, initial image info.
        ram = numpy.zeros((self.ram_size),dtype=numpy.uint8)
        ram_state = self.ale.getRAM(ram)
        screen_data = self.ale.getScreenGrayscale() if self.grayscale else self.ale.getScreenRGB()

        # Make initial state.
        self.init_state = AtariState(screen_data, ram_state, objects_from_image=self.image_to_object)
    
    def _reward_func(self, state, action):
        '''
        Args:
            state (AtariState)
            action (str)

        Returns
            (float)
        '''
        # Get reward.
        reward = self.ale.act(action)

        return reward

    def _transition_func(self, state, action):
        '''
        Args:
            state (AtariState)
            action (str)

        Returns
            (State)
        '''
         # Get Ram info.
        ram = numpy.zeros((self.ram_size),dtype=numpy.uint8)
        ram_state = self.ale.getRAM(ram)
        
        # Get screen info.
        screen_data = self.ale.getScreenGrayscale() if self.grayscale else self.ale.getScreenRGB()

        return AtariState(screen_data, ram_state, terminal=self.ale.game_over(), objects_from_image=self.image_to_object)

    def reset(self):
        self.ale.reset_game()

    def __str__(self):
        return "atari_" + self.rom

def main():
    if len(sys.argv) < 2:
        print 'Usage:', sys.argv[0], 'rom_file'
        sys.exit()

    AtariMDP(rom=sys.argv[1])

if __name__ == "__main__":
    main()
