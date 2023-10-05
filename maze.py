import copy
import math
import sys

solution = []
walls = []
start = set()
goal = set()
enemy = set()
width = 0
height = 0


## turn 0 --> Player
## turn 1 --> Enemy
class Node:
    def __init__(self, state, parent=None, action=None, val=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.val = val

def maze_init(filename):
    global start, enemy, goal, walls, width, height

    with open(filename) as f:
        contents = f.read()

    if contents.count("A") != 1:
        raise Exception("maze must have exactly one start point")
    if contents.count("C") != 1:
        raise Exception("maze must have exactly one enemy")
    if contents.count("B") != 1:
        raise Exception("maze must have exactly one goal")

    contents = contents.splitlines()
    height = len(contents)
    width = max(len(line) for line in contents)

    for i in range(height):
        row = []
        for j in range(width):
            try:
                if contents[i][j] == "A":
                    start = (i, j)
                    row.append(False)
                if contents[i][j] == "C":
                    enemy = (i, j)
                    row.append(False)
                elif contents[i][j] == "B":
                    goal = (i, j)
                    row.append(False)
                elif contents[i][j] == " ":
                    row.append(False)
                else:
                    row.append(True)
            except IndexError:
                row.append(False)
        walls.append(row)


def minimax(state_player, state_enemy):
    node_initial = Node([state_player, state_enemy])
    turn_player = player(node_initial)

    if turn_player == 1:
        action_states = actions(node_initial, turn_player)

        for action_state in action_states:
            max_value(result(node_initial, action_state, turn_player))

    else:
        actions_states = actions(node_initial, turn_player)
        for action_state in actions_states:
            min_value(result(node_initial, action_state, turn_player))


def max_value(state: Node):
    if terminal(state):
        return utility(state)
    v = -math.inf
    turn = player(state)
    for action, (r, c) in actions(state, turn):
        new_state = copy.copy(state.state)
        new_state[turn] = (r, c)
        node = Node(new_state, state, action)
        v = max(v, min_value(node))
        node.val = v
    return v


def min_value(state: Node):
    if terminal(state):
        return utility(state)
    v = math.inf
    turn = player(state)

    for action, (r, c) in actions(state, turn):
        new_state = copy.copy(state.state)
        new_state[turn] = (r, c)
        node = Node(new_state, state, action)
        v = min(v, max_value(node))
        node.val = v
    return v


def print_maze():
    global solution

    solution_start = solution[0][1] if len(solution) != 0 else None
    solution_enemy = solution[1][1] if len(solution) != 0 else None
    print()
    for i, row in enumerate(walls):
        for j, col in enumerate(row):
            if col:
                print("█", end="")
            elif (i, j) == start:
                print("A", end="")
            elif (i, j) == goal:
                print("B", end="")
            elif (i, j) == enemy:
                print("C", end="")
            elif solution_start is not None and (i, j) in solution_start:
                print("*", end="")
            elif solution_enemy is not None and (i, j) in solution_enemy:
                print("-", end="")
            else:
                print(" ", end="")
        print()
    print()


def states_explored(state: Node, turn: int):
    explored = []
    node = state
    while node.parent is not None:
        explored.append(node.parent.state[turn])
        node = node.parent
    return explored


def actions(state: Node, turn: int):
    x1, y1 = state.state[turn]
    candidates = [
        ("up", (x1 - 1, y1)),
        ("down", (x1 + 1, y1)),
        ("left", (x1, y1 - 1)),
        ("right", (x1, y1 + 1))
    ]
    result_actions = []
    explored = states_explored(state, turn)
    for action, (r, c) in candidates:
        if 0 <= r < height and 0 <= c < width and not walls[r][c] and (r, c) not in explored:
            result_actions.append((action, (r, c)))
    return result_actions


def result(state: Node, action_state: tuple, turn: int):
    new_state = copy.copy(state.state)
    new_state[turn] = action_state[1]
    node = Node(new_state, state, action_state[0])
    return node


def terminal(state: Node):
    x1, y1 = state.state[0]  # Player
    x2, y2 = state.state[1]  # Enemy
    x3, y3 = goal  # Goal
    if abs(x1 - x2) + abs(y1 - y2) == 0 or abs(x1 - x3) + abs(y1 - y3) == 0:
        return True
    return False


def utility(state: Node):
    x1, y1 = state.state[0]  # Player
    x2, y2 = state.state[1]  # Enemy
    return abs(x1 - x2) + abs(y1 - y2)


def player(state: Node):
    if state.state[0] == state.parent.state[0] if state.parent is not None else 0:
        return 0
    return 1


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("Usage: python maze.py maze.txt")
    maze_init(sys.argv[1])
    print_maze()
    minimax(start, enemy)