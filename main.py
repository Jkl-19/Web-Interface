import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chess

from engine_white import compute_move as compute_move_white
from engine_black import compute_move as compute_move_black

# Keep a dict of { game_id: chess.Board() } in memory
games: dict[str, chess.Board] = {}

class NewGameResponse(BaseModel):
    game_id: str
    fen: str

class MoveRequest(BaseModel):
    game_id: str
    move: str

class EngineRequest(BaseModel):
    game_id: str

class ResetRequest(BaseModel):
    game_id: str
    user_side: str   # "w" or "b"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chess-website-test.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
app.mount("/web", StaticFiles(directory="web"), name="web")

@app.post("/new_game", response_model=NewGameResponse)
def new_game():
    game_id = uuid.uuid4().hex
    board = chess.Board()
    games[game_id] = board
    return {"game_id": game_id, "fen": board.fen()}

@app.post("/move")
def move(req: MoveRequest):
    board = games.get(req.game_id)
    if board is None:
        raise HTTPException(404, "Unknown game_id")
    mv = chess.Move.from_uci(req.move)
    if mv not in board.legal_moves:
        raise HTTPException(400, "Illegal move")
    board.push(mv)
    return {"fen": board.fen()}

@app.post("/engine_move")
def engine_move(req: EngineRequest):
    board = games.get(req.game_id)
    if board is None:
        raise HTTPException(404, "Unknown game_id")
    # engine plays if it's its turn
    if not board.is_game_over():
        # white-to-move?
        if board.turn == chess.WHITE:
            mv = compute_move_white(board)
        else:
            mv = compute_move_black(board)
        if mv in board.legal_moves:
            board.push(mv)
    return {"fen": board.fen()}

@app.post("/reset")
def reset(req: ResetRequest):
    board = chess.Board()
    games[req.game_id] = board
    # engine first move if user is black
    if req.user_side == "b":
        mv = compute_move_white(board)
        if mv in board.legal_moves:
            board.push(mv)
    return {"fen": board.fen()}
