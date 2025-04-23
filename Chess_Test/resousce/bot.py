import random

class ChessBot:
    def __init__(self, move_validator):
        self.move_validator = move_validator
        
    def make_move(self, board):
        """Make a move for the black pieces"""
        # Find all possible moves for black pieces
        all_moves = self.get_all_possible_moves(board, 'b')
        
        if not all_moves:
            return False  # No moves available (checkmate or stalemate)
            
        # For now, just pick a random move
        # In a more advanced bot, we would evaluate which move is best
        chosen_move = random.choice(all_moves)
        
        # Execute the move
        start_pos, end_pos = chosen_move
        self.move_piece(board, start_pos, end_pos)
        
        return True
        
    def get_all_possible_moves(self, board, color):
        """Get all possible moves for a given color"""
        moves = []
        
        # Iterate through all squares on the board
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    # Get all valid moves for this piece
                    valid_moves = self.move_validator.get_all_valid_moves((file, rank))
                    for move in valid_moves:
                        moves.append(((file, rank), move))
                        
        return moves
        
    def move_piece(self, board, start_pos, end_pos):
        """Move a piece on the board (simplified version without castling/en passant)"""
        start_file, start_rank = start_pos
        end_file, end_rank = end_pos
        
        # Move the piece
        board[end_rank][end_file] = board[start_rank][start_file]
        board[start_rank][start_file] = ''
        
        # Handle pawn promotion
        piece = board[end_rank][end_file]
        if piece and piece[1] == 'P' and (end_rank == 0 or end_rank == 7):
            # Automatically promote to queen (simplest choice)
            board[end_rank][end_file] = piece[0] + 'Q'