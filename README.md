# Using CNN for Chess Engine to Capture Style
**Jacky Lin, Michelle Wang, Stone Yan (Mentor)**

## Introduction:
This project uses Convolutional Neural Network (CNN) to capture style of a chess player. We used our games from Lichess as our database and encoded them in bitboards. 
Our output includes a matrix of size 4096, corresponding to every combination of starting and ending square on the chessboard. We used three different kernel sizes
to identify rank, file, and local attributes.

After training our neural network, we downloaded the weights and combined them with Stockfish, to make sure that while capturing style, the engine makes accurate moves.
Our engine logic is included in engine_white.py and engine_black.py.

This is the repository for the website server (both front-end and back-end. Front-end webpage is included in the folder "web", which we host on netlify, and the 
back-end is hosted on Google Cloud. The front-end then makes API calls to the cloud server to retrieve an engine move.

To start, go to https://chess-website-test.netlify.app/, and click on "Play as White" / "Play as Black" on the top left. The engine should make a move when it is their turn.

## Note:
There has been some server issues due to large amounts of requests. Please allow a while for the engine to run. If issues persist, feel free to contact us at jlin25@stevensonschool.org.
We appreciate your valuable feedback and will continue adding to our website!
