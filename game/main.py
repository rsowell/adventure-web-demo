import asyncio
import textwrap

import pygame

class Monster:
    def __init__(self, name, armor, description):
        self.name = name
        self.armor = armor
        self.description = description


class Treasure:
    def __init__(self, name, value, description):
        self.name = name
        self.value = value
        self.description = description


class Weapon:
    def __init__(self, name, damage, description):
        self.name = name
        self.damage = damage
        self.description = description


class Room:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.neighbors = {}
        self.monster = None
        self.treasure = None
        self.weapon = None

    def add_neighbor(self, direction, room):
        self.neighbors[direction] = room

    def get_neighbor(self, direction):
        return self.neighbors.get(direction)

    def list_exits(self):
        return ", ".join(self.neighbors.keys())


class TextAdventure:
    def __init__(self):
        # Create rooms
        entrance = Room(
            "entrance",
            "a cramped natural passage filled with dripping stalactites"
        )
        hall = Room(
            "hall",
            "a vast hall with a vaulted stone ceiling"
        )
        armory = Room(
            "armory",
            "an abandoned armory"
        )
        lair = Room(
            "lair",
            "a large cavern steaming with volcanic heat"
        )

        # Connect rooms
        entrance.add_neighbor("north", hall)
        hall.add_neighbor("south", entrance)
        hall.add_neighbor("west", armory)
        hall.add_neighbor("east", lair)
        armory.add_neighbor("east", hall)
        lair.add_neighbor("west", hall)

        # Add monsters
        hall.monster = Monster("wolf", 2, "a ferocious, snarling wolf")
        lair.monster = Monster("dragon", 4, "a fire-breathing dragon")

        # Add treasures
        hall.treasure = Treasure("diamond", 10, "a huge, glittering diamond")
        lair.treasure = Treasure(
            "chalice",
            90,
            "a golden chalice encrusted with gemstones"
        )

        # Add a weapon
        armory.weapon = Weapon("axe", 5, "a mighty battle axe")

        # Starting state
        self.current_room = entrance
        self.best_weapon_damage = 3
        self.score = 0
        self.game_over = False
        self.messages = []


    def list_commands(self):
        self.write("Examples of commands:")
        self.write("  attack wolf")
        self.write("  go north")
        self.write("  look")
        self.write("  take diamond")
        self.write("  quit")

    def look(self):
        self.write(f"You are in {self.current_room.description}.")

        if self.current_room.monster is not None:
            self.write(f"There is {self.current_room.monster.description} here.")

        if self.current_room.weapon is not None:
            self.write(f"There is {self.current_room.weapon.description} here.")

        if self.current_room.treasure is not None:
            self.write(f"There is {self.current_room.treasure.description} here.")

        self.write(f"Exits: {self.current_room.list_exits()}")

    def go(self, direction):
        destination = self.current_room.get_neighbor(direction)

        if destination is None:
            self.write("You can't go that way from here.")
        else:
            self.current_room = destination

    def attack(self, name):
        monster = self.current_room.monster

        if monster is not None and monster.name == name:
            if self.best_weapon_damage > monster.armor:
                self.write("You strike it dead!")
                self.current_room.monster = None
            else:
                self.write("Your blow bounces off harmlessly.")
                self.write(f"The {monster.name} eats your head!")
                self.write()
                self.write("GAME OVER")
                self.game_over = True
        else:
            self.write(f"There is no {name} here.")

    def take(self, name):
        treasure = self.current_room.treasure
        weapon = self.current_room.weapon

        if treasure is not None and treasure.name == name:
            self.current_room.treasure = None
            self.score += treasure.value
            self.write(f"Your score is now {self.score} out of 100.")

            if self.score == 100:
                self.write()
                self.write("YOU WIN!")
                self.game_over = True

        elif weapon is not None and weapon.name == name:
            self.current_room.weapon = None

            if weapon.damage > self.best_weapon_damage:
                self.best_weapon_damage = weapon.damage
                self.write("You'll be a more effective fighter with this!")

        else:
            self.write(f"There is no {name} here.")

    def write(self, message=""):
        """Add text to the game window's message log."""
        self.messages.append(str(message))

    def handle_command(self, line):
        words = line.lower().split()

        if len(words) == 0:
            return

        command = words[0]

        if command == "quit":
            self.game_over = True
            return

        if self.current_room.monster is not None and command not in ["attack", "look"]:
            self.write("You can't do that with unfriendlies about.")
            self.list_commands()
            return

        if command == "look":
            self.look()
        elif command == "go" and len(words) > 1:
            self.go(words[1])
        elif command == "attack" and len(words) > 1:
            self.attack(words[1])
        elif command == "take" and len(words) > 1:
            self.take(words[1])
        else:
            self.write("I don't understand that.")
            self.list_commands()

    # def run(self):
    #     self.write("Welcome to the dungeon!")
    #     self.list_commands()
    #     self.write()

    #     while not self.game_over:
    #         self.write(f"You are in the {self.current_room.name}.")
    #         command = input("> ")
    #         self.handle_command(command)
    #         self.write()

    async def run(self):
        """Read keyboard events and draw the game without blocking."""
        pygame.init()
        screen = pygame.display.set_mode((960, 640))
        pygame.display.set_caption("Dungeon Adventure")
        # The built-in font needs no separate font file.
        font = pygame.font.Font(None, 28)
        clock = pygame.time.Clock()
        command = ""
        running = True

        self.write("Welcome to Sewanee!")
        self.list_commands()
        self.look()

        # Keep drawing after a win/loss so the final message stays visible.
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif not self.game_over:
                        if event.key == pygame.K_RETURN:
                            self.write("> " + command)
                            self.handle_command(command)
                            command = ""
                            if not self.game_over:
                                self.write(
                                    f"You are in the {self.current_room.name}."
                                )
                        elif event.key == pygame.K_BACKSPACE:
                            command = command[:-1]
                        elif event.unicode.isprintable():
                            command = (command + event.unicode)[:60]

            screen.fill((20, 24, 32))

            # Wrap messages and show only the most recent lines.
            lines = []
            for message in self.messages:
                lines.extend(textwrap.wrap(message, width=65) or [""])
            for index, line in enumerate(lines[-17:]):
                surface = font.render(line, True, (235, 235, 235))
                screen.blit(surface, (24, 20 + index * 30))

            if self.game_over:
                prompt = "Game ended. Refresh to restart; Esc closes the game."
            else:
                prompt = "> " + command + "_"
            surface = font.render(prompt, True, (150, 220, 180))
            screen.blit(surface, (24, 590))
            pygame.display.flip()
            clock.tick(30)
            # Give the browser a turn on every frame.
            await asyncio.sleep(0)

        pygame.quit()

game = TextAdventure()
asyncio.run(game.run())
