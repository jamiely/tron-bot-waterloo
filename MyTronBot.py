#!/usr/bin/python

"""Template for your tron bot"""

import math
import sys
import tron
import random


class TronBot(object):
    """Plays tron"""
    
    def __init__(self):
        super(TronBot, self).__init__()
        self.marks = {}
        self.retreat = False
        
        self.setFollowMode("right")
    def debug(self,msg):
        return
        if type(msg) == str:
            sys.stderr.write("DEBUG:\t" + msg + "\n")
        else:
            sys.stderr.write("DEBUG:\t" + str   (msg) + "\n")    
    def _dictGetMin(self, d):
        k = d.keys()
        k.sort( key = d.__getitem__)
        return k[0]
    
    def _dictKeysIntersect(self, a, b):
        return filter(a.has_key, b.keys())
    
    def _getOpenSetFScores(self, openset, fScore):
        return dict( (pos, fScore[pos]) for pos in openset )
    
    def astar(self, start, goal):
        closedset = [] # start with empty set
        openset = [start] # start with initial node
        gScore = {start: 0} # distance of note from start?
        hScore = {start: self.heuristicEstimateOfDistance(start, goal)}
        fScore = {start: hScore[start]} # estimated total distance from start to goal
        cameFrom = {}
        while len(openset) > 0:
            # get the fscores in the open set
            openSetF = self._getOpenSetFScores(openset, fScore)
            # self.debug('openset f')
            # self.debug(openSetF)
            node = self._dictGetMin( openSetF )
            # self.debug('node')
            # self.debug(node)
            if node == goal:
                return self.aStarReconstructPath(cameFrom, goal)
            openset.remove(node)
            closedset.append(node)
            possibleDirections = [move for move in self.getPossible ( board, node).values() if board.passable(move)]
            # self.debug('Possible: '+str(possibleDirections))
            for neighbor in possibleDirections:
                if neighbor in closedset:
                    continue # just skip closedset members
                tentativeG = gScore[node] + self.aStarDistance(node, neighbor)
                if not neighbor in openset:
                    openset.append(neighbor)
                    tentativeBetter = True
                elif tentativeG < gScore[neighbor]:
                    tentativeBetter = True
                else:
                    tentativeBetter = False
                if tentativeBetter:
                    cameFrom[neighbor] = node
                    gScore[neighbor] = tentativeG
                    hScore[neighbor] = self.heuristicEstimateOfDistance(neighbor, goal)
                    fScore[neighbor] = gScore[neighbor] + hScore[neighbor]
        return False
    
    
    def heuristicEstimateOfDistance(self, a, b):
        # use regular distance for now
        return self.aStarDistance(a,b)
        
    def aStarDistance(self, a, b):
        """docstring for aStarDinstance"""
        return math.sqrt((b[1]-a[1])**2 + (b[0]-a[0])**2)
        
    def aStarReconstructPath(self, cameFrom, node):
        """docstring for aStarReconstructPath"""
        if cameFrom.has_key(node):
            p = self.aStarReconstructPath(cameFrom, cameFrom[node])
            p.append(node)
            return p
        else:
            return [node]
            
        

    
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
                #self.debug(str(possibleLen)+" possible moves found: " + json.dumps(possible))
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
        
        
        # debug path to enemy
        distanceToEnemy = self.aStarDistance(board.me(), board.them())
        self.debug("distinace to enemy: " + str(distanceToEnemy))
        if not self.retreat and distanceToEnemy > 5:
            path = self.astar(board.me(), board.them())
            if path:
                path.pop(0)
                #self.debug('me: '+str(board.me())+ ' them: '+str(board.them()))
                #self.debug('astar path:\n' + str(path))
                if len(path) > 0:
                    for dir in tron.DIRECTIONS:
                        if board.rel(dir) == path[0]:
                            finalMove = dir
        else:
            self.retreat = True
        
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
    
    def getPossible(self, board, position, directions = tron.DIRECTIONS):
        return dict((dir, board.rel(dir, position)) for dir in tron.DIRECTIONS)
            
    def getMoves(self, board, position, origin = None, directions = tron.DIRECTIONS):            

        possible = self.getPossible(board, position, directions)
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
