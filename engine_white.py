import chess
import numpy as np
import tensorflow as tf
from tensorflow.keras import Model, models, layers, Input
from stockfish import Stockfish
from tensorflow.keras.initializers import HeNormal
import os, stat

DIR = os.path.dirname(__file__)
sf_path = os.path.join(DIR, "stockfish-ubuntu-x86-64-avx2")   # or whatever you named it

# Ensure it’s executable (just in case)
st = os.stat(sf_path)
os.chmod(sf_path, st.st_mode | stat.S_IEXEC)

# Tell the wrapper to use that binary
stockfish = Stockfish(path=sf_path, depth=15)

board=chess.Board()
def convert_board(board):
  arr=np.zeros((8,8,12),dtype=np.float32)
  lst=[
      board.pieces(chess.PAWN,chess.WHITE),
      board.pieces(chess.KNIGHT,chess.WHITE),
      board.pieces(chess.BISHOP,chess.WHITE),
      board.pieces(chess.ROOK,chess.WHITE),
      board.pieces(chess.QUEEN,chess.WHITE),
      board.pieces(chess.KING,chess.WHITE),
      board.pieces(chess.PAWN,chess.BLACK),
      board.pieces(chess.KNIGHT,chess.BLACK),
      board.pieces(chess.BISHOP,chess.BLACK),
      board.pieces(chess.ROOK,chess.BLACK),
      board.pieces(chess.QUEEN,chess.BLACK),
      board.pieces(chess.KING,chess.BLACK)
  ]
  for i in range(len(lst)):
    lst[i]=list(lst[i])
    for j in lst[i]:
      row=j//8
      col=j%8
      arr[row][col][i]=1
  return arr

def convert_move(move):#move will be a tuple of (start square,end square)
  arr=np.zeros((4096,),dtype=np.float32)
  arr[move[0]*64+move[1]]=1
  return arr

def mask_board(board):
  temp=np.zeros((4096,),dtype=np.float32)
  for i in board.legal_moves:
    temp=np.maximum(temp,convert_move((i.from_square,i.to_square)))
  return temp

input=Input(shape=(8,8,12))

conv1_1=layers.Conv2D(64,(3,3),padding="same",activation="relu",kernel_initializer=HeNormal())(input)
conv1_1_ln=layers.LayerNormalization()(conv1_1)
conv1_2=layers.Conv2D(8,(8,1),padding="same",activation="relu",kernel_initializer=HeNormal())(input)
conv1_2_ln=layers.LayerNormalization()(conv1_2)
conv1_3=layers.Conv2D(8,(1,8),padding="same",activation="relu",kernel_initializer=HeNormal())(input)
conv1_3_ln=layers.LayerNormalization()(conv1_3)

conv2_1=layers.Conv2D(128,(3,3),padding="same",activation="relu",kernel_initializer=HeNormal())(conv1_1_ln)
conv2_1_ln=layers.LayerNormalization()(conv2_1)
conv2_2=layers.Conv2D(16,(8,1),padding="same",activation="relu",kernel_initializer=HeNormal())(conv1_2_ln)
conv2_2_ln=layers.LayerNormalization()(conv2_2)
conv2_3=layers.Conv2D(16,(1,8),padding="same",activation="relu",kernel_initializer=HeNormal())(conv1_3_ln)
conv2_3_ln=layers.LayerNormalization()(conv2_3)

conv3_1=layers.Conv2D(256,(3,3),padding="same",activation="relu",kernel_initializer=HeNormal())(conv2_1_ln)
conv3_1_ln=layers.LayerNormalization()(conv3_1)
conv3_2=layers.Conv2D(32,(8,1),padding="same",activation="relu",kernel_initializer=HeNormal())(conv2_2_ln)
conv3_2_ln=layers.LayerNormalization()(conv3_2)
conv3_3=layers.Conv2D(32,(1,8),padding="same",activation="relu",kernel_initializer=HeNormal())(conv2_3_ln)
conv3_3_ln=layers.LayerNormalization()(conv3_3)

conv_all=layers.Concatenate()([conv3_1_ln,conv3_2_ln,conv3_3_ln])

flatten=layers.Flatten()(conv_all)
dense1 = layers.Dense(128, activation="relu",kernel_initializer=HeNormal())(flatten)
dense1_ln = layers.LayerNormalization()(dense1)
dense2 = layers.Dense(256, activation="relu",kernel_initializer=HeNormal())(dense1_ln)
dense2_ln = layers.LayerNormalization()(dense2)
dense3=layers.Dense(512, activation="relu",kernel_initializer=HeNormal())(dense2_ln)
dense3_ln = layers.LayerNormalization()(dense3)
dense4=layers.Dense(512, activation="relu",kernel_initializer=HeNormal())(dense3_ln)
dense4_ln=layers.LayerNormalization()(dense4)
output=layers.Dense(4096,activation="softmax")(dense4_ln)
model=Model(inputs=input,outputs=output)

model.load_weights('white.weights.h5')

def get_eval_matrix(board):
  eval_matrix=np.zeros((64,64)) #centipawn diff
  legal_mask=np.zeros((64,64),dtype=bool)

  is_white=board.turn #true if white's turn, false for black
  MATE_WEIGHT=1e4

  for move in board.legal_moves:
    board.push(move)
    stockfish.set_fen_position(board.fen())
    legal_mask[move.from_square,move.to_square]=1
    eval=stockfish.get_evaluation()
    value=eval["value"]
    if eval["type"]=="cp":
      if not is_white: #we want the matrix to represent probabilities, so should be all positive.
        value=-value
      eval_matrix[move.from_square,move.to_square]=value/100
    elif eval["type"]=="mate":
      if not is_white:
        value=-value
      if value==0:
        value=1e-9
      eval_matrix[move.from_square,move.to_square]=MATE_WEIGHT/value
    board.pop()
  illegal_mask=~legal_mask
  eval_matrix[illegal_mask]=-1e6
  return eval_matrix

def compute_move(board):
  y_pred=model.predict(convert_board(board).reshape(1,8,8,12))
  y_pred_mask=y_pred*mask_board(board)
  sum=np.sum(y_pred_mask)
  if sum==0:
    return False
  y_pred_renorm=y_pred_mask/sum
  eval_matrix=get_eval_matrix(board)
  alpha=5
  beta=0.90
  combined_matrix=y_pred_renorm*alpha+eval_matrix.flatten()
  idx=combined_matrix.argmax()
  start_sq=idx//64
  end_sq=idx%64
  return chess.Move(start_sq,end_sq)
