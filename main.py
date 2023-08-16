"""
checkers.py

A simple checkers engine written in Python with the pygame 1.9.1 libraries.

Here are the rules I am using: http://boardgames.about.com/cs/checkersdraughts/ht/play_checkers.htm

I adapted some code from checkers.py found at
http://itgirl.dreamhosters.com/itgirlgames/games/Program%20Leaders/ClareR/Checkers/checkers.py starting on line 159 of my program.

This is the final version of my checkers project for Programming Workshop at Marlboro College. The entire thing has been rafactored and made almost completely object oriented.

Funcitonalities include:

- Having the pieces and board drawn to the screen

- The ability to move pieces by clicking on the piece you want to move, then clicking on the square you would
  like to move to. You can change you mind about the piece you would like to move, just click on a new piece of yours.

- Knowledge of what moves are legal. When moving pieces, you'll be limited to legal moves.

- Capturing

- DOUBLE capturing etc.

- Legal move and captive piece highlighting

- Turn changes

- Automatic kinging and the ability for them to move backwords

- Automatic check for and end game.

- A silky smoooth 60 FPS!

Everest Witman - May 2014 - Marlboro College - Programming Workshop

Modified by Tanuj Barman - August 2023 (Original at: https://github.com/everestwitman/Pygame-Checkerss)
"""

import pygame, sys
from pygame.locals import *

pygame.font.init()

##COLORS##
#         R    G    B
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
HIGH = (160, 190, 255)

##DIRECTIONS##
NORTHWEST = "northwest"
NORTHEAST = "northeast"
SOUTHWEST = "southwest"
SOUTHEAST = "southeast"


class Game:
    """
    The main game control.
    """

    def __init__(self):
        self.graphics = Graphics()
        self.board = Board()

        self.turn = BLUE
        self.selected_piece = None  # a board location.
        self.hop = False
        self.selected_legal_moves = []

    def setup(self):
        """Draws the window and board at the beginning of the game"""
        # This function seems to only set up the screen and caption
        self.graphics.setup_window()

    def event_loop(self):
        """
        The event loop. This is where events are triggered
        (like a mouse click) and then effect the game state.
        """
        self.mouse_pos = self.graphics.board_coords(pygame.mouse.get_pos())  # what square is the mouse in?
        if self.selected_piece != None:
            # If there is a selected piece:
            self.selected_legal_moves = self.board.legal_moves(self.selected_piece, self.hop)

        for event in pygame.event.get():

            if event.type == QUIT: # Me just realizing event.type == QUIT is True when you x out of the board window
                self.terminate_game()

            if event.type == MOUSEBUTTONDOWN:
                if self.hop == False: # self.hop seems to be a boolean repping whether you actually jumped over a piece or not
                    if self.board.location(self.mouse_pos).occupant != None and self.board.location(
                            self.mouse_pos).occupant.color == self.turn and self.mouse_pos in self.board.pieces_that_can_move(self.turn): # ISSUE: Allows you to choose any piece even if another piece can jump
                        # If there is a piece on the tile where the mouse was clicked and it belongs to the player whos turn it is:
                        self.selected_piece = self.mouse_pos

                    elif self.selected_piece != None and self.mouse_pos in self.board.legal_moves(self.selected_piece):
                        # Else if a piece is selected and the mouse is on a tile that is a legal move:
                        self.board.move_piece(self.selected_piece, self.mouse_pos)

                        if self.mouse_pos not in self.board.adjacent(self.selected_piece):
                            # If the tile the piece just moved to is not diagonally adjacent to its starting tile (therefore it jumped):
                            self.board.remove_piece(((self.selected_piece[0] + self.mouse_pos[0]) >> 1,
                                                     (self.selected_piece[1] + self.mouse_pos[1]) >> 1))

                            self.hop = True # The piece just jumped so this is True
                            self.selected_piece = self.mouse_pos # the piece is still selected in case it can keep jumping

                        else:
                            self.end_turn()

                if self.hop == True:
                    # If the piece just jumped
                    if self.selected_piece != None and self.mouse_pos in self.board.legal_moves(self.selected_piece,
                                                                                                self.hop):
                        # if there is a selected piece (isn't this always true if we get here?) and the mouse is on a tile that is a legal move:
                        self.board.move_piece(self.selected_piece, self.mouse_pos)
                        self.board.remove_piece(((self.selected_piece[0] + self.mouse_pos[0]) >> 1,
                                                 (self.selected_piece[1] + self.mouse_pos[1]) >> 1))
                        self.selected_piece = self.mouse_pos

                    if self.board.legal_moves(self.selected_piece, self.hop) == []:
                        # If no more legal moves:
                        self.end_turn()

    def update(self):
        """Calls on the graphics class to update the game display."""
        self.graphics.update_display(self.board, self.selected_legal_moves, self.selected_piece)

# Idk why we can't just x out of the screen (since we can without this function), but imma keep it here anyways
    def terminate_game(self):
        """Quits the program and ends the game."""
        pygame.quit()
        sys.exit

    def main(self):
        """"This executes the game and controls its flow."""
        self.setup()

        while True:  # main game loop
            self.event_loop()
            self.update()

    def end_turn(self):
        """
        End the turn. Switches the current player.
        end_turn() also checks for and game and resets a lot of class attributes.
        """
        if self.turn == BLUE:
            self.turn = RED
        else:
            self.turn = BLUE

        self.selected_piece = None
        self.selected_legal_moves = []
        self.hop = False # No more extra hopping

        # Checks if the game is over
        if self.check_for_endgame():
            if self.turn == BLUE:
                self.graphics.draw_message("RED WINS!")
            else:
                self.graphics.draw_message("BLUE WINS!")

    def check_for_endgame(self):
        """
        Checks to see if a player has run out of moves or pieces. If so, then return True. Else return False.
        """
        for x in range(8):
            for y in range(8):
                if self.board.location((x, y)).color == BLACK and self.board.location(
                        (x, y)).occupant != None and self.board.location((x, y)).occupant.color == self.turn:
                    if self.board.legal_moves((x, y)) != []:
                        return False

        return True


class Graphics:
    def __init__(self):
        self.caption = "Checkers"

        self.fps = 60
        self.clock = pygame.time.Clock()

        self.window_size = 600
        self.screen = pygame.display.set_mode((self.window_size, self.window_size))
        self.background = pygame.image.load('board.png')


        self.square_size = self.window_size >> 3
        self.piece_size = self.square_size >> 1

        self.message = False

    def setup_window(self):
        """
        This initializes the window and sets the caption at the top.
        """
        pygame.init()
        pygame.display.set_caption(self.caption)

    def update_display(self, board, legal_moves, selected_piece):
        """
        This updates the current display.
        """
        self.screen.blit(self.background, (0, 0))

        self.highlight_squares(legal_moves, selected_piece)
        self.draw_board_pieces(board)

        if self.message:
            self.screen.blit(self.text_surface_obj, self.text_rect_obj)

        pygame.display.update()
        self.clock.tick(self.fps)

# This isn't needed idk why its here the board used is just an image
    def draw_board_squares(self, board):
        """
        Takes a board object and draws all of its squares to the display
        """
        for x in range(8):
            for y in range(8):
                pygame.draw.rect(self.screen, board[x][y].color,
                                 (x * self.square_size, y * self.square_size, self.square_size, self.square_size), )

    def draw_board_pieces(self, board):
        """
        Takes a board object and draws all of its pieces to the display
        """
        for x in range(8):
            for y in range(8):
                if board.matrix[x][y].occupant != None:
                    pygame.draw.circle(self.screen, board.matrix[x][y].occupant.color, self.pixel_coords((x, y)),
                                       self.piece_size)

                    if board.location((x, y)).occupant.king == True:
                        pygame.draw.circle(self.screen, GOLD, self.pixel_coords((x, y)), int(self.piece_size / 1.7),
                                           self.piece_size >> 2)

    def pixel_coords(self, board_coords):
        """
        Takes in a tuple of board coordinates (x,y)
        and returns the pixel coordinates of the center of the square at that location.
        """
        return (
        board_coords[0] * self.square_size + self.piece_size, board_coords[1] * self.square_size + self.piece_size)

    def board_coords(self, pixel):
        """
        Does the reverse of pixel_coords(). Takes in a tuple of of pixel coordinates and returns what square they are in.
        """
        return (pixel[0] // self.square_size, pixel[1] // self.square_size)

    def highlight_squares(self, squares, origin):
        """
        Squares is a list of board coordinates.
        highlight_squares highlights them.
        """
        for square in squares:
            pygame.draw.rect(self.screen, HIGH, (
            square[0] * self.square_size, square[1] * self.square_size, self.square_size, self.square_size))

        if origin != None:
            pygame.draw.rect(self.screen, HIGH, (
            origin[0] * self.square_size, origin[1] * self.square_size, self.square_size, self.square_size))

    def draw_message(self, message):
        """
        Draws message to the screen.
        """
        self.message = True
        self.font_obj = pygame.font.Font('freesansbold.ttf', 44)
        self.text_surface_obj = self.font_obj.render(message, True, HIGH, BLACK)
        self.text_rect_obj = self.text_surface_obj.get_rect()
        self.text_rect_obj.center = (self.window_size >> 1, self.window_size >> 1)


class Board:
    def __init__(self):
        self.matrix = self.new_board()

    def new_board(self):
        """
        Create a new board matrix.
        """

        # initialize squares and place them in matrix

        matrix = [[None] * 8 for i in range(8)]

        # The following code block has been adapted from
        # http://itgirl.dreamhosters.com/itgirlgames/games/Program%20Leaders/ClareR/Checkers/checkers.py
        for x in range(8):
            for y in range(8):
                if (x % 2 != 0) and (y % 2 == 0):
                    matrix[y][x] = Square(WHITE)
                elif (x % 2 != 0) and (y % 2 != 0):
                    matrix[y][x] = Square(BLACK)
                elif (x % 2 == 0) and (y % 2 != 0):
                    matrix[y][x] = Square(WHITE)
                elif (x % 2 == 0) and (y % 2 == 0):
                    matrix[y][x] = Square(BLACK)

        # initialize the pieces and put them in the appropriate squares

        for x in range(8):
            for y in range(3):
                if matrix[x][y].color == BLACK:
                    matrix[x][y].occupant = Piece(RED, x, y)
            for y in range(5, 8):
                if matrix[x][y].color == BLACK:
                    matrix[x][y].occupant = Piece(BLUE, x, y)
        return matrix

# Not used anywhere else right now
    def board_string(self, board):
        """
        Takes a board and returns a matrix of the board space colors. Used for testing new_board()
        """

        board_string = [[None] * 8] * 8

        for x in range(8):
            for y in range(8):
                if board[x][y].color == WHITE:
                    board_string[x][y] = "WHITE"
                else:
                    board_string[x][y] = "BLACK"

        return board_string

    def rel(self, dir, pixel):
        """
        Returns the coordinates one square in a different direction to (x,y).

        ===DOCTESTS===

        >>> board = Board()

        >>> board.rel(NORTHWEST, (1,2))
        (0,1)

        >>> board.rel(SOUTHEAST, (3,4))
        (4,5)

        >>> board.rel(NORTHEAST, (3,6))
        (4,5)

        >>> board.rel(SOUTHWEST, (2,5))
        (1,6)
        """
        x = pixel[0]
        y = pixel[1]
        if dir == NORTHWEST:
            return (x - 1, y - 1)
        elif dir == NORTHEAST:
            return (x + 1, y - 1)
        elif dir == SOUTHWEST:
            return (x - 1, y + 1)
        elif dir == SOUTHEAST:
            return (x + 1, y + 1)
        else:
            return 0

    def adjacent(self, pixel):
        """
        Returns a list of squares locations that are adjacent (on a diagonal) to (x,y).
        """
        x = pixel[0]
        y = pixel[1]

        return [self.rel(NORTHWEST, (x, y)), self.rel(NORTHEAST, (x, y)), self.rel(SOUTHWEST, (x, y)),
                self.rel(SOUTHEAST, (x, y))]

    def location(self, pixel):
        """
        Takes a set of coordinates as arguments and returns self.matrix[x][y]
        This can be faster than writing something like self.matrix[coords[0]][coords[1]]
        """
        x = pixel[0]
        y = pixel[1]

        return self.matrix[x][y]

    def blind_legal_moves(self, pixel):
        """
        Returns a list of blind legal move locations from a set of coordinates (x,y) on the board.
        If that location is empty, then blind_legal_moves() return an empty list.
        """

        x = pixel[0]
        y = pixel[1]
        if self.matrix[x][y].occupant != None:
            # If there is a piece on that tile

            if self.matrix[x][y].occupant.king == False and self.matrix[x][y].occupant.color == BLUE:
                # If the piece is a regular blue piece
                blind_legal_moves = [self.rel(NORTHWEST, (x, y)), self.rel(NORTHEAST, (x, y))]

            elif self.matrix[x][y].occupant.king == False and self.matrix[x][y].occupant.color == RED:
                # If the piece is a regular red piece
                blind_legal_moves = [self.rel(SOUTHWEST, (x, y)), self.rel(SOUTHEAST, (x, y))]

            else:
                # If the piece is a king
                blind_legal_moves = [self.rel(NORTHWEST, (x, y)), self.rel(NORTHEAST, (x, y)),
                                     self.rel(SOUTHWEST, (x, y)), self.rel(SOUTHEAST, (x, y))]

        else:
            blind_legal_moves = []

        return blind_legal_moves

    def legal_moves(self, pixel, hop=False):
        """
        Returns a list of legal move locations from a given set of coordinates (x,y) on the board.
        If that location is empty, then legal_moves() returns an empty list.
        """

        x = pixel[0]
        y = pixel[1]
        blind_legal_moves = self.blind_legal_moves((x, y))
        legal_moves = []

        if hop == False:
            # If the piece can jump
            if self.can_jump(pixel):
                for move in blind_legal_moves:
                    jump_coord = (move[0] + (move[0] - x), move[1] + (move[1] - y))
                    if self.legal_jump(pixel, move, jump_coord):
                        legal_moves.append(jump_coord)
            # If the piece cannot jump
            else:
                for move in blind_legal_moves:
                    if self.on_board(move):
                        if self.location(move).occupant == None:
                            legal_moves.append(move)

        else:  # hop == True
            for move in blind_legal_moves:
                jump_coord = (move[0] + (move[0] - x), move[1] + (move[1] - y))
                if self.legal_jump(pixel, move, jump_coord):
                    legal_moves.append(jump_coord)

        return legal_moves

    def legal_jump(self, pixel, move, jump_coord):
        if self.on_board(move):
            if self.location(move).occupant != None:
                not_same_color = self.location(move).occupant.color != self.location(pixel).occupant.color
                return not_same_color and self.on_board(jump_coord) and self.location(jump_coord).occupant == None
        return False

    def can_jump(self, pixel):
        '''
        Checks if the given piece can jump or not
        '''
        blind_legal_moves = self.blind_legal_moves(pixel)
        can_jump = False
        for move in blind_legal_moves:
            jump_coord = (move[0] + (move[0] - pixel[0]), move[1] + (move[1] - pixel[1]))
            can_jump = can_jump or self.legal_jump(pixel, move, jump_coord)

        return can_jump

    def pieces_that_can_move(self, turn):
        '''
        Returns the list of all pieces the player can legally move
        If there are any pieces that can jump, then the list will consist only of those pieces
        Otherwise, every piece that has a tile to move to will be returned
        player_color should be RED or BLUE
        '''
        # ONE LINER (have fun reading :D)

        x = [(piece.x, piece.y) for piece in [space for space in [square.occupant for square in [piece for column in self.matrix for piece in column]] if space != None] if piece.color == turn]; return [coord for coord in x if self.can_jump(coord)] if any(self.can_jump(coord) for coord in x) else [coord for coord in x if self.legal_moves(coord) != []]

        '''Uncomment the below code for the readable version of the code above'''

        # # Flattens the 2d matrix into a 1d list
        # player_pieces = [piece for column in self.matrix for piece in column]
        #
        # # Returns the occupant of each sqaure
        # player_pieces = [square.occupant for square in player_pieces]
        #
        # # Filters out all empty spaces
        # while None in player_pieces:
        #     player_pieces.remove(None)
        #
        # # The pieces only count coords when initialized, and those coords never change, so when u move a piece u gotta update corods
        #
        # # Gets rid of all pieces that don't belong to the current player and converts them to their coordinates
        # player_pieces = [(piece.x, piece.y) for piece in player_pieces if piece.color == turn]
        #
        # pieces_that_can_move = [] # The list of all pieces that can legally move
        # there_are_pieces_that_can_jump = False # Long name for clarity
        #
        # # Checks if there are pieces that can jump
        # for coord in player_pieces:
        #     there_are_pieces_that_can_jump = there_are_pieces_that_can_jump or self.can_jump(coord)
        #
        # # If there are pieces that can jump, add every piece that can jump to the list of legal moves
        # if there_are_pieces_that_can_jump:
        #     for coord in player_pieces:
        #         if self.can_jump(coord):
        #             pieces_that_can_move.append(coord)
        #
        # # Else add every piece that can move to the list of legal moves
        # else:
        #     for coord in player_pieces:
        #         if self.legal_moves(coord) != []:
        #             pieces_that_can_move.append(coord)
        #
        # return pieces_that_can_move

    def remove_piece(self, pixel):
        """
        Removes a piece from the board at position (x,y).
        """
        x = pixel[0]
        y = pixel[1]
        self.matrix[x][y].occupant = None

    def move_piece(self, pixel_start, pixel_end):
        """
        Move a piece from (start_x, start_y) to (end_x, end_y).
        """
        start_x = pixel_start[0]
        start_y = pixel_start[1]
        end_x = pixel_end[0]
        end_y = pixel_end[1]

        self.matrix[end_x][end_y].occupant = self.matrix[start_x][start_y].occupant
        self.matrix[end_x][end_y].occupant.x, self.matrix[end_x][end_y].occupant.y = end_x, end_y # updates the piece's coords
        self.remove_piece((start_x, start_y))

        self.king((end_x, end_y))

    def is_end_square(self, coords):
        """
        Is passed a coordinate tuple (x,y), and returns true or
        false depending on if that square on the board is an end square.

        ===DOCTESTS===

        >>> board = Board()

        >>> board.is_end_square((2,7))
        True

        >>> board.is_end_square((5,0))
        True

        >>>board.is_end_square((0,5))
        False
        """

        if coords[1] == 0 or coords[1] == 7:
            return True
        else:
            return False

    def on_board(self, pixel):
        """
        Checks to see if the given square (x,y) lies on the board.
        If it does, then on_board() return True. Otherwise it returns false.

        ===DOCTESTS===
        >>> board = Board()

        >>> board.on_board((5,0)):
        True

        >>> board.on_board(-2, 0):
        False

        >>> board.on_board(3, 9):
        False
        """

        x = pixel[0]
        y = pixel[1]
        if x < 0 or y < 0 or x > 7 or y > 7:
            return False
        else:
            return True

    def king(self, pixel):
        """
        Takes in (x,y), the coordinates of square to be considered for kinging.
        If it meets the criteria, then king() kings the piece in that square and kings it.
        """
        x = pixel[0]
        y = pixel[1]
        if self.location((x, y)).occupant != None:
            if (self.location((x, y)).occupant.color == BLUE and y == 0) or (
                    self.location((x, y)).occupant.color == RED and y == 7):
                self.location((x, y)).occupant.king = True


class Piece:
    def __init__(self, color, x, y, king=False):
        self.color = color
        self.king = king
        self.x = x
        self.y = y

class Square:
    def __init__(self, color, occupant=None):
        self.color = color  # color is either BLACK or WHITE
        self.occupant = occupant  # occupant is a Square object


def main():
    game = Game()
    game.main()

# we need this for some reason but idk why
if __name__ == "__main__":
    main()