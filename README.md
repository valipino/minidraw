# Mini Draw - Computer Graphics and Image Processing Project

This project, developed for the course "Computer Graphics and Image Processing," is based on my own code for a mini drawing application called "Mini Draw." The fundamental concepts of the functions were acquired during the course and subsequently implemented in this project.

## Features

The application allows users to draw points, lines, circles, and Bezier curves on a Tkinter canvas. Users can select the color of the drawings, toggle the visibility of points and control points, zoom in on the canvas, and draw into the canvas using the mouse wheel. There is also an option to create filled polygons.

One notable aspect of the project is the implementation of Bezier curves, which can be created and edited by clicking and dragging control points. Bernstein polynomials are used to calculate the points on the Bezier curve. Despite intensive efforts, there is an unresolved bug: if the polygon contains a Bezier curve, it is not recognized and therefore ignored when filling the polygon.

## Demonstration

The application showcases the use of 2D graphics and interactions in Tkinter. The code is well-structured, utilizing classes for the application and functions for drawing operations. The incorporation of color selection, mouse interaction, and zoom functionality makes the application versatile and user-friendly. The unresolved bug, though present, highlights the challenges and learning process involved in debugging more complex projects.
