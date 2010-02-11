#!/usr/bin/python

"""Template for your tron bot"""
import copy, math, random
import sys
import tron

def debug(msg):
    if type(msg) == str:
        sys.stderr.write("DEBUG:\t" + msg + "\n")
    else:
        sys.stderr.write("DEBUG:\t" + str   (msg) + "\n")    


class TronBot(object):
    """Plays tron"""
    
    def __init__(self):
        super(TronBot, self).__init__()
        self.marks = {}
        self.retreat = False
        
        self.setFollowMode("right")
    def debug(self,msg):
        debug(msg)

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
        

class Minimax(object):
    """docstring for TronMiniMax"""
    def __init__(self):
        super(Minimax, self).__init__()
    def minimaxDecision(self, state):
        """state is the current state of the game"""
        v = self.maxValue(state)
        return [action for action, successorState in self.successors(state) if self.utility(action) == v]
        
    def infinity(self):
        return sys.maxint
    def negativeInfinity(self):
        return -sys.maxint - 1
        
    def maxValue(self, state):
        """docstring for maxValue"""
        if self.isTerminal(state): return self.utility(state)
        v = self.negativeInfinity()
        for successorAction,successorState in self.successors(state):
            v = max(v, self.minValue(successorState)) 
        return v
    def minValue(self, state):
        if self.isTerminal(state): return self.utility(state)
        v = self.infinity()
        for successorAction, successorState in self.successors(state):
            v = min(v, self.maxValue(successorState))
        return v
    def isTerminal(self, state):
        """docstring for isTerminal"""
        return true
    def successors(self, state):
        return {}
    def utility(self, state):
        pass


class AlphaBeta(object):
    """docstring for TronMiniMax"""
    def __init__(self):
        super(Minimax, self).__init__()
        self._maxDepth = 1
        
    def search(self, state):
        """state is the current state of the game"""

        v = self.maxValue(state, self.negativeInfinity(), self.infinity())
        return [action for action, successorState in self.successors(state) if self.utility(action) == v]

    def infinity(self):
        return sys.maxint
    def negativeInfinity(self):
        return -sys.maxint - 1

    def maxValue(self, state, alpha, beta, depth = 1):
        """docstring for maxValue
            alpha = the value of the best alternative for MAX along the path to state
            beta = the value of the best alternative for MIN along the path to state
        """
        if self.isTerminal(state, depth): return self.utility(state)
        
        v = self.negativeInfinity()
        for successorAction,successorState in self.successors(state):
            v = max(v, self.minValue(successorState, alpha, beta, depth + 1)) 
            if v >= beta: return v
            alpha = max(alpha, v)
        return v
         
    def minValue(self, state, alpha, beta, depth = 1):
        if self.isTerminal(state, depth): return self.utility(state)
        v = self.infinity()
        for successorAction, successorState in self.successors(state):
            v = min(v, self.maxValue(successorState,alpha, beta, depth + 1))
            if v <= alpha: return v
            beta = min(beta, v)
            
        return v
    def isTerminal(self, state, depth):
        """docstring for isTerminal"""
        return depth < self._maxDepth
        
    def successors(self, state):
        return {}
    def utility(self, state):
        return 0
        
        
class TronAlphaBeta(AlphaBeta):
    """docstring for TronAlphaBeta"""
    def __init__(self):
        super(TronAlphaBeta, self).__init__()
    def utility(self, board):
        """docstring for utility"""
        pass
    def isTerminal(self, board, depth):
        """docstring for isTerminal"""
        pass
    def successors(self, board):
        """docstring for successors"""
        pass




class JamieBoard(object):
    """docstring for JamieBoard"""
    def __init__(self, board):
        super(JamieBoard, self).__init__()
        self.board = board
        self.loser = ''
        self.draw = False
        
    def bisect(self):
        """
        This function will calculate the perpendicular bisector
        of me and them. 
        """
        # step 1, figure out the slope
        me = self.board.me()
        them = self.board.them()
        slope = self.getSlope(me, them)
        midpt = self.getMidpoint(me, them)
        if slope is 0:
            # handle drawing vertical line
            y, throwaway = midpt
            y = int(round(y))
            for x in xrange(self.board.width):
                if self.check(y,x):
                    self.set((y,x), '@')
                    debug("biset in range"+str((y,x)))
                else:
                    debug("biset out of range"+str((y,x)))
        else:
            nr = 0 if slope is None else self.negativeReciprocal(slope) 
            
            y,x = midpt
            b = y - nr * x
        
            debug("bisect y = "+str(nr)+"x + "+str(b))
        
            # draw bisection
            for x in xrange(self.board.width):
                y = nr * x + b
                y = int(round(y))
                if self.check(y,x):
                    self.set((y,x), '@')
                    debug("biset in range"+str((y,x)))                    
                else:
                    debug("biset out of range"+str((y,x)))
        
        debug("bisected:\n"+str(self))
        # eqtn of line, y = mx + b,
        # b = y - mx
    def check(self, y, x):
        return 0 <= x < self.board.width and 0 <= y < self.board.height 
    def getMidpoint(self, a, b):
        return (b[0]+a[0])/2, (b[1]+a[1])/2
        
    def getSlope(self, a, b):
        run = a[1] - b[1]
        
        return (a[0]-b[0])/run if run != 0 else None
    
    def negativeReciprocal(self, val):
        """docstring for negativeReciprocal"""
        return -1/val
        
    def successors(self):
        """
        Use this function to return all possible permutations
        for all the moves that me or them could make. Each retured
        object is an instance of JamieBoard
        """
        suc = []
        b = self.board
        for meMove in self.moves(b.me()):
            for themMove in self.moves(b.them()):
                jb = copy.deepcopy ( self )
                b = jb.board
                if b.rel(meMove, b.me()) == b.rel(themMove, b.them()): # draw
                    jb.draw = True
                else:
                    themLost = not jb.move(b.them(), themMove)
                    meLost = not jb.move(b.me(), meMove)
                    if themLost and meLost:
                        jb.draw = True
                    elif themLost: 
                        jb.loser = b.them()
                    elif meLost: 
                        jb.loser = b.me()

                        # otherwise, no one lost!
                suc.append(jb)
        return suc
                
    def moves(self, origin):
        """Calculate which moves are safe to make this turn.

        Any move in the returned list is a valid move. There
        are two ways moving to one of these tiles could end
        the game:

            1. At the beginning of the following turn,
               there are no valid moves off this tile.
            2. The other player also moves onto this tile,
               and you collide.
        """
        b = self.board
        possible = dict((dir, b.rel(dir, origin)) for dir in tron.DIRECTIONS)
        passable = [dir for dir in possible if b.passable(possible[dir])]
        if not passable:
            # it seems we have already lost
            return []
        return passable      
    
 
               
    def set(self, coords, mark):
        y, x = coords      
        self.board.board[y] = self.board.board[y][:x] + mark + self.board.board[y][x+1:]
    
    def move(self, coordsFrom, dir):
        """Moves whoever is at coordsFrom in the direction specified"""
        b = self.board
        mark = b[coordsFrom] #mark should contain me or them (1 or 2)
        debug("coordsFrom = "+str(coordsFrom)+ " mark="+mark + " me="+ str(b.me()) + " them=" + str(b.them()))
        self.set (coordsFrom, tron.WALL)
        
        newCoords = b.rel(dir, coordsFrom)
        passable = b.passable(newCoords)
        if passable:
            debug("Setting "+str(newCoords)+" to "+mark)
            self.set (newCoords, mark)
        else:
            self.loser = mark
        return passable


    def isGameOver(self):
        """Sees if loser is specified."""
        return self.getLoser() != "" or self.draw
        
    def getLoser(self):
        return self.loser
    def __str__(self):
        return 'loser: ' + self.loser + ' draw? ' + str(self.draw) + '\n' + '\n'.join(self.board.board)
    def simpleFill(self,board,node,target = tron.FLOOR, replaceMark=tron.WALL):
        q = []
        if board[node] != target: return
        q.append(node)
        for n in q:
            e = eNext = w = wNext = n
            while board[wNext] != target :
                w = wNext
                wNext = board.rel(tron.WEST, wNext)
            while board[eNext] != target 
                e = eNext
                eNext = board.rel(tron.EAST, wNext)
            for pt in self.between(w,e):
                north = board.rel(tron.NORTH, pt)
                south = board.rel(tron.SOUTH, pt)                
                if board[north] == target:
                    q.append(north)
                elif board[south] == target:
                    q.append(south)
        return

    def between(self, a, b):
        """is inclusive of a and b"""
        # vertical or horiz?
        a_y, a_x = a
        b_y, b_x = b

        if a_y == b_y: #horiz
            bt = [(a_y, x) for x in xrange(min(a_x,b_x), max(a_x,b_x)+1)]
        else: #vert
            bt = [(y, a_x) for y in xrange(min(a_y,b_y), max(a_y,b_y)+1)]
        return bt
   

tronBot = TronBot()
def which_move(board):
    jb = JamieBoard (board)
    jb.bisect()
    s = jb.successors()
    debug ('successors\n%s\n' % str(len(s)))
    if len(s) < 6:
        for a in s: debug( '\t*** successor ***\n' + str(a)+'\n')
    return tronBot.getMove(board)

# you do not need to modify this part
for board in tron.Board.generate():
    tron.move(which_move(board))