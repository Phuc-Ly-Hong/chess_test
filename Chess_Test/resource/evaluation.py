# evaluation.py

PIECE_VALUES = {
    'P': 100, 'N': 300, 'B': 320, 'R': 500, 'Q': 900, 'K': 20000
}

PASSED_PAWN_BONUSES = [0, 120, 80, 50, 30, 15, 15]
ISOLATED_PAWN_PENALTY_BY_COUNT = [0, -10, -25, -50, -75, -75, -75, -75, -75]
KING_PAWN_SHIELD_SCORES = [4, 7, 4, 3, 6, 3]

POSITION_TABLES = {
    'P': [  # Pawn
         0,   0,   0,   0,   0,   0,   0,   0,
        50,  50,  50,  50,  50,  50,  50,  50,
        10,  10,  20,  30,  30,  20,  10,  10,
         5,   5,  10,  25,  25,  10,   5,   5,
         0,   0,   0,  20,  20,   0,   0,   0,
         5,  -5, -10,   0,   0, -10,  -5,   5,
         5,  10,  10, -20, -20,  10,  10,   5,
         0,   0,   0,   0,   0,   0,   0,   0
    ],
    'P_end': [  # Pawn endgame
         0,   0,   0,   0,   0,   0,   0,   0,
        80,  80,  80,  80,  80,  80,  80,  80,
        50,  50,  50,  50,  50,  50,  50,  50,
        30,  30,  30,  30,  30,  30,  30,  30,
        20,  20,  20,  20,  20,  20,  20,  20,
        10,  10,  10,  10,  10,  10,  10,  10,
        10,  10,  10,  10,  10,  10,  10,  10,
         0,   0,   0,   0,   0,   0,   0,   0
    ],
    'R': [  # Rook
         0,   0,   0,   0,   0,   0,   0,   0,
         5,  10,  10,  10,  10,  10,  10,   5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
         0,   0,   0,   5,   5,   0,   0,   0
    ],
    'N': [  # Knight
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ],
    'B': [  # Bishop
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    ],
    'Q': [  # Queen
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
         -5,  0,  5,  5,  5,  5,  0, -5,
          0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ],
    'K_middle': [  # King middle game
        -80, -70, -70, -70, -70, -70, -70, -80,
        -60, -60, -60, -60, -60, -60, -60, -60,
        -40, -50, -50, -60, -60, -50, -50, -40,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
         20,  20,  -5,  -5,  -5,  -5,  20,  20,
         20,  30,  10,   0,   0,  10,  30,  20
    ],
    'K_end': [  # King end game
        -20, -10, -10, -10, -10, -10, -10, -20,
         -5,   0,   5,   5,   5,   5,   0,  -5,
        -10,  -5,  20,  30,  30,  20,  -5, -10,
        -15, -10,  35,  45,  45,  35, -10, -15,
        -20, -15,  30,  40,  40,  30, -15, -20,
        -25, -20,  20,  25,  25,  20, -20, -25,
        -30, -25,   0,   0,   0,   0, -25, -30,
        -50, -30, -30, -30, -30, -30, -30, -50
    ]
}

class Evaluation:
    def __init__(self, move_validator):
        self.validator = move_validator

    def evaluate(self, board, color):
        material = self.material_score(board, color)
        game_phase = 0 if material > 3000 else 1
        score = material
        score += self.position_score(board, color, game_phase)
        score += self.mobility_score(board, color) * 0.1
        score += self.pawn_structure_score(board, color) * 0.05
        score += self.king_safety_score(board, color, game_phase) * 0.2
        return score

    def material_score(self, board, color):
        score = 0
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece:
                    val = PIECE_VALUES.get(piece[1], 0)
                    if piece[0] == color:
                        score += val
                    else:
                        score -= val
        return score

    def position_score(self, board, color, game_phase):
        score = 0
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    idx = rank * 8 + file
                    if color == 'b':
                        idx = 63 - idx
                    ptype = piece[1]
                    if ptype == 'K':
                        key = 'K_end' if game_phase == 1 else 'K_middle'
                        score += POSITION_TABLES[key][idx]
                    elif ptype == 'P':
                        pscore = (1 - game_phase) * POSITION_TABLES['P'][idx] + game_phase * POSITION_TABLES['P_end'][idx]
                        score += pscore
                    elif ptype in POSITION_TABLES:
                        score += POSITION_TABLES[ptype][idx]
        return score

    def mobility_score(self, board, color):
        moves = 0
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    moves += len(self.validator.get_all_valid_moves((file, rank)))
        return moves

    def pawn_structure_score(self, board, color):
        pawns = []
        for rank in range(8):
            for file in range(8):
                if board[rank][file] == color + 'P':
                    pawns.append((file, rank))
        score = 0
        for file, rank in pawns:
            isolated = True
            for f in [file-1, file+1]:
                if 0 <= f < 8:
                    if (f, rank) in pawns:
                        isolated = False
                        break
            if isolated:
                score += ISOLATED_PAWN_PENALTY_BY_COUNT[min(len(pawns), 8)]

            for r in range(8):
                if r != rank and (file, r) in pawns:
                    score -= 15
                    break
        return score

    def king_safety_score(self, board, color, game_phase):
        if game_phase == 1:
            return 0
        score = 0
        king_pos = None
        for rank in range(8):
            for file in range(8):
                if board[rank][file] == color + 'K':
                    king_pos = (file, rank)
                    break
            if king_pos:
                break

        if not king_pos:
            return 0

        defender_count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x, y = king_pos[0] + dx, king_pos[1] + dy
                if 0 <= x < 8 and 0 <= y < 8:
                    piece = board[y][x]
                    if piece and piece[0] == color:
                        defender_count += 1
        score += defender_count * 5
        return score
