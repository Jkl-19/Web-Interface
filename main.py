from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import chess
from engine_white import compute_move as compute_move_white
from engine_black import compute_move as compute_move_black

app = FastAPI()
# Serve static files under /web
app.mount("/web", StaticFiles(directory="web"), name="web")

# Serve index.html
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    with open("web/index.html", "r", encoding="utf-8") as f:
        return f.read()

# Global state
game_board = chess.Board()
user_side  = 'b'

# Human move endpoint (no FEN needed)
@app.post("/move")
async def move(payload: dict):
    move_str = payload.get("move")
    if not move_str:
        raise HTTPException(status_code=400, detail="No move provided")
    try:
        mv = chess.Move.from_uci(move_str)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid move format: {e}")
    if mv not in game_board.legal_moves:
        raise HTTPException(status_code=400, detail="Illegal move")

    game_board.push(mv)
    return {"fen": game_board.fen()}

# Engine move endpoint
@app.post("/engine_move")
async def engine_move():
    global game_board
    # only run when it's engine's turn
    if not game_board.is_game_over():
        if user_side == 'b' and game_board.turn == chess.WHITE:
            mv = compute_move_white(game_board)
            if mv in game_board.legal_moves:
                game_board.push(mv)
        elif user_side == 'w' and game_board.turn == chess.BLACK:
            mv = compute_move_black(game_board)
            if mv in game_board.legal_moves:
                game_board.push(mv)
    return {"fen": game_board.fen()}

# Reset endpoint
@app.post("/reset")
async def reset(payload: dict):
    global game_board, user_side
    user_side = payload.get("user_side", "b").lower()
    game_board = chess.Board()
    # engine first move if user chose black
    if user_side == 'b' and game_board.turn == chess.WHITE:
        mv = compute_move_white(game_board)
        if mv in game_board.legal_moves:
            game_board.push(mv)
    return {"fen": game_board.fen()}