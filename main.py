from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chess

from engine_white import compute_move as compute_move_white
from engine_black import compute_move as compute_move_black

# ——— request models ————————————————————————————————————————————————————
class MoveRequest(BaseModel):
    fen: str
    move: str

class EngineRequest(BaseModel):
    fen: str
    user_side: str   # "w" or "b"

class ResetRequest(BaseModel):
    user_side: str

# ——— app setup ———————————————————————————————————————————————————————
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chess-website-test.netlify.app/"],  # your real URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/web", StaticFiles(directory="web"), name="web")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("web/index.html", "r", encoding="utf-8") as f:
        return f.read()

# ——— human move endpoint —————————————————————————————————————————————
@app.post("/move")
def move(req: MoveRequest):
    try:
        board = chess.Board(req.fen)
    except Exception:
        raise HTTPException(400, "Invalid FEN")

    try:
        mv = chess.Move.from_uci(req.move)
    except Exception:
        raise HTTPException(400, "Invalid move format")

    if mv not in board.legal_moves:
        raise HTTPException(400, "Illegal move")

    board.push(mv)
    return {"fen": board.fen()}

# ——— engine move endpoint ————————————————————————————————————————————
@app.post("/engine_move")
def engine_move(req: EngineRequest):
    try:
        board = chess.Board(req.fen)
    except Exception:
        raise HTTPException(400, "Invalid FEN")

    user_side = req.user_side.lower()
    is_white_to_move = board.turn == chess.WHITE

    if not board.is_game_over():
        if (user_side == "w" and not is_white_to_move) or \
           (user_side == "b" and is_white_to_move):
            # pick correct engine
            mv = compute_move_white(board) if is_white_to_move else compute_move_black(board)
            if mv in board.legal_moves:
                board.push(mv)

    return {"fen": board.fen()}

# ——— reset endpoint —————————————————————————————————————————————————
@app.post("/reset")
def reset(req: ResetRequest):
    board = chess.Board()
    user_side = req.user_side.lower()
    # engine first move if user chose black
    if user_side == "b":
        mv = compute_move_white(board)
        if mv in board.legal_moves:
            board.push(mv)
    return {"fen": board.fen()}
