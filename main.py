from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import chess
from engine_white import compute_move as compute_move_white
from engine_black import compute_move as compute_move_black

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["https://your-netlify-site.netlify.app"],  # replace with your actual domain
  allow_methods=["GET","POST","OPTIONS"],
  allow_headers=["*"],
)

# Serve the main HTML page.
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    # Open and read the index.html file from the "web" folder.
    with open("web/index.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return html_content

# Create a global chess board using python-chess.
game_board = chess.Board()

# Define which side the user is playing (default 'b' for Black).
user_side = 'b'

# Endpoint to handle a human move only.
@app.post("/move")
async def move(payload: dict):
    move_str = payload.get("move")
    if not move_str:
        return JSONResponse({"error": "No move provided"}, status_code=400)
    try:
        # Parse the move in UCI format.
        move = chess.Move.from_uci(move_str)
    except Exception as e:
        return JSONResponse({"error": "Invalid move format: " + str(e)}, status_code=400)

    # Verify that the move is legal.
    if move not in game_board.legal_moves:
        return JSONResponse({"error": "Illegal move"}, status_code=400)

    # Apply the human move.
    game_board.push(move)
    print("After human move, FEN:", game_board.fen())

    # Return the updated board state (FEN) after the human move.
    return {"fen": game_board.fen()}

# Endpoint to compute and apply the engine's move.
@app.post("/engine_move")
async def engine_move_endpoint():
    # Check if the game is not over and it’s the engine’s turn.
    if not game_board.is_game_over() and game_board.turn != user_side:
        if user_side == "b" and game_board.turn == chess.WHITE:
            engine_move = compute_move_white(game_board)
            if engine_move in game_board.legal_moves:
                game_board.push(engine_move)
        if user_side == "w" and game_board.turn == chess.BLACK:
            engine_move = compute_move_black(game_board)
            if engine_move in game_board.legal_moves:
                game_board.push(engine_move)
    # Return the updated board state.
    return {"fen": game_board.fen()}

# Endpoint to reset the game.
@app.post("/reset")
async def reset(payload: dict):
    global game_board, user_side
    # Set the user side; default to 'b' if not provided.
    user_side = payload.get("user_side", "b")
    game_board = chess.Board()  # Reset the board to its starting position.
    # If the user is Black, white (the engine) moves first.
    if user_side == "b" and not game_board.is_game_over() and game_board.turn == chess.WHITE:
        engine_move = compute_move_white(game_board)
        if engine_move in game_board.legal_moves:
            game_board.push(engine_move)
    if user_side == "w" and not game_board.is_game_over() and game_board.turn == chess.BLACK:
        engine_move = compute_move_black(game_board)
        if engine_move in game_board.legal_moves:
            game_board.push(engine_move)
    return {"fen": game_board.fen()}