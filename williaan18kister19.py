import random
import sys

sys.path.append("..")  # so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *


##
# AIPlayer
# Description: The responsbility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# will be implemented by students in Dr. Nuxoll's AI course.
#
# Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):
    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "AI_NOT_FOUND")

        self.enemyFood = []
        self.ourFood = []

        self.weHaveNotDoneThisBefore = True


        self.SEARCH_DEPTH = 2
    
    ##
    # getPlacement
    #
    # Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    # Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    # Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:  # stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    ##
    # getMove
    # Description: Gets the next move from the Player.
    #
    # Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: The Move to be made
    ##
    def getMove(self, currentState):
        # get food lists
        if self.weHaveNotDoneThisBefore:
            foods = getConstrList(currentState, None, (FOOD,))
            for food in foods:
                if food.coords[1] > 3:
                    self.enemyFood.append(food)
                else:
                    self.ourFood.append(food)
            self.weHaveNotDoneThisBefore = False

        retMove = self.moveSearch(currentState, 0, None)
        return retMove[-2]['move']

    ##
    # getAttack
    # Description: Gets the attack to be made from the Player
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        # Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    # getUtility
    # Description: Creates a utility value in the range 0-1 with the given state
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    ##
    def getUtility(self, currentState):
        # If our agent has won, return a utility of 1.0
        if self.hasWon(currentState, self.playerId):
            return 1.0
        # If our agent has lost, return a utility of 0
        elif self.hasWon(currentState, (self.playerId + 1) % 2):
            return 0.0
        # Getting our inventory and our enemy's inventory
        for inv in currentState.inventories:
            if inv.player == currentState.whoseTurn:
                ourInv = inv
            else:
                enemyInv = inv

        utility = 0
        # The code below creates a utility value based on the amount of food our agent has in their inventory
        # Range of 0 to 60
        utility += float(ourInv.foodCount) * float(5)

        # If our agent has less than three ants this is a bad utility, if our agent has 3 to 5 ants this is a good
        # utility, and if our agent over 5 ants this is a medium utility        numAnts = len(ourInv.ants)
        # Range 0 to 40
        numAnts = len(ourInv.ants)
        if numAnts == 2:
            utility += 5
        if numAnts == 3:
            utility += 20
        if numAnts == 4:
            utility += 40
        if numAnts > 4:
            utility += 10
        

        # The code below creates a utility value based on the number of ants the enemy has
        # If the enemy has more than 4 ants this is a bad utility and if the enemy has less it is a good utility
        # Range 0 to 40
        enemyNumAnts = len(enemyInv.ants)
        if enemyNumAnts == 1:
            utility += 40
        if enemyNumAnts == 2:
            utility += 30
        if enemyNumAnts == 3:
            utility += 20
        if enemyNumAnts == 4:
            utility += 10


        for worker in getAntList(currentState, self.playerId, (WORKER,)):
            if worker.carrying:
                utility += 4

        # Utility Range from 0 to 140
        utility = float(utility)/166.0 + 0.03

        return utility

    # #
    # initNode
    # Description: Create a new Node and return it
    #
    # Parameters:
    #   move - the move to create the next node
    #   currentState - a clone of the current state
    ##
    def initNode(self, move, currentState):
        node = {'move': move, 'nextState': getNextState(currentState, move), 
                'utility': self.getUtility(getNextState(currentState, move))}

        return node


    # #
    # evalNode
    # Description: Takes a dictionary of node and returns the average utility
    #
    # Parameters:
    #   nodes - a dictionary list of nodes to be evaluated
    ##
    def evalNode(self, nodes):
    	util = 0
    	for node in nodes:
    		util += node['utility']

    	return float(util) / float(len(nodes))


    ##
    # moveSearch
    # Description: Takes the game state, depth, and a node and expands the node
    # using the current state. It then picks the node with the best utility and then
    # repeats this process until the desired depth has been reached.
    #
    # Parameters:
    #   state - the current game state
    #   depth - the depth we are currently at
    #   currNode - the node we are expanding
    ##
    def moveSearch(self, state, depth, currNode):
        if depth >= self.SEARCH_DEPTH:
            return [currNode]

        # get list of neighboring nodes
        nodes = []
        for move in listAllLegalMoves(state):
            nodes.append(self.initNode(move, state))

        pathUtil = -1
        for node in nodes:
        	pathToNode = self.moveSearch(node['nextState'], depth+1, node)
        	currUtil = self.evalNode(pathToNode)
        	if currUtil > pathUtil:
        		pathUtil = currUtil
        		favoriteMove = pathToNode

        favoriteMove.append(currNode)
        return favoriteMove


    # Register a win
    def hasWon(self, currentState, playerId):
        opponentId = (playerId + 1) % 2

        if ((currentState.phase == PLAY_PHASE) and
                ((currentState.inventories[opponentId].getQueen() == None) or
                     (currentState.inventories[opponentId].getAnthill().captureHealth <= 0) or
                     (currentState.inventories[playerId].foodCount >= FOOD_GOAL) or
                     (currentState.inventories[opponentId].foodCount == 0 and
                              len(currentState.inventories[opponentId].ants) == 1))):
            return True
        else:
            return False



#### UNIT TESTS ####

board = [[Location((col, row)) for row in xrange(0,BOARD_LENGTH)] for col in xrange(0,BOARD_LENGTH)]
p1Inventory = Inventory(PLAYER_ONE, [], [], 0)
p2Inventory = Inventory(PLAYER_TWO, [], [], 0)
neutralInventory = Inventory(NEUTRAL, [], [], 0)
state = GameState(board, [p1Inventory, p2Inventory, neutralInventory], PLAY_PHASE, PLAYER_ONE)

player = AIPlayer(PLAYER_ONE)
x = player.getUtility(state)

if not (x <=1 and x >= 0):
    print "The method getUtility() has returned an out of bounds value."


for move in listAllLegalMoves(state):
    node = player.initNode(move, state)
    if node['move'] is not Move:
        print "Move not found in Node structure"
    if node['nextState'] is not GameState:
        print "State not found in Node structure"
    if node['utility'] is not float:
        print "Utility not found in Node structure"