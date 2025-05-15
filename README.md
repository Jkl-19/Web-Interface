# Using CNN for Chess Engine to Capture Style
**Jacky Lin, Michelle Wang, Stone Yan (Mentor)**

## Introduction:
This project uses Convolutional Neural Network (CNN) to capture style of a chess player. We used our games from Lichess as our database and encoded them in bitboards. 
Our output includes a matrix of size 4096, corresponding to every combination of starting and ending square on the chessboard. We used kernel sizes of 3*3, 1*8 and 8*1,
to identify rank, file, and local attributes.
