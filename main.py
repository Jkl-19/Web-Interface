from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import chess
import uuid

from engine_white import compute_move as compute_move_white
from engine_black import compute_move as compute_move_black

app = FastAPI()

# serve your static SPA
app.mount("/web", StaticFiles(directory="web"), name="web")

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    with open("web/index.html", "r", encoding="utf-8") as f:
        return f.read()

# in-memory session storage: { session_id: Board }
sessions: dict[str, chess.Board] = {}
# user side storage: { session_id: 'w' or 'b' }
sides:    dict[str, str]        = {}

def get_board(sid: str) -> chess.Board:
    board = sessions.get(sid)
    if board is None:
        raise HTTPException(status_code=400, detail="Unknown session_id")
    return board

@app.post("/reset")
async def reset(payload: dict):
    sid = payload.get("session_id")
    if not sid:
        # if client forgot to send one, give them a fresh id!
        sid = uuid.uuid4().hex
    user_side = payload.get("user_side", "b").lower()
    if user_side not in ("w", "b"):
        raise HTTPException(400, "user_side must be 'w' or 'b'")

    # create or overwrite this session
    board = chess.Board()
    sessions[sid] = board
    sides[sid]    = user_side

    # if user chose Black, White (engine) moves first
    if user_side == "b" and board.turn == chess.WHITE:
        mv = compute_move_white(board)
        if mv in board.legal_moves:
            board.push(mv)

    return JSONResponse({"session_id": sid, "fen": board.fen()})

@app.post("/move")
async def move(payload: dict):
    sid      = payload.get("session_id")
    move_str = payload.get("move")
    if not sid or not move_str:
        raise HTTPException(400, "session_id and move are required")

    board = get_board(sid)

    try:
        mv = chess.Move.from_uci(move_str)
    except Exception as e:
        raise HTTPException(400, f"Invalid move format: {e}")

    if mv not in board.legal_moves:
        raise HTTPException(400, "Illegal move")

    board.push(mv)
    return {"fen": board.fen()}

@app.post("/engine_move")
async def engine_move(payload: dict):
    sid = payload.get("session_id")
    if not sid:
        raise HTTPException(400, "session_id required")

    board     = get_board(sid)
    user_side = sides.get(sid, "b")

    # only if it's the engine’s turn
    if not board.is_game_over() and board.turn != user_side:
        if board.turn == chess.WHITE:
            mv = compute_move_white(board)
        else:
            mv = compute_move_black(board)

        if mv in board.legal_moves:
            board.push(mv)

    return {"fen": board.fen()}
