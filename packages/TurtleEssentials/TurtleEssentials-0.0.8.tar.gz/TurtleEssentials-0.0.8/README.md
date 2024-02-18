
# **Turtle Extentions**
![LOGO](https://i.postimg.cc/y6JWpLvM/Untitled-design.png)

## Docs:
### Install:
- Open CMD Prompt by pressing the windows button and typing cmd, then hit enter
- Type ```py -m pip install TurtleExtentions``` (Windows) or 
```python pip install TurtleExtentions``` (Linux/MacOS)
- Import the module inside the code like this: 
```python
import TurtleExtentions as TE
# Code here
```
### Basic shapes and arguments:
#### Basic Shapes:
- The `Shape` class contains all basic shapes
- To use it, just type 
```python
import TurtleExtentions as TE
TE.Shape.ShapeHere(params)
```
- Lets make a hexagon appear
```python
TE.Shape.Hexagon(Size=50) # The size by default is 20
```
- To change its position just use the pos1 and pos2 arguments
```python
TE.Shape.Hexagon(Size=50, pos1=150, pos2=150) # Default positons are 100, 100
```
- Now by default this would not be filled in. To do so set the DoFill paramater to True 
- You can also edit the fillcolor with the FillColor paramater like this
```python
TE.Shape.Hexagon(Size=50, pos1=150, pos2=150, DoFill=True, FillColor="Green")
```
- That would result in this
![HEXAGON-SHAPE-DOCS](https://i.postimg.cc/VLpqHSqR/image.png)

- Now if you want to delete the last drawn shape, simply use the Remove_Shape function
```python
TE.Shape.Hexagon()
TE.Shape.Remove_Shape()
``` 
- And if you want to delete a certain shape, just set the index of your shape! (Note: The shapes are stored in a list, therefore the index starts at 0)
```python
TE.Shape.Hexagon()
TE.Shape.Triangle()
TE.Shape.Remove_Shape(0)
```
- Which results in the hexagon getting deleted.

## Release 0.0.8
- Remove_Shape adjusted