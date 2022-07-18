from image import images, images2
import copy
import pygame
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, Float, create_engine
from sqlalchemy.orm import sessionmaker



Base = declarative_base()

class Stats(Base):
    """Used for database"""
    __tablename__ = 'Games'
    id_Match = Column(Integer, primary_key=True)
    Black_Res = Column(Float)
    White_Res = Column(Float)
    Game_Length = Column(Integer)

engine = create_engine('sqlite:///Games.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
pygame.init()
win = pygame.display.set_mode((750, 750))
font = pygame.font.SysFont('Arial', 25)
pygame.display.set_caption("Chess game")
COLORS = [(238, 238, 210, 255), (118, 150, 86, 255)]  # Default Board
COLORS_CLICKED = [(255, 242, 0, 255), (255, 201, 14, 255)]  # After cllicking on a piece
COLORS_POSSIBLE = [(250, 250, 160, 255), (146, 158, 33, 255)]  # Colors of possible tiles
En_passant_White = 8 * [False]  # Keeping track of possible En passant moves
En_passant_Black = 8 * [False]
x = 55  # margin of a chessboard
y = 55
tile_side = 75
border = tile_side + 5
BOARD = [
    ["BR", "BK", "BB", "BQ", "BS", "BB", "BK", "BR"],
    ["BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP"],
    ["-", "-", "-", "-", "-", "-", "-", "-"],
    ["-", "-", "-", "-", "-", "-", "-", "-"],
    ["-", "-", "-", "-", "-", "-", "-", "-"],
    ["-", "-", "-", "-", "-", "-", "-", "-"],
    ["WP", "WP", "WP", "WP", "WP", "WP", "WP", "WP"],
    ["WR", "WK", "WB", "WQ", "WS", "WB", "WK", "WR"]
]
Black_Pos = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
             (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7)]
White_Pos = [(6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7),
             (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)]
Whites = ["WP", "WQ", "WR", "WK", "WB", "WS"]
Blacks = ["BP", "BQ", "BR", "BK", "BB", "BS"]
Figures = Whites + Blacks
Turn = True  # Whites -> True, Blacks -> False
run = True  # Set to false when shutting down a program
clicked = False
checked = False
endgame = False  # Set to True after a checkmate, or a stalemate
promotion = False  # Set to True when promoting a pawn
review = False  # Turning on "Review Game", can be set to True after finishing a game
# Castling requirements
white_king_fmove = True
black_king_fmove = True
white_lrook_fmove = True
white_rrook_fmove = True
black_lrook_fmove = True
black_rrook_fmove = True
temp_figure = []  # Used when promoting a pawn, remember a state before promotion in case player decide to cancel a move
Game_Report = []  # Remember which move were played, used in reviewing game
White_Passant = False  # Used to add a specific input to Game_Report
Black_Passant = False  # Used to add a specific input to Game_Report
castle = False         # Used to add a specific input to Game_Report
game_counter = 0  # Keep track of how many moves were played, information later added to database





def restart_game():
    """Bring the game back to its original state"""
    global BOARD, white_king_fmove, black_king_fmove
    global white_lrook_fmove, white_rrook_fmove
    global black_lrook_fmove, black_rrook_fmove
    global endgame, promotion, Turn, clicked, checked
    global Black_Pos, White_Pos, game_counter
    global Game_Report
    BOARD = [
        ["BR", "BK", "BB", "BQ", "BS", "BB", "BK", "BR"],
        ["BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP"],
        ["-", "-", "-", "-", "-", "-", "-", "-"],
        ["-", "-", "-", "-", "-", "-", "-", "-"],
        ["-", "-", "-", "-", "-", "-", "-", "-"],
        ["-", "-", "-", "-", "-", "-", "-", "-"],
        ["WP", "WP", "WP", "WP", "WP", "WP", "WP", "WP"],
        ["WR", "WK", "WB", "WQ", "WS", "WB", "WK", "WR"]
    ]
    Black_Pos = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
                 (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7)]
    White_Pos = [(6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7),
                 (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)]
    Turn = True
    clicked = False
    checked = False
    endgame = False
    promotion = False
    white_king_fmove = True
    black_king_fmove = True
    white_lrook_fmove = True
    white_rrook_fmove = True
    black_lrook_fmove = True
    black_rrook_fmove = True
    game_counter = 0


def draw(i, j, col):
    """Takes in two numbers representing row and column and a list of numbers which represent color
    Draw a rectangle using this parameters"""
    pygame.draw.rect(win, col[(i+j) % 2],
                     (x+i*border, y+j*border, tile_side, tile_side))


def Draw_Board(COL):
    """Draw a board 8x8 full of rectangles"""
    for j in range(8):
        for i in range(8):
            draw(i, j, COL)
    pygame.display.update()


def show_move(turn, j, i, figure, Board, defend, click):
    """Returns a list of possible tiles to move for given piece

        Parameters:
            turn (boolean): True -> White turn; False -> Black turn
            j (int): Integer from 0 to 7, index of a row
            i (int): Integer from 0 to 7, index of a column
            figure (string): Type of piece
            Board (string): list of list of string, represent a chessboard
            defend (boolean): Parameter used to check if given move won't result in discover check, need to be set to
            False afterwards to prevent infinte loop
            click (boolean): True -> function called when player clicked on a piece, used while checking castling,
            which is not possible otherwise (can't be used to escape check)

        Returns:
            Move_Possible ((int,int)) list of tuples of ints, representing possible tiles to move for given piece"""
    Move_Possible = []
    Move_Not_Possible = []
    En_pasan = (10, 10)
    if figure == "WP":
        if j-1 >= 0 and Board[j-1][i] == "-":
            Move_Possible.append((j-1, i))
            if j == 6 and Board[j-2][i] == "-":
                Move_Possible.append((j-2, i))
        if (j-1 >= 0 and i-1 >= 0):
            if Board[j-1][i-1] in Blacks:
                Move_Possible.append((j-1, i-1))
            if j == 3 and En_passant_Black[i-1]:
                Move_Possible.append((j-1, i-1))
                En_pasan = [(j-1, i-1), (j, i-1)]
        if (j-1 >= 0 and i+1 <= 7):
            if Board[j-1][i+1] in Blacks:
                Move_Possible.append((j-1, i+1))
            if j == 3 and En_passant_Black[i+1]:
                Move_Possible.append((j-1, i+1))
                En_pasan = [(j-1, i+1), (j, i+1)]
    elif figure == "BP":
        if j+1 <= 7 and Board[j+1][i] == "-":
            Move_Possible.append((j+1, i))
            if j == 1 and Board[j+2][i] == "-":
                Move_Possible.append((j+2, i))
        if (j+1 <= 7 and i-1 >= 0):
            if Board[j+1][i-1] in Whites:
                Move_Possible.append((j+1, i-1))
            if j == 4 and En_passant_White[i-1]:
                Move_Possible.append((j+1, i-1))
                En_pasan = [(j+1, i-1), (j, i-1)]
        if (j+1 <= 7 and i+1 <= 7):
            if Board[j+1][i+1] in Whites:
                Move_Possible.append((j+1, i+1))
            if j == 4 and En_passant_White[i+1]:
                Move_Possible.append((j+1, i+1))
                En_pasan = [(j+1, i+1), (j, i+1)]
    elif figure == "BK" or figure == "WK":
        if turn:
            Enemy = Blacks
        else:
            Enemy = Whites
        KPOS = [(1, 2), (1, -2), (-1, 2), (-1, -2),
                (2, 1), (2, -1), (-2, 1), (-2, -1)]
        for l in range(8):
            for k in range(8):
                for m, n in KPOS:
                    if(k != i or l != j) and i == k+m and j == l+n \
                            and (Board[l][k] == "-" or Board[l][k] in Enemy):
                        Move_Possible.append((l, k))
                        break
    elif figure == "WS":
        KPOS = [(1, 0), (1, 1), (1, -1), (-1, 0),
                (-1, 1), (-1, -1), (0, 1), (0, -1)]
        for l in range(8):
            for k in range(8):
                for m, n in KPOS:
                    if(k != i or l != j) and (i, j) == (k+m, l+n) \
                            and Board[l][k] not in Whites:
                        Move_Possible.append((l, k))
                        break
        if white_king_fmove and click:
            if white_lrook_fmove and Board[7][1:4].count("-") == 3:
                BOARD_temp = copy.deepcopy(Board)
                BOARD_temp[7][3] = BOARD_temp[j][i]
                BOARD_temp[j][i] = "-"
                if not check_checker(not turn, BOARD_temp, False):
                    Move_Possible.append((7, 2))
            if white_rrook_fmove and Board[7][5:7].count("-") == 2:
                BOARD_temp = copy.deepcopy(Board)
                BOARD_temp[7][5] = BOARD_temp[j][i]
                BOARD_temp[j][i] = "-"
                if not check_checker(not turn, BOARD_temp, False):
                    Move_Possible.append((7, 6))
    elif figure == "BS":
        KPOS = [(1, 0), (1, 1), (1, -1), (-1, 0),
                (-1, 1), (-1, -1), (0, 1), (0, -1)]
        for l in range(8):
            for k in range(8):
                for m, n in KPOS:
                    if(k != i or l != j) and (i, j) == (k+m, l+n) \
                            and Board[l][k] not in Blacks:
                        Move_Possible.append((l, k))
                        break
        if black_king_fmove and click:
            if black_lrook_fmove and Board[0][1:4].count("-") == 3:
                BOARD_temp = copy.deepcopy(Board)
                BOARD_temp[0][3] = BOARD_temp[j][i]
                BOARD_temp[j][i] = "-"
                if not check_checker(not turn, BOARD_temp, False):
                    Move_Possible.append((0, 2))
            if black_rrook_fmove and Board[0][5:7].count("-") == 2:
                BOARD_temp = copy.deepcopy(Board)
                BOARD_temp[0][5] = BOARD_temp[j][i]
                BOARD_temp[j][i] = "-"
                if not check_checker(not turn, BOARD_temp, False):
                    Move_Possible.append((0, 6))
    elif figure == "WR" or figure == "BR":
        if figure == "BR":
            Enemy = Whites
        else:
            Enemy = Blacks
        for l in range(8):
            for k in range(8):
                if(i == k or j == l) and (k != i or l != j):
                    if Board[l][k] in Figures:
                        if Board[l][k] in Enemy:
                            Move_Possible.append((l, k))
                        Move_Not_Possible.append((l, k))
                    else:
                        Move_Possible.append((l, k))
        for (y_pos, x_pos) in Move_Not_Possible:
            if y_pos == j and x_pos > i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] == y_pos and \
                            Move_Possible[iter][1] > x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
            if y_pos == j and x_pos < i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] == y_pos and \
                            Move_Possible[iter][1] < x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
            if y_pos > j and x_pos == i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] > y_pos and \
                            Move_Possible[iter][1] == x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
            if y_pos < j and x_pos == i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] < y_pos and \
                            Move_Possible[iter][1] == x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
    elif figure == "WB" or figure == "BB":
        if figure == "BB":
            Enemy = Whites
        else:
            Enemy = Blacks
        for l in range(8):
            for k in range(8):
                if abs(k-i) == abs(j-l) != 0:
                    if Board[l][k] in Figures:
                        if Board[l][k] in Enemy:
                            Move_Possible.append((l, k))
                        Move_Not_Possible.append((l, k))
                    else:
                        Move_Possible.append((l, k))
        for (y_pos, x_pos) in Move_Not_Possible:
            if y_pos > j and x_pos > i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] > y_pos and \
                            Move_Possible[iter][1] > x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
            if y_pos > j and x_pos < i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] > y_pos and \
                            Move_Possible[iter][1] < x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
            if y_pos < j and x_pos < i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] < y_pos and \
                            Move_Possible[iter][1] < x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
            if y_pos < j and x_pos > i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] < y_pos and \
                            Move_Possible[iter][1] > x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
    elif figure == "BQ" or figure == "WQ":
        if figure == "BQ":
            Enemy = Whites
        else:
            Enemy = Blacks
        for l in range(8):
            for k in range(8):
                if (k != i or l != j) and(abs(k-i) == abs(j-l) or i == k or j == l):
                    if Board[l][k] in Figures:
                        if Board[l][k] in Enemy:
                            Move_Possible.append((l, k))
                        Move_Not_Possible.append((l, k))
                    else:
                        Move_Possible.append((l, k))
        for (y_pos, x_pos) in Move_Not_Possible:
            if y_pos > j and x_pos > i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] > y_pos and Move_Possible[iter][1] > x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
            if y_pos > j and x_pos < i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] > y_pos and Move_Possible[iter][1] < x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
            if y_pos < j and x_pos < i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] < y_pos and Move_Possible[iter][1] < x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
            if y_pos < j and x_pos > i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] < y_pos and Move_Possible[iter][1] > x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
            if y_pos == j and x_pos > i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] == y_pos and Move_Possible[iter][1] > x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
            if y_pos == j and x_pos < i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] == y_pos and Move_Possible[iter][1] < x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
            if y_pos > j and x_pos == i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] > y_pos and Move_Possible[iter][1] == x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
            if y_pos < j and x_pos == i:
                l = len(Move_Possible)
                iter = 0
                while iter < l:
                    if Move_Possible[iter][0] < y_pos and Move_Possible[iter][1] == x_pos:
                        del Move_Possible[iter]
                        l -= 1
                    else:
                        iter += 1
    l = len(Move_Possible)
    iter = 0
    while iter < l and defend:
        # Check if move won't result in exposing king
        BOARD_temp = copy.deepcopy(Board)
        BOARD_temp[Move_Possible[iter][0]][Move_Possible[iter][1]] = BOARD_temp[j][i]
        BOARD_temp[j][i] = "-"
        if En_pasan[0] == (Move_Possible[iter]):
            BOARD_temp[En_pasan[1][0]][En_pasan[1][1]] = "-"
        if check_checker(not turn, BOARD_temp, False):
            del Move_Possible[iter]
            l -= 1
        else:
            iter += 1
    return Move_Possible


def check_checker(turn, Board, defend):
    """Takes in a boolean representing whom turn it is, setup of a board and
     another boolean responsible for stating if we called the function before moving a piece,
     or after we moved a piece
     Function looks at the board and checks if there is any check at the moment"""
    if turn:
        for (y_pos, x_pos) in White_Pos:
            MP = show_move(turn, y_pos, x_pos, Board[y_pos][x_pos], Board, defend, False)
            for (mp_y_pos, mp_x_pos) in MP:
                if Board[mp_y_pos][mp_x_pos] == "BS":
                    return True
    else:
        for (y_pos, x_pos) in Black_Pos:
            MP = show_move(turn, y_pos, x_pos, Board[y_pos][x_pos], Board, defend, False)
            for (mp_y_pos, mp_x_pos) in MP:
                if Board[mp_y_pos][mp_x_pos] == "WS":
                    return True


def end_game_checker(Board, turn):
    """Takes in a board setup and a boolean representing which turn it is
    Function checks if end of the game happened (either checkmate or stalemate) and return
    adequate boolean value"""
    if turn:
        for(y_pos, x_pos) in White_Pos:
            MP = show_move(turn, y_pos, x_pos, Board[y_pos][x_pos], Board, True, False)
            if len(MP) != 0:
                return False
        if check_checker(not turn, Board, True):
            print("Check mate!")
            RES = Stats(Black_Res=1, White_Res=0, Game_Length=game_counter)
        else:
            print("Stale mate!")
            RES = Stats(Black_Res=0.5, White_Res=0.5, Game_Length=game_counter)
    else:
        for(y_pos, x_pos) in Black_Pos:
            MP = show_move(turn, y_pos, x_pos, Board[y_pos][x_pos], Board, True, False)
            if len(MP) != 0:
                return False
        if check_checker(not turn, Board, True):
            print("Check mate!")
            RES = Stats(Black_Res=0, White_Res=1, Game_Length=game_counter)
        else:
            RES = Stats(Black_Res=0.5, White_Res=0.5, Game_Length=game_counter)
            print("Stale mate!")
    # Game end, result is added to database
    session.add(RES)
    session.commit()
    session.close()
    return True


def Put_pictures():
    """Function for each figure on the board paste adequate image"""
    for X, i in enumerate(BOARD):
        for Y, j in enumerate(i):
            if j == "WP":
                win.blit(images[0], (x + 13 + Y * border, y + 13 + X * border))
            elif j == "BP":
                win.blit(images[1], (x + 13 + Y * border, y + 13 + X * border))
            elif j == "WR":
                win.blit(images[2], (x + 13 + Y * border, y + 13 + X * border))
            elif j == "BR":
                win.blit(images[3], (x + 13 + Y * border, y + 13 + X * border))
            elif j == "WS":
                win.blit(images[4], (x + 13 + Y * border, y + 13 + X * border))
            elif j == "BS":
                win.blit(images[5], (x + 13 + Y * border, y + 13 + X * border))
            elif j == "WK":
                win.blit(images[6], (x + 13 + Y * border, y + 13 + X * border))
            elif j == "BK":
                win.blit(images[7], (x + 13 + Y * border, y + 13 + X * border))
            elif j == "WB":
                win.blit(images[8], (x + 13 + Y * border, y + 13 + X * border))
            elif j == "BB":
                win.blit(images[9], (x + 13 + Y * border, y + 13 + X * border))
            elif j == "WQ":
                win.blit(images[10], (x + 13 + Y * border, y + 13 + X * border))
            elif j == "BQ":
                win.blit(images[11], (x + 13 + Y * border, y + 13 + X * border))


# Prepare a default state of the game
def Play_Game():
    global BOARD, white_king_fmove, black_king_fmove
    global white_lrook_fmove, white_rrook_fmove
    global black_lrook_fmove, black_rrook_fmove
    global endgame, promotion, Turn, clicked, checked
    global Black_Pos, White_Pos, game_counter
    global Game_Report, review, castle, White_Passant
    global Black_Passant
    Draw_Board(COLORS)
    Put_pictures()
    run = True
    while run:
        # event handler
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if review:
                    # Only happen when option "review game" was chosen at the end of the game
                    if len(Game_Report) == 0:
                        review = False
                        restart_game()
                    else:
                        fir = Game_Report[0][1][0]
                        sec = Game_Report[0][1][1]
                        fir2 = Game_Report[0][0][0]
                        sec2 = Game_Report[0][0][1]
                        if fir == 8:
                            BOARD[fir2][sec2] = sec  # Promotion
                        elif fir == 9:
                            BOARD[fir2+1][sec2] = "-"  # White en-passant
                        elif fir == 10:
                            BOARD[fir2-1][sec2] = "-"  # Black en-passant
                        else:
                            BOARD[fir][sec] = BOARD[fir2][sec2]  # Basic Moves
                            BOARD[fir2][sec2] = "-"
                        Game_Report = Game_Report[1:]
                    Draw_Board(COLORS)
                    Put_pictures()
                if endgame:
                    if 135 < pos[0] < 290 and 295 < pos[1] < 450:
                        # Start a new game
                        restart_game()
                        pygame.draw.rect(win, "black", [0, 0, 750, 750])
                        Draw_Board(COLORS)
                        Put_pictures()
                        Game_Report = []
                    elif 295 < pos[0] < 450 and 295 < pos[1] < 450:
                        # End the program
                        run = False
                        continue
                    elif 455 < pos[0] < 610 and 295 < pos[1] < 450:
                        # Review the game
                        restart_game()
                        pygame.draw.rect(win, "black", [0, 0, 750, 750])
                        Draw_Board(COLORS)
                        Put_pictures()
                        review = True
                elif promotion:
                    # if we promoting a pawn, each if statement is responsible for each piece
                    if 275 < pos[0] < 375 and 275 < pos[1] < 375:
                        if Turn:
                            BOARD[temp_figure[1][0]][temp_figure[1][1]] = "WR"
                            Game_Report.append((temp_figure[1], (8, "WR")))
                        else:
                            BOARD[temp_figure[1][0]][temp_figure[1][1]] = "BR"
                            Game_Report.append((temp_figure[1], (8, "BR")))
                        Turn = not Turn
                    elif 375 < pos[0] < 475 and 275 < pos[1] < 375:
                        if Turn:
                            BOARD[temp_figure[1][0]][temp_figure[1][1]] = "WB"
                            Game_Report.append((temp_figure[1], (8, "WB")))
                        else:
                            BOARD[temp_figure[1][0]][temp_figure[1][1]] = "BB"
                            Game_Report.append((temp_figure[1], (8, "BB")))
                        Turn = not Turn
                    elif 275 < pos[0] < 375 and 375 < pos[1] < 475:
                        if Turn:
                            BOARD[temp_figure[1][0]][temp_figure[1][1]] = "WK"
                            Game_Report.append((temp_figure[1], (8, "WK")))
                        else:
                            BOARD[temp_figure[1][0]][temp_figure[1][1]] = "BK"
                            Game_Report.append((temp_figure[1], (8, "BK")))
                        Turn = not Turn
                    elif 375 < pos[0] < 475 and 375 < pos[1] < 475:
                        if Turn:
                            BOARD[temp_figure[1][0]][temp_figure[1][1]] = "WQ"
                            Game_Report.append((temp_figure[1], (8, "WQ")))
                        else:
                            BOARD[temp_figure[1][0]][temp_figure[1][1]] = "BQ"
                            Game_Report.append((temp_figure[1], (8, "BQ")))
                        Turn = not Turn
                    else:
                        # When you click outside of a given choice
                        if Turn:
                            BOARD[pos_test[0]][pos_test[1]] = "WP"
                            game_counter -= 1
                        else:
                            BOARD[pos_test[0]][pos_test[1]] = "BP"
                        BOARD[temp_figure[1][0]][temp_figure[1][1]] = temp_figure[0]
                        clicked = True
                    pygame.draw.rect(win, "black", [0, 0, 750, 750])
                    Draw_Board(COLORS)
                    promotion = False
                    if check_checker(not Turn, BOARD, True):
                        print("check")
                    if end_game_checker(BOARD, not Turn):
                        run = False
                if clicked:
                    checked = True
                else:
                    for j in range(8):
                        for i in range(8):
                            if (x+i*border < pos[0] < x+(i+1)*border) and \
                                    (y+j*border < pos[1] < y+(j+1)*border) and BOARD[j][i] != "-":
                                if not Turn and BOARD[j][i] in Whites:
                                    continue
                                if Turn and BOARD[j][i] in Blacks:
                                    continue
                                clicked = True
                                draw(i, j, COLORS_CLICKED)
                                MP = show_move(Turn, j, i, BOARD[j][i], BOARD, True, clicked)
                                for (x_field, y_field) in MP:
                                    draw(y_field, x_field, COLORS_POSSIBLE)
                                pos_test = (j, i)
                                break
                    Put_pictures()
                    pygame.display.update()
            if event.type == pygame.MOUSEBUTTONUP and checked:
                clicked = False
                checked = False
                pos2 = pygame.mouse.get_pos()
                for j in range(8):
                    for i in range(8):
                        if(x+i*border < pos2[0] < x+(i+1)*border) and \
                                (y+j*border < pos2[1] < y+(j+1)*border):
                            if (j, i) in MP:
                                white_len = len(White_Pos)
                                black_len = len(Black_Pos)
                                if Turn:
                                    # Modify White_Pos
                                    for e in range(white_len):
                                        if White_Pos[e] == pos_test:
                                            White_Pos[e] = (j, i)
                                        if (j, i) in Black_Pos:
                                            for f in range(black_len):
                                                if Black_Pos[f] == (j, i):
                                                    del Black_Pos[f]
                                                    break
                                else:
                                    # Modify Black_Pos
                                    for e in range(black_len):
                                        if Black_Pos[e] == pos_test:
                                            Black_Pos[e] = (j, i)
                                        if (j, i) in White_Pos:
                                            for f in range(white_len):
                                                if White_Pos[f] == (j, i):
                                                    del White_Pos[f]
                                                    break
                                if BOARD[pos_test[0]][pos_test[1]] == "WS" and white_king_fmove:
                                    # Castling White
                                    white_king_fmove = False
                                    if (j, i) == (7, 2):
                                        for e in range(white_len):
                                            if White_Pos[e] == (7, 0):
                                                White_Pos[e] = (7, 3)
                                                break
                                        BOARD[7][0] = "-"
                                        BOARD[7][3] = "WR"
                                        castle = True
                                    elif (j, i) == (7, 6):
                                        for e in range(white_len):
                                            if White_Pos[e] == (7, 7):
                                                White_Pos[e] = (7, 5)
                                                break
                                        BOARD[7][7] = "-"
                                        BOARD[7][5] = "WR"
                                        castle = True
                                elif BOARD[pos_test[0]][pos_test[1]] == "BS" and black_king_fmove:
                                    # Castling Black
                                    black_king_fmove = False
                                    if (j, i) == (0, 2):
                                        for e in range(black_len):
                                            if Black_Pos[e] == (0, 0):
                                                Black_Pos[e] = (0, 3)
                                                break
                                        BOARD[0][0] = "-"
                                        BOARD[0][3] = "BR"
                                        castle = True
                                    elif (j, i) == (0, 6):
                                        for e in range(black_len):
                                            if Black_Pos[e] == (0, 7):
                                                Black_Pos[e] = (0, 5)
                                                break
                                        BOARD[0][7] = "-"
                                        BOARD[0][5] = "BR"
                                        castle = True
                                if BOARD[pos_test[0]][pos_test[1]] == "WR" and pos_test[1] == 0:
                                    white_lrook_fmove = False
                                elif BOARD[pos_test[0]][pos_test[1]] == "WR" and pos_test[1] == 7:
                                    white_rrook_fmove = False
                                elif BOARD[pos_test[0]][pos_test[1]] == "BR" and pos_test[1] == 0:
                                    black_lrook_fmove = False
                                elif BOARD[pos_test[0]][pos_test[1]] == "BR" and pos_test[1] == 7:
                                    black_rrook_fmove = False
                                elif BOARD[pos_test[0]][pos_test[1]] == "WP" and \
                                        i != pos_test[1] and En_passant_Black[i]:
                                    BOARD[j+1][i] = "-"
                                    White_Passant = True
                                elif BOARD[pos_test[0]][pos_test[1]] == "BP" and \
                                        i != pos_test[1] and En_passant_White[i]:
                                    BOARD[j-1][i] = "-"
                                    Black_Passant = True
                                En_passant_White = 8 * [False]
                                En_passant_Black = 8 * [False]
                                if BOARD[pos_test[0]][pos_test[1]] == "WP" and pos_test[0]-j == 2:
                                    En_passant_White[i] = True
                                if BOARD[pos_test[0]][pos_test[1]] == "BP"and j-pos_test[0] == 2:
                                    En_passant_Black[i] = True
                                if (BOARD[pos_test[0]][pos_test[1]] == "WP" and j == 0) or\
                                        (BOARD[pos_test[0]][pos_test[1]] == "BP" and j == 7):
                                    promotion = True
                                    temp_figure = [BOARD[j][i], (j, i)]
                                BOARD[j][i] = BOARD[pos_test[0]][pos_test[1]]
                                BOARD[pos_test[0]][pos_test[1]] = "-"
                                if check_checker(Turn, BOARD, True):
                                    print("check")
                                if Turn:
                                    game_counter += 1
                                Turn = not Turn
                                if end_game_checker(BOARD, Turn):
                                    endgame = True
                                Game_Report.append((pos_test, (j, i)))
                                if castle:
                                    if (j, i) == (7, 2):
                                        Game_Report.append(((7, 0), (7, 3)))
                                    elif (j, i) == (7, 6):
                                        Game_Report.append(((7, 7), (7, 5)))
                                    elif (j, i) == (0, 2):
                                        Game_Report.append(((0, 0), (0, 3)))
                                    elif (j, i) == (0, 6):
                                        Game_Report.append(((0, 7), (0, 5)))
                                    castle = False
                                if White_Passant:
                                    Game_Report.append(((j, i), (9, 0)))
                                    White_Passant = False
                                if Black_Passant:
                                    Game_Report.append(((j, i), (10, 0)))
                                    Black_Passant = False
                            MP = []
                            Draw_Board(COLORS)
                Put_pictures()
                if promotion:
                    Turn = not Turn
                    pygame.draw.rect(win, "gray", [275, 275, 200, 200])
                    if Turn:
                        win.blit(images2[2], (275, 275))   # WR
                        win.blit(images2[6], (275, 375))   # WK
                        win.blit(images2[8], (375, 275))   # WB
                        win.blit(images2[10], (375, 375))  # WQ
                    else:
                        win.blit(images2[3], (275, 275))   # BR
                        win.blit(images2[7], (275, 375))   # BK
                        win.blit(images2[9], (375, 275))   # BB
                        win.blit(images2[11], (375, 375))  # BQ
                if endgame:
                    pygame.draw.rect(win, "gray", [130, 290, 485, 165])
                    pygame.draw.rect(win, "blue", [135, 295, 155, 155])
                    pygame.draw.rect(win, "green", [295, 295, 155, 155])
                    pygame.draw.rect(win, "yellow", [455, 295, 155, 155])
                    win.blit(font.render('New Game', True, (255, 0, 0)), (165, 355))
                    win.blit(font.render('End Game', True, (255, 0, 0)), (325, 355))
                    win.blit(font.render('Review Game', True, (255, 0, 0)), (470, 355))
                pygame.display.update()

if __name__ == "__main__":
    Play_Game()
