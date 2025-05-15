from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chess
from engine_white import compute_move as compute_move_white
from engine_black import compute_move as compute_move_black

# Pydantic models for request bodies\ 
class MovePayload(BaseModel):
    fen: str
    move: str

class EnginePayload(BaseModel):
    fen: str
    user_side: str  # 'w' or 'b'

class ResetPayload(BaseModel):
    user_side: str  # 'w' or 'b'

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chess-website-test.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static front-end
app.mount("/web", StaticFiles(directory="web"), name="web")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("web/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/move")
def move(req: MovePayload):
    board = chess.Board(req.fen)
    try:
        mv = chess.Move.from_uci(req.move)
    except Exception:
        raise HTTPException(400, "Invalid move format")
    if mv not in board.legal_moves:
        raise HTTPException(400, "Illegal move")
    board.push(mv)
    return {"fen": board.fen()}

@app.post("/engine_move")
def engine_move(req: EnginePayload):
    board = chess.Board(req.fen)
    user_side = req.user_side
    # If it's engine's turn, compute and apply move
    if not board.is_game_over() and board.turn != (chess.WHITE if user_side=='w' else chess.BLACK):
        # white engine if user is black, vice versa
        if board.turn == chess.WHITE:
            mv = compute_move_white(board)
        else:
            mv = compute_move_black(board)
        if mv and mv in board.legal_moves:
            board.push(mv)
    return {"fen": board.fen()}

@app.post("/reset")
def reset(req: ResetPayload):
    board = chess.Board()
    user_side = req.user_side
    # Engine to move first if user chose black
    if user_side == 'b' and board.turn == chess.WHITE:
        mv = compute_move_white(board)
        if mv in board.legal_moves:
            board.push(mv)
    elif user_side == 'w' and board.turn == chess.BLACK:
        mv = compute_move_black(board)
        if mv in board.legal_moves:
            board.push(mv)
    return {"fen": board.fen()}
