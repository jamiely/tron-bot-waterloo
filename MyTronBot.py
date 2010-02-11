#!/usr/bin/python

"""Template for your tron bot"""

import sys
import tron
import random
import json


class TronBot(object):
    """Plays tron"""
    
    def __init__(self):
        super(TronBot, self).__init__()
        self.marks = {}
        
        self.setFollowMode("right")
    
    def debug(self,msg):
        sys.stderr.write("DEBUG:\t" + msg + "\n")
    
    def setFollowMode(self, mode):
        self.followMode = mode
        self.debug("Setting direction mode to " + mode)
        if mode == "right":
            self.directions = [tron.EAST, tron.NORTH, tron.WEST, tron.SOUTH]
        else:
            self.directions = [tron.WEST, tron.NORTH, tron.SOUTH, tron.EAST]
    
    def getMove(self, board):
        """Returns a move applicable to passed board"""
        moves = board.moves()
        movesLen = len(moves)
        finalMove = None
        if movesLen == 0:
            pass
        elif movesLen == 1:
            finalMove = moves[0]
        else:
            self.debug("More than 1 move, attempting to find move using lookahead.")
            possible = [self.getMoveLookahead(board, board.me(), dir) for dir in moves]
            possible = [x for x in possible if x != None]
            possibleLen = len(possible)
            if possibleLen > 0:
                self.debug(str(possibleLen)+" possible moves found: " + json.dumps(possible))
                for dir in self.directions:
                    for pos in possible:
                        if board.rel(dir) == pos:
                            finalMove = dir
                            break
            else:
                self.debug("No moves found via lookahead.")
            
            
            if finalMove == None:
                self.debug("Could not find move. Using follow mode rule.")
                finalMove = self.getMovesUsingRules(board, board.me())[0]

        if finalMove == None:
            finalMove = [tron.NORTH]            
        self.decideMove (board, board.rel(finalMove), finalMove)            
        
        
        return finalMove
    
        
    def getMoveLookahead(self, board, origin, dir):
        """getMoveLookahead looks at the available moves
        and determines what to do"""
        self.debug("Lookahead.")
        
        target = board.rel(dir, origin) # get the position we are going to check
        targetMoves = self.getMoves(board, target, origin) # retrieves allowable moves excluding origin
        targetMovesLen = len(targetMoves)
        
        shouldTakeMove = False
        
        moveToMake = None
        result = False
        if targetMovesLen == 2: 
            #special processing
            result = self.processMoves2(board, target, dir)
        elif targetMovesLen == 3:
            #special processing
            result = self.processMoves3(board, target, dir)
        if result:
            moveToMake = target
        return moveToMake
        
    def decideMove (self, board, position, dir):
        # this is the move we are taking
        positionMoves = self.getMoves(board, board.me(), position)
        positionMovesCount = len(positionMoves)
        if positionMovesCount == 2: 
            if self.marks.has_key(position) and dir == self.marks[position]:
                # good, color and remove mark
                self.marks.pop(position)
            else: # this is not so good
                self.setFollowMode ("left") # follow left hand rule
        elif positionMovesCount > 2:
            # really, we need to enter a "special mode" where we search
            # for a simple path. one that has two boundary pixels
            self.setFollowMode ("right") # follow right hand rule
        
    def processMoves2(self, board, position, dir):
        #processes case #3
        shouldFill = False
        self.debug("ProcessMoves2")
        if self.marks.has_key(position):
            if dir == self.marks[position]:
                # should take this position
                shouldFill = True
            else:
                # the direction is not the same. we must enter a wicked loop
                # enter left hand mode.
                pass
        else:
            self.marks[position] = dir
        return shouldFill
        
    def processMoves3(self, board, position, dir):
        #processes case #4
        # determine which direction is blocked
        # assume that we are coming from dir, so that behind us is the blocked location
        self.debug("processMoves3")
        newPos = board.rel(dir) #keep on going in the same direction to check
        
        if dir in [1,3]: # North or South
            # check east and west
            dirs = [tron.WEST, tron.EAST]
        else: # East or west
            # check north and south
            dirs = [tron.NORTH, tron.SOUTH]

        # these are positions we should check for availability
        check = [board.rel(dir, newPos) for dir in dirs]

        # we should only fill the position if both of the positions are available.
        shouldFill = len([pos for pos in check if board[pos]!=tron.FLOOR]) < 1
        return shouldFill

    def getMovesUsingRules(self, board, position, origin = None):
        return self.getMoves(board, position, origin, self.directions)
    
    def getMoves(self, board, position, origin, directions = tron.DIRECTIONS):
        possible = dict((dir, board.rel(dir, position)) for dir in tron.DIRECTIONS)
        passable = [dir for dir in possible if board.passable(possible[dir]) and possible[dir] != origin ]
        if not passable:
            # it seems we have already lost
            return []
        return passable        
        
tronBot = TronBot()
def which_move(board):
    return tronBot.getMove(board)

# you do not need to modify this part
for board in tron.Board.generate():
    tron.move(which_move(board))
