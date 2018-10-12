#!/usr/bin/python3
import argparse
import copy
import sys

INF = 100
NEG_INF = -100


class GameBoard(object):

    def __init__(self):
        self.board = []
        for i in range(0, 3):
            self.board.append(['.']*3)

    def print_board(self):
        print('')
        for i in range(0,3):
            for j in range(0,3):
                print(self.board[i][j] if self.board[i][j]!='.' else ' ', '|' if j!=2 else '', sep='', end='')
            print('')
            for k in range(0,5):
                print('-' if i!=2 else '', end='')
            print('')

    def get_states(self, player):
        # states = []
        for i in range(0,3):
            for j in range(0,3):
                if self.board[i][j] == '.':
                    state = GameBoard()
                    state.board = copy.deepcopy(self.board)
                    state.board[i][j] = player
                    yield state
                    # states.append(state)
        # return states

    def is_terminal(self):
        # determine if the current state is terminal state
        # if so, return it's utility value
        # 1 if X wins
        # 0 if a tie
        # -1 if O wins
        # None if it is not a terminal state

        # check all horizontal rows
        for i in range(0,3):
            win_tile = self.board[i][0]
            flag = True
            for j in range(0, 3):
                if self.board[i][j] != win_tile:
                    flag = False
                    break
            if flag and win_tile!='.':
                if win_tile == 'X':
                    return 1
                elif win_tile == 'O':
                    return -1
        
        # check all vertical rows
        for j in range(0,3):
            win_tile = self.board[0][j]
            flag = True
            for i in range(0, 3):
                if self.board[i][j] != win_tile:
                    flag = False
                    break
            if flag and win_tile != '.':
                if win_tile == 'X':
                    return 1
                elif win_tile == 'O':
                    return -1
        
        # check right diagonal
        if self.board[0][0] == self.board[1][1] and self.board[1][1] == self.board[2][2]:
            if self.board[0][0] == 'X':
                return 1
            elif self.board[0][0] == 'O':
                return -1

        # check left diagonal
        if self.board[0][2] == self.board[1][1] and self.board[1][1] == self.board[2][0]:
            if self.board[0][2] == 'X':
                return 1
            elif self.board[0][2] == 'O':
                return -1

        tie = True
        for i in range(0,3):
            for j in range(0,3):
                if self.board[i][j] == '.':
                    tie = False
        if tie:
            return 0
        else:
            return None

def play_min(state, alpha_beta, alpha=NEG_INF, beta=INF):
    p = (state, state.is_terminal())
    if p[1] is not None:
        return p
    else:
        p = (state, INF)
        for next_state in state.get_states(player='O'):
            n_tup = play_max(next_state, alpha_beta, alpha=alpha, beta=beta)
            p = (next_state, n_tup[1]) if n_tup[1] < p[1] else p
            if alpha_beta:
                if p[1] <= alpha:
                    return p
                beta = min(beta, p[1])
    return p

def play_max(state, alpha_beta, alpha=NEG_INF, beta=INF):
    p = (state, state.is_terminal())
    if p[1] is not None:
        return p
    else:
        p = (state, NEG_INF)
        for next_state in state.get_states(player='X'):
            n_tup = play_min(next_state, alpha_beta, alpha=alpha, beta=beta)
            p = (next_state, n_tup[1]) if n_tup[1] > p[1] else p
            if alpha_beta:
                if p[1] >= beta:
                    return p
                alpha = max(alpha, p[1])
    return p

def play_user(state, ch='X'):
    state.print_board()
    row, col = map(lambda x: int(x.strip())-1, input('Enter your move (1 indexed): r, c ').split(','))
    if state.board[row][col] != '.':
        print('Illegal Move')
        sys.exit(0)
    else:
        state.board[row][col] = ch

def main(alpha_beta=False):
    # X is max player (user) and O is min player
    print('Tic Tac Toe', 'Alpha-Beta pruning:',alpha_beta)
    tictactoe = GameBoard()
    counter = 0
    while(tictactoe.is_terminal() is None):
        if counter%2==0:
            play_user(tictactoe)
            # tictactoe = play_max(tictactoe, alpha_beta)[0]
        else:
            tictactoe = play_min(tictactoe, alpha_beta)[0]
        counter +=1
    p = tictactoe.is_terminal()
    tictactoe.print_board()
    if p == 1:
        print('X wins')
    elif p == -1:
        print('O wins')
    else:
        print('Nobody Wins. It\'s a tie.')    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--alphabeta", help='Whether to use alpha beta pruning or not', action='store_true')
    args = parser.parse_args()
    main(alpha_beta=args.alphabeta)