PIECE_VALUES = {
    'P': 100, 'N': 300, 'B': 320, 'R': 500, 'Q': 900, 'K': 20000
}

PASSED_PAWN_BONUSES = [0, 120, 80, 50, 30, 15, 15]
ISOLATED_PAWN_PENALTY_BY_COUNT = [0, -10, -25, -50, -75, -75, -75, -75, -75]
KING_PAWN_SHIELD_SCORES = [4, 7, 4, 3, 6, 3]

POSITION_TABLES = {
    'P': [
         0,   0,   0,   0,   0,   0,   0,   0,
        50,  50,  50,  50,  50,  50,  50,  50,
        10,  10,  20,  30,  30,  20,  10,  10,
         5,   5,  10,  25,  25,  10,   5,   5,
         0,   0,   0,  20,  20,   0,   0,   0,
         5,  -5, -10,   0,   0, -10,  -5,   5,
         5,  10,  10, -20, -20,  10,  10,   5,
         0,   0,   0,   0,   0,   0,   0,   0
    ],
    'P_end': [
         0,   0,   0,   0,   0,   0,   0,   0,
        80,  80,  80,  80,  80,  80,  80,  80,
        50,  50,  50,  50,  50,  50,  50,  50,
        30,  30,  30,  30,  30,  30,  30,  30,
        20,  20,  20,  20,  20,  20,  20,  20,
        10,  10,  10,  10,  10,  10,  10,  10,
        10,  10,  10,  10,  10,  10,  10,  10,
         0,   0,   0,   0,   0,   0,   0,   0
    ],
    'R': [
         0,   0,   0,   0,   0,   0,   0,   0,
         5,  10,  10,  10,  10,  10,  10,   5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
         0,   0,   0,   5,   5,   0,   0,   0
    ],
    'N': [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ],
    'B': [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    ],
    'Q': [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
         -5,  0,  5,  5,  5,  5,  0, -5,
          0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ],
    'K_middle': [
        -80, -70, -70, -70, -70, -70, -70, -80,
        -60, -60, -60, -60, -60, -60, -60, -60,
        -40, -50, -50, -60, -60, -50, -50, -40,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
         20,  20,  -5,  -5,  -5,  -5,  20,  20,
         20,  30,  10,   0,   0,  10,  30,  20
    ],
    'K_end': [
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
        score += self.king_safety_score(board, color, game_phase) * 0.3
        score += self.piece_development_score(board, color, game_phase) * 0.2
        score += self.piece_protection_score(board, color) * 0.15
        score += self.center_control_score(board, color) * 0.1
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

    def exchange_score(self, board, color, start_pos, end_pos):
        target_piece = board[end_pos[1]][end_pos[0]]
        if not target_piece:
            return 0
        score = PIECE_VALUES.get(target_piece[1], 0)
        temp_board = [row[:] for row in board]
        temp_board[end_pos[1]][end_pos[0]] = board[start_pos[1]][start_pos[0]]
        temp_board[start_pos[1]][start_pos[0]] = ''
        if self.is_piece_attacked(temp_board, end_pos, color):
            score -= PIECE_VALUES.get(board[start_pos[1]][start_pos[0]][1], 0)
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
        opponent_pawns = []
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece == color + 'P':
                    pawns.append((file, rank))
                elif piece and piece[0] != color and piece[1] == 'P':
                    opponent_pawns.append((file,rank))

        score = 0
        for file, rank in pawns:
            
            is_passed = True
            for opp_file, opp_rank in opponent_pawns:
                if (color == 'w' and opp_rank < rank) or (color == 'b' and opp_rank > rank):
                    if abs(opp_file - file) <= 1:
                        is_passed = False
                        break
        
            if is_passed:
                advance = rank if color == 'b' else 7 - rank
                score += PASSED_PAWN_BONUSES[min(advance, 6)]

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
        score = 0
        king_pos = None
    
        # Find king position
        for rank in range(8):
            for file in range(8):
                if board[rank][file] == color + 'K':
                    king_pos = (file, rank)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return 0
        
        # Check if king is in check
        in_check = self.validator.is_king_in_check(board, color)
        if in_check:
            score -= 150
        
        # Count attackers
        attacker_count = self.count_king_attackers(board, king_pos, color)
        score -= attacker_count * 40
        
        # Evaluate pawn shield
        if game_phase == 0:
            score += self.evaluate_pawn_shield(board, king_pos, color)
        
        # Penalize exposed king
        if self.is_king_exposed(board, king_pos, color):
            score -= 80
            
        return score

    def count_king_attackers(self, board, king_pos, color):
        opponent_color = 'w' if color == 'b' else 'b'
        attackers = 0
        king_file, king_rank = king_pos
    
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == opponent_color:
                    if (king_file, king_rank) in self.validator.get_all_valid_moves((file, rank)):
                        attackers += 1
        return attackers

    def evaluate_pawn_shield(self, board, king_pos, color):
        file, rank = king_pos
        shield_score = 0
        pawn_dir = 1 if color == 'w' else -1
    
        # Check squares in front of king
        for f in [file-1, file, file+1]:
            if 0 <= f < 8:
                shield_rank = rank + pawn_dir
                if 0 <= shield_rank < 8:
                    if board[shield_rank][f] == color + 'P':
                        shield_score += 30
                    elif f == file:
                        shield_score -= 20
                        
        return shield_score

    def is_king_exposed(self, board, king_pos, color):
        file, rank = king_pos
        open_file = True
        for r in range(8):
            if r != rank and board[r][file] == color + 'P':
                open_file = False
                break
        return open_file

    def piece_development_score(self, board, color, game_phase):
        if game_phase == 1:
            return 0
        score = 0
        
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    if piece[1] in ['N', 'B']:
                        if (color == 'w' and rank < 7) or (color == 'b' and rank > 0):
                            score += 30  # Increased bonus for developing knights and bishops
                    elif piece[1] == 'Q':
                        if (color == 'w' and rank < 7) or (color == 'b' and rank > 0):
                            score -= 30
                            
        king_pos = None
        for rank in range(8):
            for file in range(8):
                if board[rank][file] == color + 'K':
                    king_pos = (file, rank)
                    break
            if king_pos:
                break
        if king_pos:
            file, rank = king_pos
            if (color == 'w' and rank == 7 and (file in [2, 6])) or \
               (color == 'b' and rank == 0 and (file in [2, 6])):
                score += 100  # Increased bonus for castling
            if color == 'w' and rank == 7:
                if file == 4 and (board[7][5] == '' and board[7][6] == ''):  # Kingside
                    score += 50
                if file == 4 and (board[7][1] == '' and board[7][2] == '' and board[7][3] == ''):  # Queenside
                    score += 50
            elif color == 'b' and rank == 0:
                if file == 4 and (board[0][5] == '' and board[0][6] == ''):  # Kingside
                    score += 50
                if file == 4 and (board[0][1] == '' and board[0][2] == '' and board[0][3] == ''):  # Queenside
                    score += 50
        
        return score
    
    def piece_protection_score(self, board, color):
        score = 0
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    protected = self.is_piece_protected(board, (file, rank), color)
                    if protected:
                        score += 15  # Increased bonus for protected pieces
                    piece_value = PIECE_VALUES.get(piece[1], 0)
                    if piece_value > 300 and self.is_piece_attacked(board, (file, rank), color):
                        score -= piece_value // 2  # Heavier penalty for attacked high-value pieces
                    if piece[1] == 'Q' and self.is_piece_attacked(board, (file, rank), color):
                        score -= 200  # Extra penalty for attacked queen
        return score

    def is_piece_protected(self, board, pos, color):
        file, rank = pos
        for r in range(8):
            for f in range(8):
                piece = board[r][f]
                if piece and piece[0] == color and piece[1] != 'K':
                    if (file, rank) in self.validator.get_all_valid_moves((f, r)):
                        return True
        return False

    def is_piece_attacked(self, board, pos, color):
        opponent_color = 'w' if color == 'b' else 'b'
        file, rank = pos
        for r in range(8):
            for f in range(8):
                piece = board[r][f]
                if piece and piece[0] == opponent_color:
                    if (file, rank) in self.validator.get_all_valid_moves((f, r)):
                        return True
        return False
    
    def center_control_score(self, board, color):
        center_squares = [(3,3), (3,4), (4,3), (4,4)]
        score = 0
        for file, rank in center_squares:
            piece = board[rank][file]
            if piece and piece[0] == color:
                score += 15
                if piece[1] == 'Q':
                    score += 30  # Extra bonus for queen in center
            for r in range(8):
                for f in range(8):
                    piece = board[r][f]
                    if piece and piece[0] == color:
                        if (file, rank) in self.validator.get_all_valid_moves((f, r)):
                            score += 10
        return score