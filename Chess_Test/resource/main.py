import pygame
import os
from move_validator import MoveValidator 
from bot import ChessBot

# Initialize pygame
pygame.init()

# Window dimensions
WIDTH, HEIGHT = 850, 850
SQUARE_SIZE = WIDTH // 8  # Size of each square
  
# Colors
LIGHT_COLOR = (238, 238, 210)
DARK_COLOR = (118, 150, 86)
TEXT_COLOR = (0, 0, 0)

# Thêm vào phần khai báo biến toàn cục
valid_moves = []  # Lưu trữ các nước đi hợp lệ
highlight_color = (100, 200, 255, 100)  # Màu xanh nhạt trong suốt để highlight

# Font for coordinates
pygame.font.init()
FONT = pygame.font.SysFont("Arial", 24)

# Create window
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Board")

# Path to assets directory
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

# Load chess pieces images
def load_pieces():
    pieces = {}
    piece_names = ['K', 'Q', 'R', 'B', 'N', 'P']
    colors = {'w': 'white', 'b': 'black'}

    for color_prefix, color_name in colors.items():
        for piece in piece_names:
            image_path = os.path.join(ASSETS_DIR, f"{color_prefix}{piece}.png")
            try:
                img = pygame.image.load(image_path)
                img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
                pieces[f"{color_name}_{piece}"] = img
            except Exception as e:
                print(f"Unable to load image: {image_path} with error {e}")
    return pieces

# Load pieces images
pieces = load_pieces()

# Initial board setup
initial_board = [
    ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
    ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
]

castling_rights = "KQkq"  # K=White kingside, Q=White queenside, k=Black kingside, q=Black queenside
last_move = None
move_validator = MoveValidator(initial_board, castling_rights, last_move)
promoting_pawn = None  # Lưu trữ vị trí quân tốt cần phong cấp
promotion_pieces = ['Q', 'R', 'B', 'N']  # Các loại quân có thể phong cấp thành

# Variables for game state
selected_piece = None
selected_pos = None
turn = True  # True for white, False for black
bot = ChessBot(move_validator)
game_over = False
winner = None

def draw_board():
    for file in range(8):
        for rank in range(8):
            is_light_square = (file + rank) % 2 == 0
            color = LIGHT_COLOR if is_light_square else DARK_COLOR
            pygame.draw.rect(win, color, (file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
            # Vẽ highlight cho các ô có thể di chuyển
            if selected_piece and (file, rank) in valid_moves:
                highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                highlight.fill(highlight_color)
                win.blit(highlight, (file * SQUARE_SIZE, rank * SQUARE_SIZE))
            
            piece_code = initial_board[rank][file]
            if piece_code:
                color_prefix = piece_code[0]
                piece_name = piece_code[1]
                color_name = 'white' if color_prefix == 'w' else 'black'
                piece_key = f"{color_name}_{piece_name}"
                if piece_key in pieces:
                    win.blit(pieces[piece_key], (file * SQUARE_SIZE, rank * SQUARE_SIZE))

    if promoting_pawn:
        pawn_color = initial_board[promoting_pawn[1]][promoting_pawn[0]][0]
        draw_promotion_menu(pawn_color)

    for i in range(8):
        rank_text = FONT.render(str(8 - i), True, TEXT_COLOR)
        win.blit(rank_text, (5, i * SQUARE_SIZE + 5))
        file_text = FONT.render(chr(97 + i), True, TEXT_COLOR)
        win.blit(file_text, (i * SQUARE_SIZE + SQUARE_SIZE - 20, HEIGHT - 25))

def display_game_result(winner):
    win.fill((0, 0, 0, 180))  # Màn hình tối mờ
    font = pygame.font.SysFont("Arial", 50)
    
    if winner:
        text = f"{'White' if winner == 'w' else 'Black'} wins!"
        color = (255, 255, 255) if winner == 'w' else (200, 200, 200)
    else:
        text = "Game ended in draw!"
        color = (200, 200, 0)
    
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
    win.blit(text_surface, text_rect)
    
    # Hiển thị hướng dẫn tiếp tục
    small_font = pygame.font.SysFont("Arial", 30)
    continue_text = small_font.render("Press any key to close", True, (255, 255, 255))
    win.blit(continue_text, (WIDTH//2 - 150, HEIGHT//2 + 60))

# Function to get the square at the mouse position
def get_square_at_pos(mouse_pos):
    x, y = mouse_pos
    return x // SQUARE_SIZE, y // SQUARE_SIZE

def update_castling_rights(piece_moved, start_pos):
    global castling_rights
    
    start_file, start_rank = start_pos
    
    # If the king moves, remove all castling rights for that color
    if piece_moved[1] == 'K':
        if piece_moved[0] == 'w':  # White king
            castling_rights = castling_rights.replace('K', '').replace('Q', '')
        else:  # Black king
            castling_rights = castling_rights.replace('k', '').replace('q', '')
    
    # If a rook moves from its starting position, remove its specific castling right
    elif piece_moved[1] == 'R':
        # White rooks
        if piece_moved[0] == 'w':
            if start_file == 0 and start_rank == 7:  # Queenside rook (a1)
                castling_rights = castling_rights.replace('Q', '')
            elif start_file == 7 and start_rank == 7:  # Kingside rook (h1)
                castling_rights = castling_rights.replace('K', '')
        # Black rooks
        else:
            if start_file == 0 and start_rank == 0:  # Queenside rook (a8)
                castling_rights = castling_rights.replace('q', '')
            elif start_file == 7 and start_rank == 0:  # Kingside rook (h8)
                castling_rights = castling_rights.replace('k', '')
    
    # Also update the move validator's castling rights
    move_validator.castling_rights = castling_rights

def handle_promotion(piece_type):
    global promoting_pawn, turn
    
    if promoting_pawn:
        file, rank = promoting_pawn
        pawn_color = initial_board[rank][file][0]
        initial_board[rank][file] = pawn_color + piece_type
        promoting_pawn = None
        
        # Hoàn thành nước đi bằng cách đổi lượt
        turn = not turn

def move_piece(start_pos, end_pos):
    global castling_rights, turn, last_move, promoting_pawn

    start_file, start_rank = start_pos
    end_file, end_rank = end_pos
    piece_moved = initial_board[start_rank][start_file]

    # *Kiểm tra bắt tốt qua đường*
    if piece_moved[1] == 'P' and start_file != end_file and initial_board[end_rank][end_file] == '':
        if last_move:
            last_start, last_end = last_move
            last_start_file, last_start_rank = last_start
            last_end_file, last_end_rank = last_end

            # Xác định quân tốt bị bắt
            last_piece = initial_board[last_end_rank][last_end_file] if 0 <= last_end_rank < 8 and 0 <= last_end_file < 8 else ''
            if last_piece == ('bP' if piece_moved[0] == 'w' else 'wP'):
                if last_start_rank == (6 if piece_moved[0] == 'b' else 1) and last_end_rank == (4 if piece_moved[0] == 'b' else 3):
                    if last_end_file == end_file and last_end_rank == start_rank:
                        # Xóa quân tốt bị bắt
                        initial_board[last_end_rank][last_end_file] = ''  

    # *Thực hiện di chuyển quân cờ*
    initial_board[end_rank][end_file] = piece_moved
    initial_board[start_rank][start_file] = ''

    # Tốt phong cấp
    if piece_moved[1] == 'P' and (end_rank ==0 or end_rank == 7):
        promoting_pawn = (end_file,end_rank)
        return

    # *Cập nhật nước đi cuối cùng*
    last_move = (start_pos, end_pos)

    # *Cập nhật quyền nhập thành*
    update_castling_rights(piece_moved, start_pos)

    # *Cập nhật validator*
    move_validator.board = initial_board
    move_validator.castling_rights = castling_rights
    move_validator.last_move = last_move

    
    # Xử lý nhập thành (di chuyển xe)
    if piece_moved[1] == 'K' and abs(start_file - end_file) == 2:
        if end_file > start_file:  # Nhập thành cánh vua
            # Di chuyển xe từ h1 sang f1 (đen) hoặc h8 sang f8 (trắng)
            initial_board[end_rank][5] = initial_board[end_rank][7]
            initial_board[end_rank][7] = ''
            # Remove castling rights after castling
            if piece_moved[0] == 'w':
                castling_rights = castling_rights.replace('K', '').replace('Q', '')
            else:
                castling_rights = castling_rights.replace('k', '').replace('q', '')
        else:  # Nhập thành cánh hậu
            # Di chuyển xe từ a1 sang d1 (đen) hoặc a8 sang d8 (trắng)
            initial_board[end_rank][3] = initial_board[end_rank][0]
            initial_board[end_rank][0] = ''
            # Remove castling rights after castling
            if piece_moved[0] == 'w':
                castling_rights = castling_rights.replace('K', '').replace('Q', '')
            else:
                castling_rights = castling_rights.replace('k', '').replace('q', '')
    
    # Cập nhật quyền nhập thành
    update_castling_rights(piece_moved, start_pos)
    
    # Cập nhật validator với board mới và castling rights
    move_validator.board = initial_board
    move_validator.castling_rights = castling_rights
    move_validator.last_move = last_move

def draw_promotion_menu(pawn_color):
    promotion_color = 'white' if pawn_color == 'w' else 'black'
    menu_width = SQUARE_SIZE
    menu_height = 4 * SQUARE_SIZE
    menu_x = WIDTH // 2 - menu_width // 2
    menu_y = HEIGHT // 2 - menu_height // 2
    
    # Vẽ nền menu
    pygame.draw.rect(win, (200, 200, 200), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(win, (0, 0, 0), (menu_x, menu_y, menu_width, menu_height), 2)
    
    # Vẽ các lựa chọn phong cấp
    for i, piece in enumerate(promotion_pieces):
        piece_key = f"{promotion_color}_{piece}"
        if piece_key in pieces:
            win.blit(pieces[piece_key], (menu_x, menu_y + i * SQUARE_SIZE))

# Main function
def main():
    global selected_piece, selected_pos, turn, valid_moves, promoting_pawn, initial_board, game_over, winner
    
    running = True
    clock = pygame.time.Clock()

    while running:
        # Kiểm tra trạng thái game trước khi xử lý lượt đi
        current_color = 'w' if turn else 'b'
        if move_validator.is_checkmate(current_color):
            game_over = True
            winner = 'b' if current_color == 'w' else 'w'
        elif move_validator.is_stalemate(current_color):
            game_over = True
            winner = None

        if game_over:
            draw_board()  # Vẽ bàn cờ trước
            display_game_result(winner)  # Hiển thị thông báo kết quả
            pygame.display.flip()
            
            # Chờ người chơi nhấn phím để thoát
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    running = False
            continue

        # Bot đi nếu đến lượt đen và không đang phong cấp
        if not turn and not promoting_pawn and not game_over:
            result = bot.make_move(initial_board, turn, castling_rights, last_move)
            if isinstance(result, tuple):
                promoting_pawn = result
            else:
                turn = not turn
            
            # Cập nhật trạng thái cho move validator
            move_validator.board = initial_board
            move_validator.last_move = last_move
            
            # Hiển thị nước đi của bot
            draw_board()
            pygame.display.flip()
            pygame.time.delay(500)  # Dừng ngắn để xem nước đi

        # Xử lý sự kiện người chơi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouse_pos = pygame.mouse.get_pos()
                file, rank = get_square_at_pos(mouse_pos)

                # Xử lý phong cấp
                if promoting_pawn:
                    pawn_file, pawn_rank = promoting_pawn
                    menu_width = SQUARE_SIZE
                    menu_height = 4 * SQUARE_SIZE
                    menu_x = WIDTH // 2 - menu_width // 2
                    menu_y = HEIGHT // 2 - menu_height // 2
                    
                    if (menu_x <= mouse_pos[0] < menu_x + menu_width and 
                        menu_y <= mouse_pos[1] < menu_y + menu_height):
                        selected_index = (mouse_pos[1] - menu_y) // SQUARE_SIZE
                        if 0 <= selected_index < len(promotion_pieces):
                            handle_promotion(promotion_pieces[selected_index])
                    continue

                # Xử lý chọn quân và di chuyển
                piece_code = initial_board[rank][file]
                
                if selected_piece is None:
                    if piece_code and ((turn and piece_code[0] == 'w') or (not turn and piece_code[0] == 'b')):
                        selected_piece = piece_code
                        selected_pos = (file, rank)
                        valid_moves = move_validator.get_all_valid_moves(selected_pos)
                else:
                    if (file, rank) in valid_moves:
                        move_piece(selected_pos, (file, rank))
                        if not promoting_pawn:
                            turn = not turn
                    selected_piece = None
                    selected_pos = None
                    valid_moves = []

        # Vẽ bàn cờ
        draw_board()
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
