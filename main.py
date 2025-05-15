from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import chess
import uuid

from engine_white import compute_move as compute_move_white
from engine_black import compute_move as compute_move_black

app = FastAPI()

# allow your Netlify origin to call this API
app.add_middleware(
  CORSMiddleware,
  allow_origins=["https://chess-website-test.netlify.app/"],
  allow_methods=["*"],
  allow_headers=["*"],
)

app.mount("/web", StaticFiles(directory="web"), name="web")

@app.get("/", response_class=HTMLResponse)
async def read_index():
  with open("web/index.html", "r", encoding="utf-8") as f:
    return f.read()

# store per-session boards and sides
sessions: dict[str, chess.Board] = {}
sides:    dict[str, str]        = {}

def get_board(sid: str) -> chess.Board:
  board = sessions.get(sid)
  if board is None:
    raise HTTPException(400, "Unknown session_id")
  return board

@app.post("/reset")
async def reset(payload: dict):
  sid       = payload.get("session_id")
  user_side = payload.get("user_side", "b")
  if not sid:
    raise HTTPException(400, "No session_id provided")

  # create new board and store
  board = chess.Board()
  sessions[sid] = board
  sides[sid]    = user_side

  # if engine to move first, push engine move
  if user_side == "b" and board.turn == chess.WHITE:
    m = compute_move_white(board)
    if m in board.legal_moves:
      board.push(m)
  elif user_side == "w" and board.turn == chess.BLACK:
    m = compute_move_black(board)
    if m in board.legal_moves:
      board.push(m)

  return {"fen": board.fen()}

@app.post("/move")
async def move(payload: dict):
  sid      = payload.get("session_id")
  move_str = payload.get("move")
  if not sid or not move_str:
    return JSONResponse({"error": "session_id and move are required"}, 400)

  board = get_board(sid)
  try:
    mv = chess.Move.from_uci(move_str)
  except Exception as e:
    return JSONResponse({"error": f"Invalid move: {e}"}, 400)

  if mv not in board.legal_moves:
    return JSONResponse({"error": "Illegal move"}, 400)

  board.push(mv)
  return {"fen": board.fen()}

@app.post("/engine_move")
async def engine_move(payload: dict):
  sid = payload.get("session_id")
  if not sid:
    raise HTTPException(400, "No session_id provided")

  board = get_board(sid)
  user_side = sides.get(sid, "b")

  # only move if it's engine's turn
  if not board.is_game_over() and board.turn != user_side:
    if board.turn == chess.WHITE:
      m = compute_move_white(board)
    else:
      m = compute_move_black(board)
    if m in board.legal_moves:
      board.push(m)

  return {"fen": board.fen()}
