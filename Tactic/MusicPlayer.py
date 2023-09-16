import os
import pygame

class MusicPlayer:

    def __init__(self, music_folder):
        # Initialize the mixer
        pygame.mixer.init()

        # List all music files
        self.playlist = sorted([os.path.join(music_folder, f) for f in os.listdir(music_folder) if f.endswith('.mp3')])
        self.current_track = 0

        # Set up an event handler for the MUSIC_END event
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
        # self.play_next_track()


    def play_next_track(self):
        if self.current_track >= len(self.playlist):
            self.current_track = 0  # Loop back to the first track
        pygame.mixer.music.load(self.playlist[self.current_track])
        pygame.mixer.music.play()
        self.current_track += 1

