# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles
# import chess
# from engine import compute_move

# app = FastAPI()
# app.mount("/web", StaticFiles(directory="web"), name="web")

# # Serve the index page
# @app.get("/", response_class=HTMLResponse)
# async def read_index(request: Request):
#     with open("web/index.html", "r", encoding="utf-8") as file:
#         html_content = file.read()
#     return html_content

# # Create a global chess board using python-chess
# game_board = chess.Board()

# user_side = 'b'

# # Create a POST endpoint to handle moves.
# @app.post("/move")
# async def move(payload: dict):
#     move_str = payload.get("move")
#     if not move_str:
#         return JSONResponse({"error": "No move provided"}, status_code=400)
#     try:
#         # Parse the move using UCI format.
#         move = chess.Move.from_uci(move_str)
#     except Exception as e:
#         return JSONResponse({"error": "Invalid move format: " + str(e)}, status_code=400)

#     # Check if the move is legal.
#     if move not in game_board.legal_moves:
#         return JSONResponse({"error": "Illegal move"}, status_code=400)

#     # Apply the move.
#     game_board.push(move)
#     print("After human move, FEN:", game_board.fen())  # DEBUG


#     if not game_board.is_game_over() and game_board.turn != user_side:
#         engine_move = compute_move(game_board)
#         print("Engine computed move:", engine_move)  # DEBUG
#         if engine_move in game_board.legal_moves:
#             game_board.push(engine_move)
#             print("After engine move, FEN:", game_board.fen())  # DEBUG

#     # Return the updated FEN.
#     return {"fen": game_board.fen()}

# @app.post("/engine_move")
# async def engine_move_endpoint():
#     # If the game is not over and it's the engine's turn,
#     # compute the engine move.
#     if not game_board.is_game_over() and game_board.turn != user_side:
#         engine_move = compute_move(game_board)
#         if engine_move and engine_move in game_board.legal_moves:
#             game_board.push(engine_move)
#     # Return the updated FEN.
#     return {"fen": game_board.fen()}

# @app.post("/reset")
# async def reset(payload: dict):
#     global game_board, user_side
#     # Get the user's chosen side from the payload. Default to 'b' (black) if not provided.
#     user_side = payload.get("user_side", "b")
#     # Reset the global game board to the starting position.
#     game_board = chess.Board()
#     # Optionally, if the user plays black (engine plays white), 
#     # the engine should move first because white starts.
#     if user_side == "b" and not game_board.is_game_over() and game_board.turn == chess.WHITE:
#         engine_move = compute_move(game_board)
#         if engine_move in game_board.legal_moves:
#             game_board.push(engine_move)
#     return {"fen": game_board.fen()}

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import chess
from engine import compute_move

app = FastAPI()
# Mount the static folder so that files under "web" (CSS, JS, images) can be served.
app.mount("/web", StaticFiles(directory="web"), name="web")

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
        engine_move = compute_move(game_board)
        if engine_move and engine_move in game_board.legal_moves:
            game_board.push(engine_move)
            print("After engine move, FEN:", game_board.fen())
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
        engine_move = compute_move(game_board)
        if engine_move in game_board.legal_moves:
            game_board.push(engine_move)
    return {"fen": game_board.fen()}