from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys

# Global variable that stores the current height of the window.
# Required for using the y coordinate of the mouse.
global windowHeight
windowHeight = 500

# Boolean and coordinates for drawing temporary lines
global isDrawing
isDrawing = False
global mouseX
global mouseY

# Global lists that store pairs of vertexes selected by the user.
global initialVertexes
initialVertexes = []
global endVertexes
endVertexes = []

# List that stores all intersection points' coordinates.
# Since the intersections cannot change position (lines don't move or cease to exist),
# we can keep storing all new intersections as we insert new lines.
global lineIntersections
lineIntersections = []

# Class that contains the coordinates of a point, be it a line's vertex
# or an intersection point. Includes a comparison operator.
class Vertex:
	def __init__(self, x, y):
		self.x = x
		self.y = y
	
	def __eq__(self, other):
		return self.x == other.x and self.y == other.y

# Mouse function that adds vertexes to the global list.
# Each pair is defined by the vertex where the mouse button is pressed
# and the vertex where the mouse button is released.
def mouseClick(button, state, x, y):
	global initialVertexes
	global endVertexes
	global windowHeight
	global isDrawing
	global mouseX
	global mouseY
	
	if (button == GLUT_LEFT_BUTTON and state == GLUT_DOWN):
		initialVertexes.append(Vertex(x, windowHeight-y))
		isDrawing = True
		mouseX = x
		mouseY = windowHeight - y
	elif (button == GLUT_LEFT_BUTTON and state == GLUT_UP and isDrawing):
		# If the mouse is released at the same position it was pressed (line with zero size),
		# the line is discarded.
		if Vertex(x, windowHeight-y) == initialVertexes[len(initialVertexes)-1]:
			initialVertexes.pop()
		else:
			endVertexes.append(Vertex(x, windowHeight-y))
			insertNewIntersections(len(endVertexes)-1)
		isDrawing = False
	# Right click cancels the new line and discards its initial position.
	elif (button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN and isDrawing):
		initialVertexes.pop()
		isDrawing = False
	glutPostRedisplay()
		

# Mouse function that registers the position of the cursor
# for drawing temporary lines
def mouseMovement(x, y):
	global windowHeight
	global isDrawing
	global mouseX
	global mouseY
	
	if (isDrawing):
		mouseX = x
		mouseY = windowHeight - y
		
def resizeWindow(w, h):
	global windowHeight
	global cameraBounds
	
	# Prevents window from having zero height or width
	if(h == 0):
		h = 1
	if(w == 0):
		w = 1
	
	glMatrixMode(GL_PROJECTION) # sets the current matrix to projection
	glLoadIdentity() # multiply the current matrix by identity matrix
	gluOrtho2D(0, w, 0, h) # sets the camera's size as the full window area
	
	windowHeight = h
	glViewport(0, 0, w, h)
	
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	gluLookAt(0,0,1,0,0,0,0,1,0)
	
# Simple intersection function using determinants.
def checkForIntersection(a1, a2, b1, b2):
	xdiff = Vertex(a1.x - a2.x, b1.x - b2.x)
	ydiff = Vertex(a1.y - a2.y, b1.y - b2.y)

	def det(a, b):
		return a.x * b.y - a.y * b.x

	div = det(xdiff, ydiff)
	if div == 0:
	   return False

	d = Vertex(det(a1, a2), det(b1, b2))
	x = det(d, xdiff) / div
	y = det(d, ydiff) / div
	
	# Tests if the intersection happens within the boundaries of the segments.
	# Has a 3 pixels room for error (so if the lines are close enough, it detects the intersection).
	if not ((x >= a1.x - 3 and x <= a2.x + 3) or (x <= a1.x + 3 and x >= a2.x - 3)):
		return False
	if not ((x >= b1.x - 3 and x <= b2.x + 3) or (x <= b1.x + 3 and x >= b2.x - 3)):
		return False
	if not ((y >= a1.y - 3 and y <= a2.y + 3) or (y <= a1.y + 3 and y >= a2.y - 3)):
		return False
	if not ((y >= b1.y - 3 and y <= b2.y + 3) or (y <= b1.y + 3 and y >= b2.y - 3)):
		return False
	
	return Vertex(x, y)
	
# Function that returns all intersections found.
# Each line looks at all other lines to test if they intersect each other.
def findIntersections():
	global initialVertexes
	global endVertexes
	
	lineIntersections = []
	i = 0
	while (i < len(endVertexes)):
		j = i + 1
		while (j < len(endVertexes)):
			aux = checkForIntersection(initialVertexes[i],endVertexes[i],initialVertexes[j],endVertexes[j])
			if aux != False: lineIntersections.append(aux)
			j = j + 1
		i = i + 1
	return lineIntersections
	
# Function that inserts all intersections found with a given line into the global list of intersections.
# The line represented by initialVertexes[index] and endVertexes[index] finds its intersections with
# each of the other lines.
def insertNewIntersections(index):
	global initialVertexes
	global endVertexes
	global lineIntersections
	
	i = 0
	while (i < len(endVertexes)):
		aux = checkForIntersection(initialVertexes[index],endVertexes[index],initialVertexes[i],endVertexes[i])
		if aux != False: lineIntersections.append(aux)
		i = i + 1
	return lineIntersections
	
# Function that draws the scene every frame.
def renderScene():
	global initialVertexes
	global endVertexes
	global lineIntersections
	global mouseX
	global mouseY
	global isDrawing
	
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); # clears the buffer to draw new frame
	glColor3f(1,1,0) # sets the color for the lines as yellow
	glLineWidth(2) # sets the width of the lines
	
	# For loop to draw each line by using pairs of vertexes from the global list.
	k = 0
	while(k < len(endVertexes)):

		glBegin(GL_LINES)
		glVertex2i(initialVertexes[k].x,initialVertexes[k].y)
		glVertex2i(endVertexes[k].x,endVertexes[k].y)
		glEnd()
		
		k = k + 1

	glColor3f(0,.3,1) # sets the color for the intersection points as blue 
	glPointSize(10) # sets the size of the points
	
	
	# Foreach loop to draw the intersection points.
	# If the intersections could change position, we would use
	# 	for j in findIntersections():
	# instead.
	for j in lineIntersections:
		glBegin(GL_POINTS)
		glVertex2i(j.x,j.y)
		glEnd()
		
	if (isDrawing):
		glColor4f(1,1,0,.5) # sets the color for the temporary lines as transparent yellow
		glBegin(GL_LINES)
		glVertex2i(initialVertexes[len(initialVertexes)-1].x,initialVertexes[len(initialVertexes)-1].y)
		glVertex2i(mouseX,mouseY)
		glEnd()
		
	glFlush()
	

def main():
	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
	glutInitWindowPosition(100,100)
	glutInitWindowSize(500,500)
	glutCreateWindow("Trabalho 1 CG - Julio Rama")
	glClearColor(0, .3, 0, 1); # sets the background color to dark green
	glutDisplayFunc(renderScene)
	glEnable(GL_BLEND) # enables blending for transparent lines
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) # sets the blending function
	glutIdleFunc(renderScene)
	glutMouseFunc(mouseClick)
	glutMotionFunc(mouseMovement)
	glutReshapeFunc(resizeWindow)
	glutMainLoop()

if __name__ == '__main__': main()
