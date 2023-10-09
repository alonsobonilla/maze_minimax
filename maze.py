import copy
import math
import sys
import time
from pynput.keyboard import Key, Listener, KeyCode

walls = []
start = ()
goal = ()
enemy = ()
width = 0
height = 0
base_nodes_explored = []
nodes_explored = []
node_values_enemy = {
    'states_values': list()
}

controller = 0
nodes_initial = []

PLAYER = 0
BOT = 1


def maze_init(filename):
    global start, enemy, goal, width, height

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


def alfa_min(state, alfa, beta):
    global controller, nodes_initial
    nodes_explored.append(state)
    controller += 1

    if end_game(state[0], state[1]):
        return utility(state[0], state[1])
    actions_states = actions(state, BOT)

    if len(actions_states) == 0:
        return 1000

    if controller == 1:
        nodes_initial = copy.copy(actions_states)

    actions_states.sort(key=lambda n: utility(state[0], n[1]))
    v = math.inf
    for action in actions_states:
        state_result = result(state, action, BOT)
        valor_state = alfa_max(state_result, alfa, beta)

        for index in range(len(nodes_initial)):
            if nodes_initial[index][1] == action[1]:
                node_values_enemy['states_values'].append([action, valor_state])

        v = min(v, valor_state)
        if v <= alfa:
            return v
        if v < beta:
            beta = v
    return v


def alfa_max(state, alfa, beta):
    global controller
    nodes_explored.append(state)

    if end_game(state[0], state[1]):
        return utility(state[0], state[1])

    actions_states = actions(state, PLAYER)
    if len(actions_states) == 0:
        return 1000

    actions_states.sort(key=lambda n: utility(n[1], state[1]), reverse=True)
    v = -math.inf
    for action in actions_states:
        state_result = result(state, action, PLAYER)
        valor_state = alfa_min(state_result, alfa, beta)
        v = max(v, valor_state)
        if v >= beta:
            return v
        if v > alfa:
            alfa = v
    return v


def print_maze():
    print()
    for i, row in enumerate(walls):
        print(i, end=" ")
        for j, col in enumerate(row):
            if col:
                print("█", end="")
            elif (i, j) == enemy:
                print("C", end="")
            elif (i, j) == start:
                print("A", end="")
            elif (i, j) == goal:
                print("B", end="")
            else:
                print(" ", end="")
        print()
    print()


def states_explored(turn: int, states=None):
    explored = set()
    if states is not None:
        nodes = states
    else:
        nodes = nodes_explored

    for node in nodes:
        explored.add(node[turn])
    return explored


def actions(state: list, turn: int):
    x1, y1 = state[turn]
    candidates = [
        ("up", (x1 - 1, y1)),
        ("down", (x1 + 1, y1)),
        ("left", (x1, y1 - 1)),
        ("right", (x1, y1 + 1))
    ]
    result_actions = []
    explored = states_explored(turn)
    for action, (r, c) in candidates:
        if 0 <= r < height and 0 <= c < width \
                and not walls[r][c] and (r, c) not in explored:
            result_actions.append((action, (r, c)))
    return result_actions


def result(state: list, action_state: tuple, turn: int):
    new_state = copy.copy(state)
    new_state[turn] = action_state[1]
    return new_state


def utility(player, bot):
    x1, y1 = player  # Player
    x2, y2 = bot  # Enemy
    return abs(x1 - x2) + abs(y1 - y2)


def player(ct_start: tuple, ct_enemy: tuple):
    x1, y1 = ct_start
    x2, y2 = ct_enemy

    d_start = abs(x1 - start[0]) + abs(y1 - start[1])
    d_enemy = abs(x2 - enemy[0]) + abs(y2 - enemy[1])
    if d_start > d_enemy:
        return 1
    return 0


def end_game(player: tuple, enemy: tuple):
    x1, y1 = player
    x2, y2 = enemy
    x3, y3 = goal
    return abs(x1 - x2) + abs(y1 - y2) == 0 \
        or abs(x1 - x3) + abs(y1 - y3) == 0 \
        or abs(x2 - x3) + abs(y2 - y3) == 0


def validate_input(state: tuple, turn):
    r, c = state
    if 0 <= r < height and 0 <= c < width and not walls[r][c] and (r, c) not in states_explored(turn,
                                                                                                base_nodes_explored):
        return True
    return False


def on_release(key):
    global possible_start
    if key == Key.up:
        r = start[0] - 1
        possible_start = (r, start[1])
        return False
    if key == Key.down:
        r = start[0] + 1
        possible_start = (r, start[1])
        return False
    if key == Key.left:
        c = start[1] - 1
        possible_start = (start[0], c)
        return False
    if key == Key.right:
        c = start[1] + 1
        possible_start = (start[0], c)
        return False


def end_game_message(player):
    x1, y1 = player
    x2, y2 = enemy
    x3, y3 = goal
    if abs(x1 - x3) + abs(y1 - y3) == 0:
        print("Llegaste al objetivo!")
    elif abs(x1 - x2) + abs(y1 - y2) == 0:
        print("Te atraparon")
    else:
        print("No llegaste al objetivo")


if __name__ == '__main__':

    if len(sys.argv) != 2:
        sys.exit("Usage: python maze.py maze.txt")
    maze_init(sys.argv[1])
    print_maze()
    state_initial = [start, enemy]
    base_nodes_explored.append(state_initial)

    turn = True

    while True:
        controller = 0
        if end_game(start, enemy):
            end_game_message(start)
            break
        if turn:
            print("Turno: Usuario")
            possible_start = ()

            with Listener(on_release=on_release) as listener:
                listener.join()
            if not validate_input(possible_start, PLAYER):
                print("Coordenada no válida. Realiza nuevamente tu acción")
                continue
            start = possible_start

            print("Nuevo estado: ", [start, enemy])
            print_maze()
            turn = False

        else:
            print("Turno: Bot")
            turn = True

            nodes_explored = copy.copy(base_nodes_explored)
            state = [start, enemy]
            val = alfa_min(state, -math.inf, math.inf)

            for state in node_values_enemy['states_values']:
                if state[1] == val:
                    enemy = state[0][1]
                    break
            node_values_enemy['states_values'].clear()
            base_nodes_explored.append((start, enemy))

            print("Enemigo pensando...")

            time.sleep(2)

            print("Nuevo estado: ", [start, enemy])
            print_maze()
