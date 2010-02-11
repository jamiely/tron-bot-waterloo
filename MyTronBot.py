#!/usr/bin/python

"""Template for your tron bot"""

import sys
import tron
import random
import json


flood_fill_marks = {}
# right hand rule for flood filling
flood_fill_order_right = [tron.EAST, tron.NORTH, tron.WEST, tron.SOUTH]
# copy and reverse for left hand rule
flood_fill_order_left = flood_fill_order_right[:].reverse() 

def debug(msg):
    sys.stderr.write("DEBUG:\t" + msg + "\n")

def flood_fill_right_hand_rule(board, moves):
    move = None
    moveTwoDir = None
    for dir in flood_fill_order_right:
        des = board.rel(dir)
        if des == moves[0]:
            move = moves[0]
        if des == moves[1]:
            moveTwoDir = dir            
    if len(moves) == 2 and not move is None:
        # mark the position with the direction we were looking
        flood_fill_marks[moves[1]] = moveTwoDir   
    return move 

def flood_fill(board, moves = None):
    if moves is None:
        moves = board.moves()
    movesLen = len(moves)
    move = None
    debug("moves: " + str(movesLen) + '\n')
    if movesLen == 0:
        debug('Screwed!')
    elif movesLen == 1:
        move = moves[0]
    elif movesLen == 2: # this means that we are in case 3
        # check each new position
        
        
        
    
        move = flood_fill_right_hand_rule (board, moves)
    else:
        move = flood_fill_right_hand_rule (board, moves)
        adjacent = board.adjacent(move)
        count = len ([a for a in adjacent if board[a] == tron.FLOOR])
        debug("other count: " + str(count) + "\n")
        if count < 3 and len(moves) > 1:
            moves.remove(move)
            move = flood_fill_right_hand_rule (board, moves)
    if move in flood_fill_marks and len(moves) > 1:
        moves.remove(move)
        move = flood_fill (board, moves)     
        
        # be careful about blocking
    if move is None: move = random.choice(moves)
    return move


    
class TronBot(object):
    """This is Jamie's TronBot"""
    def __init__(self):
        super(TronBot, self).__init__()
        self.marks = {}
        
    def setBoard(self, board):
        """Sets the board that are going to evalaute"""
        self.board = board
    
    def getMove(self, board):
        self.setBoard(board)
        self.floodFill()
        return random.choice(board.moves())
    
    def floodFill(self):
        """This is version two of the floodfill algorithm"""

        moves = self.board.moves() # moves is a list of board positions
        movesCount = len(moves) # the number of possible moves
        me = self.board.me()

        if movesCount <= 1:
            return moves[0] if movesCount > 0 else None
        else:
            # for all other considerations, must evaluate each position
            for move in moves:
                self.flood_fill2_evalpos(me, move)
    
    def mark(self, pos, dir):
        self.marks[pos] = dir
    
    def isMarked(self, pos):
        return self.marks.has_key(pos)
    
    def getMarkDirection(self, pos):
        return self.marks[pos]
    
    def flood_fill2_evalpos(self, origin, move):
        # evaluate the board position "move" with respect to the origin
        futureMoves = self.futureMoves(origin)
        debug("Future Moves: " + json.dumps(futureMoves))
        
        moves = [] # moves = {pos: score, pos: score}
        
        for dir, pos in futureMoves.items():
            debug("\tFrom " + json.dumps(pos))
            mFutureSecondary = self.futureMoves(pos)
            # this is the number of moves available from that position
            secondaryMoveCount = len ( mFutureSecondary )
            if secondaryMoveCount == 2:
                if self.isMarked ( pos ):
                    # if it's already marked, and we're going in the same
                    # direction, we should take the move
                    if self.getMarkDirection( pos ) == dir:
                        # TAKE MOVE!
                        moves.append((pos, 1000))
                    else:
                        moves.append((pos, -1000))
                        moves.append(())
                else:
                    #mark that position!
                    self.mark(pos, dir)
                    moves.append((pos, -1000)) # do not take the move yet

                
            
            
            for fm, pos2 in mFutureSecondary.items():
                debug("\t\t" + json.dumps(pos2))
                
        
        
        
        debug("Future Moves: " + json.dumps(futureMoves))
        
    def futureMoves(self, origin):
        possible = dict((dir, board.rel(dir, origin)) for dir in tron.DIRECTIONS)
        #passable = [dir for dir in possible if board.passable(possible[dir])]
        passable = dict((dir, possible[dir]) for dir in possible if board.passable(possible[dir]) and possible[dir] != origin )
        return passable


# getting too complicated!!







        
tronBot = TronBot()
def which_move(board):
    tronBot.setBoard(board)
    return tronBot.getMove(board)

# you do not need to modify this part
for board in tron.Board.generate():
    tron.move(which_move(board))
