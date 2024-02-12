# Code von Valentino Giorgio Pino, Grundkonzept der Funktionen wurden durch das im Unterricht erlerntem Wissen
# umgesetzt und zur Hilfestellung und Bugfixing wurde ChatGPT und Phind.com genutzt

# Ungelöster Bug: Beim Ausmalen eines Polygon wird, wenn das Polygon eine Bezier-Kurve beinhaltet, diese nicht erkannt
# und daher beim Ausmalprozess ignoriert. Dieser Bug konnte ich nach sehr intensiven und langwierigen Bugfixen leider
# nicht lösen

import tkinter as tk
import numpy as np
from tkinter.colorchooser import askcolor


# Funktion zum Zeichnen einer Bézier-Kurve
def P(t, X):
    X = np.array(X)
    N, d = np.shape(X)
    N = N - 1
    xx = np.zeros((len(t), d))

    for i in range(N + 1):
        xx += np.outer(B(i, N, t), X[i])

    return xx


# Funktion zur Berechnung der Bernstein-Polynome
def B(i, N, t):
    return (np.math.factorial(N) / (np.math.factorial(i) * np.math.factorial(N - i))) * (t ** i) * ((1 - t) ** (N - i))


# Funktion zum Überprüfen, ob ein Punkt in der Nähe eines Kontrollpunkts liegt
def is_point_near_control_point(x, y, control_points, threshold=5):
    for control_point in control_points:
        if abs(control_point[0] - x) <= threshold and abs(control_point[1] - y) <= threshold:
            return True
    return False


class MiniDraw(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mini Draw")
        self.geometry("800x600")

        # Erstellen der Toolbar
        self.toolbar = tk.Frame(self, bd=1, relief="raised")
        self.toolbar.pack(side="top", fill="x")

        # Erstellen des "Choose Color" Buttons
        color_button = tk.Button(self.toolbar, text="Choose Color", command=self.choose_color)
        color_button.pack(side="left", padx=2, pady=2)

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.bind("<KeyPress-p>", self.draw_filled_polygon)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Button-3>", self._on_middle_click)
        self.canvas.bind("<B3-Motion>", self._on_middle_motion)
        self.canvas.bind("<Button-2>", self.on_right_click)
        self.canvas.bind("<B2-Motion>", self.on_right_motion)

        self.canvas.bind("<Button-1>", self.on_left_click)
        self.bind("<KeyPress-c>", self.clear_canvas)
        self.bind("<KeyPress-x>", self.toggle_points_visibility)
        self.zoom_factor = 1.0

        self.points = []
        self.lines = []
        self.control_points = []
        self.bezier_curves = []
        self.current_circle = None
        self.selected_color = "black"

    # Funktion zum Erstellen eines Punktes und einer Linie bei einem Linksklick
    def on_left_click(self, event):
        # Berechne die Canvas-Koordinaten
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        if is_point_near_control_point(canvas_x, canvas_y, [cp[:2] for cp in self.control_points]):
            return

        # Verwende die ausgewählte Farbe beim Erstellen des Punkts
        point = self.canvas.create_rectangle(canvas_x - 2, canvas_y - 2, canvas_x + 2, canvas_y + 2,
                                             fill=self.selected_color)
        self.points.append((canvas_x, canvas_y, point))

        # Verwende die ausgewählte Farbe beim Erstellen der Linie
        if len(self.points) > 1:
            line = self.canvas.create_line(self.points[-2][:2], self.points[-1][:2], fill=self.selected_color, width=2)
            self.lines.append(line)

            # Erstelle Kontrollpunkt in der Mitte der Linie und zeichne ihn in Rot
            mid_x = (self.points[-2][0] + self.points[-1][0]) / 2
            mid_y = (self.points[-2][1] + self.points[-1][1]) / 2
            control_point = self.canvas.create_rectangle(mid_x - 2, mid_y - 2, mid_x + 2, mid_y + 2,
                                                         fill="red")
            self.control_points.append((mid_x, mid_y, control_point))
            self.canvas.tag_bind(control_point, "<B1-Motion>", self.on_control_point_move)

    # Funktion zum Starten des Zeichnens eines Kreises bei einem Rechtsklick
    def on_right_click(self, event):
        # Berechne die Canvas-Koordinaten
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        # Verwende die ausgewählte Farbe beim Erstellen des Kreises
        circle = self.canvas.create_oval(canvas_x, canvas_y, canvas_x, canvas_y, fill=self.selected_color,
                                         outline="black")

        # Speichere Informationen über den aktuellen Kreis
        self.current_circle = {
            "id": circle,
            "center_x": canvas_x,
            "center_y": canvas_y,
        }

    # Funktion zum Anpassen der Größe des Kreises bei Bewegung der Maus bei gedrückter Rechtsklick-Taste

    def on_right_motion(self, event):
        if self.current_circle:
            # Berechne die Canvas-Koordinaten
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)

            center_x, center_y = self.current_circle["center_x"], self.current_circle["center_y"]
            self.canvas.coords(self.current_circle["id"], center_x, center_y, canvas_x, canvas_y)
            # Aktualisiere die Füllfarbe des Kreises
            self.canvas.itemconfigure(self.current_circle["id"], fill=self.selected_color)

    def _on_middle_click(self, event):
        self.canvas.scan_mark(event.x, event.y)

    # Bewege das Canvas und alle enthaltenen Elemente basierend auf der Mausbewegung
    def _on_middle_motion(self, event):
        # Berechne die Differenz in x- und y-Koordinaten
        dx = int(event.x - self.canvas.canvasx(0))
        dy = int(event.y - self.canvas.canvasy(0))

        # Bewege das Canvas
        self.canvas.scan_dragto(dx, dy, gain=1)

        # Aktualisiere die Koordinaten der Linien
        for line in self.lines:
            current_coords = self.canvas.coords(line)
            updated_coords = [coord + dx if idx % 2 == 0 else coord + dy for idx, coord in enumerate(current_coords)]
            self.canvas.coords(line, *updated_coords)

    # Öffne den Farbauswahldialog und setze die ausgewählte Farbe
    def choose_color(self):
        color = askcolor()[1]
        if color:
            self.selected_color = color

    # Wechsle die Sichtbarkeit der Punkte und Kontrollpunkte bei gedrückter 'c'-Taste
    def toggle_points_visibility(self, event):
        if self.points and self.control_points:
            current_state = self.canvas.itemcget(self.points[0][2], "state")
            new_state = "hidden" if current_state == "normal" else "normal"
            for point in self.points:
                self.canvas.itemconfigure(point[2], state=new_state)
            for control_point in self.control_points:
                self.canvas.itemconfigure(control_point[2], state=new_state)

    # Verschiebe den ausgewählten Kontrollpunkt und aktualisiere die Bezier-Kurve
    def on_control_point_move(self, event):
        control_point = event.widget.find_withtag(tk.CURRENT)[0]
        index = self.control_points.index(next(cp for cp in self.control_points if cp[2] == control_point))

        # Aktualisiere die Koordinaten des Kontrollpunkts
        self.canvas.coords(control_point, event.x - 2, event.y - 2, event.x + 2, event.y + 2)

        # Lösche die Linie, die mit dem Kontrollpunkt verbunden ist
        if len(self.lines) > 0:
            self.canvas.delete(self.lines[index])
            self.lines[index] = None

        # Berechne und zeichne die aktualisierte Bezier-Kurve
        t = np.linspace(0, 1, num=100)
        bezier_points = P(t, [self.points[index][:2], (event.x, event.y), self.points[index + 1][:2]])
        bezier_points_flattened = [coord for point in bezier_points for coord in point]

        if len(self.bezier_curves) > index:
            self.canvas.delete(self.bezier_curves[index])
            self.bezier_curves[index] = self.canvas.create_line(*bezier_points_flattened, fill=self.selected_color,
                                                                smooth=True)
        else:
            bezier_curve = self.canvas.create_line(*bezier_points_flattened, fill=self.selected_color, smooth=True)
            self.bezier_curves.append(bezier_curve)

    # Funktion zum Zoomen in das Canvas bei Mausrad-Bewegung
    def zoom(self, event):
        # Setze den Zoomfaktor basierend auf der Bewegungsrichtung des Mausrads
        zoom_scale = 1.1 if event.delta > 0 else 0.9

        # Skaliere alle Elemente im Canvas
        self.canvas.scale("all", event.x, event.y, zoom_scale, zoom_scale)

        # Aktualisiere das Scrollgebiet des Canvas, um den neuen Zoom-Stand zu berücksichtigen
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # Lösche alle Elemente im Canvas und setze den Zeichenzustand zurück
    def clear_canvas(self, event):
        self.canvas.delete("all")
        self.points = []
        self.lines = []
        self.control_points = []
        self.bezier_curves = []

    # Setze den Zeichenzustand zurück, um von einem neuen Punkt auf dem Canvas zu beginnen
    def reset_drawing_state(self):
        self.points = []
        self.lines = []
        self.control_points = []
        self.bezier_curves = []
        for cp in self.control_points:
            self.canvas.tag_unbind(cp[2], "<B1-Motion>")

    # Zeichne ein ausgefülltes Polygon, wenn die 'p'-Taste gedrückt wird
    def draw_filled_polygon(self, event):
        # Überprüfe, ob es genug Punkte gibt, um ein Polygon zu zeichnen
        if len(self.points) > 2:
            # Erstelle eine Liste von Koordinaten aus den Punkten
            polygon_coords = [coord for point in self.points for coord in point[:2]]
            # Erstelle das Polygon auf dem Canvas mit der ausgewählten Farbe und schwarzer Umrandung
            self.canvas.create_polygon(polygon_coords, fill=self.selected_color, outline="black")

            # Setze den Zeichenzustand zurück, um von einem neuen Punkt auf dem Canvas zu beginnen
            self.reset_drawing_state()

    # Hauptprogramm


if __name__ == "__main__":
    # Erstelle eine Instanz der MiniDraw-Klasse
    app = MiniDraw()
    # Starte die Haupt-Event-Loop der Anwendung
    app.mainloop()
