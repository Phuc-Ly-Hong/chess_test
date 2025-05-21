import math
import random
import time
from opening_book import OpeningBook
from evaluation import Evaluation, PIECE_VALUES

class ChessBot:
    def __init__(self, move_validator):
        self.move_validator = move_validator
        self.evaluator = Evaluation(move_validator)
        self.killer_moves = {}
        self.history_table = {}
        
        try:
            self.opening_book = OpeningBook(file_path=r"D:\Chess_Test\resource\Book.txt")
        except FileNotFoundError:
            print(r"Error: Could not find Book.txt at D:\Chess_Test\resource\Book.txt")
            self.opening_book = None

    def make_move(self, board, turn, castling_rights, last_move):
        start_time = time.time()
        max_time = 5  # Increased time for move calculation (seconds)
        bot_color = 'b'  # Assuming bot plays black

        # 1. Try opening book first
        if self.opening_book and self.try_opening_book_move(board, turn, castling_rights, last_move, bot_color):
            return True

        # 2. Use Alpha-Beta search if no book move found
        print("[Bot] Starting Alpha-Beta search...")
        best_move = self.find_best_move_with_alphabeta(board, bot_color, start_time, max_time)
        
        if best_move:
            score = self.evaluator.evaluate(board, bot_color)
            print(f"[Bot] Best move found: {best_move}, Evaluation score: {score}")
            self.execute_move(board, best_move[0], best_move[1])
            return True
        
        # Fallback to random move if no valid move found
        return self.fallback_to_random_move(board, bot_color)

    def try_opening_book_move(self, board, turn, castling_rights, last_move, color):
        try:
            book_move = self.opening_book.try_get_book_move(
                board=board,
                color=color,
                turn=turn,
                castling_rights=castling_rights,
                last_move=last_move,
                weight_pow=0.5  # Adjusted to prefer more common moves
            )
            if book_move:
                print(f"[Bot] Using book move: {book_move}")
                self.execute_move(board, book_move[0], book_move[1])
                return True
        except Exception as e:
            print(f"[Bot] Book error: {str(e)}")
        return False

    def find_best_move_with_alphabeta(self, board, color, start_time, max_time):
        best_move = None
        best_score = -math.inf
        
        # Iterative deepening (reduced max depth to 5 to avoid timeout)
        for depth in range(2, 6):
            if time.time() - start_time > max_time:
                break
                
            try:
                score, move = self.alphabeta_search(
                    board=board,
                    depth=depth,
                    kappa=-math.inf,
                    beta=math.inf,
                    maximizing_player=True,
                    current_color=color,
                    start_time=start_time,
                    max_time=max_time
                )
                
                if move and score > best_score:
                    best_move = move
                    best_score = score
                    print(f"[Bot] Depth {depth}: move {move} score {score}")
            except TimeoutError:
                print(f"[Bot] Depth {depth} search timed out")
                break

        return best_move

    def alphabeta_search(self, board, depth, kappa, beta, maximizing_player, current_color, start_time, max_time):
        """Alpha-Beta search implementation"""
        if time.time() - start_time > max_time:
            raise TimeoutError()
            
        # Check terminal node (leaf node or game over)
        if depth == 0 or self.is_terminal_node(board, current_color):
            return self.evaluator.evaluate(board, current_color), None
            
        # Get and order legal moves
        moves = self.get_ordered_moves(board, current_color, depth)
        
        best_move = None
        best_value = -math.inf if maximizing_player else math.inf
        
        for move in moves:
            new_board = self.copy_board(board)
            self.execute_move(new_board, move[0], move[1])
            
            # Recursive Alpha-Beta search
            value, _ = self.alphabeta_search(
                new_board, depth-1, kappa, beta,
                not maximizing_player,
                'w' if current_color == 'b' else 'b',
                start_time, max_time
            )
            
            # Update best value and move
            if maximizing_player:
                if value > best_value:
                    best_value = value
                    best_move = move
                    kappa = max(kappa, best_value)
            else:
                if value < best_value:
                    best_value = value
                    best_move = move
                    beta = min(beta, best_value)
                    
            # Alpha-Beta pruning
            if beta <= kappa:
                self.store_killer_move(move, depth)
                break
                
        return best_value, best_move

    def is_terminal_node(self, board, color):
        """Check if node is terminal (checkmate/stalemate)"""
        if not self.get_all_valid_moves(board, color):
            return True
        return False

    def get_ordered_moves(self, board, color, depth):
        """Get and order moves for better Alpha-Beta performance"""
        moves = self.get_all_valid_moves(board, color)
        return self.order_moves(board, moves, depth, color)

    def order_moves(self, board, moves, depth, color):
        """Order moves using various heuristics"""
        scored_moves = []
        for move in moves:
            start, end = move
            piece = board[start[1]][start[0]]
            target = board[end[1]][end[0]]
            score = 0
            
            # Check if move leaves king in check
            temp_board = self.copy_board(board)
            self.execute_move(temp_board, start, end)
            if self.move_validator.is_king_in_check(temp_board, color):
                score -= 1000  # Heavy penalty for moves leaving king in check
                continue  # Skip invalid moves
            
            # Capture heuristic
            if target:
                score += 10 * PIECE_VALUES.get(target[1], 0) - PIECE_VALUES.get(piece[1], 0)
            
            # Exchange heuristic
            score += self.evaluator.exchange_score(board, color, start, end) * 5
            
            # Killer move heuristic
            if self.is_killer_move(move, depth):
                score += 100
                
            # History heuristic
            score += self.history_table.get(move, 0) * 2
            
            # Promotion heuristic
            if piece[1] == 'P' and (end[1] == 0 or end[1] == 7):
                score += 500
                
            # Castling heuristic
            if piece[1] == 'K' and abs(end[0] - start[0]) == 2:
                score += 200  # Prioritize castling
                
            # Penalty for moving to attacked square
            if self.evaluator.is_piece_attacked(temp_board, end, color):
                score -= PIECE_VALUES.get(piece[1], 0) // 2
                
            # Penalty for moving queen to attacked square
            if piece[1] == 'Q':
                if self.evaluator.is_piece_attacked(temp_board, end, color):
                    score -= 300  # Heavy penalty for moving queen to danger
                    
            # Penalty for queen exchange
            if target and target[1] == 'Q' and piece[1] == 'Q':
                score -= 100
                material_score = self.evaluator.material_score(board, color)
                if material_score > 300:
                    score += 50
                    
            scored_moves.append((score, move))
        
        # Sort moves by score (highest first)
        scored_moves.sort(reverse=True, key=lambda x: x[0])
        return [move for score, move in scored_moves]

    def is_killer_move(self, move, depth):
        """Check if move is a killer move for this depth"""
        return depth in self.killer_moves and move in self.killer_moves[depth]

    def store_killer_move(self, move, depth):
        """Store a new killer move for this depth"""
        if depth not in self.killer_moves:
            self.killer_moves[depth] = []
        if move not in self.killer_moves[depth]:
            if len(self.killer_moves[depth]) >= 2:
                self.killer_moves[depth].pop()
            self.killer_moves[depth].insert(0, move)

    def get_all_valid_moves(self, board, color):
        """Get all valid moves for current color"""
        moves = []
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    valid_moves = self.move_validator.get_all_valid_moves((file, rank))
                    for move in valid_moves:
                        # Verify move doesn't leave king in check
                        temp_board = self.copy_board(board)
                        self.execute_move(temp_board, (file, rank), move)
                        if not self.move_validator.is_king_in_check(temp_board, color):
                            moves.append(((file, rank), move))
        return moves

    def execute_move(self, board, start_pos, end_pos):
        """Execute a move on the board"""
        start_file, start_rank = start_pos
        end_file, end_rank = end_pos
        piece = board[start_rank][start_file]
        board[end_rank][end_file] = piece
        board[start_rank][start_file] = ''
        # Handle pawn promotion
        if piece and piece[1] == 'P' and (end_rank == 0 or end_rank == 7):
            board[end_rank][end_file] = piece[0] + 'Q'
        # Check if king is in check (for debugging only)
        if self.move_validator.is_king_in_check(board, piece[0]):
            print(f"[Warning] Move {start_pos}->{end_pos} leaves king in check!")

    def fallback_to_random_move(self, board, color):
        """Fallback to random move if no better move found"""
        all_moves = self.get_all_valid_moves(board, color)
        if all_moves:
            random_move = random.choice(all_moves)
            print(f"[Bot] Using random move: {random_move}")
            self.execute_move(board, random_move[0], random_move[1])
            return True
        return False

    def copy_board(self, board):
        """Create a deep copy of the board"""
        return [row[:] for row in board]