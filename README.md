# Graph Reader
OpenCV Application that tries to process images of graphs and generate the corresponding Adjacency Matrix.

**Requirements**:
* Python3.X
* OpenCV 4.X
* Pytesseract (Used to read node names)
* Numpy

**Installation**: 
* git clone this repository onto your system and open a terminal in the repository folder
* install needed modules using `pip install -r requirements.txt`

**Execution**:
* Run graph.py while using the `-i`argument to pass the path to your input image
* For example: `python3 graph.py -i graph7.png`
* A new directory called 'outputs' will be created in your working directory containing the the output JSON file with the adjacency matrix, as well as the inputted image with detected nodes and edges highlighted.

**Sample Output**: <br>

