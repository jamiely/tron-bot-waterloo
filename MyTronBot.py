#!/usr/bin/python

"""Template for your tron bot"""

import sys
import tron
import random


flood_fill_marks = {}
# right hand rule for flood filling
flood_fill_order = [tron.EAST, tron.NORTH, tron.WEST, tron.SOUTH]

def debug(msg):
    sys.stderr.write(msg)

def flood_fill_right_hand_rule(board, moves):
    move = None
    moveTwoDir = None
    for dir in flood_fill_order:
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
    elif movesLen == 2:
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
        
        
def which_move(board):
    moves = board.moves()
    movesLen = len(moves)
    move = flood_fill(board)
    return move

# you do not need to modify this part
for board in tron.Board.generate():
    tron.move(which_move(board))
