from menu import MainMenu
from Game import StrategyGame
from BuildTeam import TeamBuilder

class MainFrame():
    def __init__(self):
        pass

    def run(self):
        running = True
        while running:
            main_menu = MainMenu()
            selected_menu_item = main_menu.run()
            if selected_menu_item == "New Game":
                team_builder = TeamBuilder()
                selected_team = team_builder.run()
                game = StrategyGame(selected_team)
                game.game_loop()
            elif selected_menu_item == "Quit":
                running = False

main = MainFrame()
main.run()
