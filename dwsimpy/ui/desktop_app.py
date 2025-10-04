"""
Desktop UI for DWSIMpy Flowsheet Editing

Uses PyQt6 for graphical interface and NetworkX for flowsheet graph.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem,
    QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QListWidget, QSplitter,
    QGraphicsEllipseItem, QGraphicsLineItem, QMenu
)
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import QPen, QBrush, QColor, QAction, QDrag
from PyQt6.QtCore import QMimeData
import networkx as nx

from ..unit_ops.mixer import Mixer
from ..unit_ops.heater import Heater
from ..streams.material_stream import MaterialStream


class UnitItem(QGraphicsEllipseItem):
    """Graphical item for unit operations."""

    def __init__(self, unit_op, x, y):
        super().__init__(-30, -30, 60, 60)
        self.unit_op = unit_op
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("lightblue")))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # Add label
        # For simplicity, no text label yet

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.pos())
        super().mousePressEvent(event)

    def show_context_menu(self, pos):
        menu = QMenu()
        edit_action = menu.addAction("Edit Properties")
        delete_action = menu.addAction("Delete")
        action = menu.exec(self.mapToGlobal(pos.toPoint()))
        if action == edit_action:
            self.edit_properties()
        elif action == delete_action:
            self.scene().removeItem(self)

    def edit_properties(self):
        # Placeholder for property editor
        print(f"Edit {self.unit_op.component_name}")


class StreamItem(QGraphicsLineItem):
    """Graphical item for streams."""

    def __init__(self, start_item, end_item):
        super().__init__()
        self.start_item = start_item
        self.end_item = end_item
        self.update_position()
        self.setPen(QPen(Qt.GlobalColor.blue, 2))

    def update_position(self):
        start_pos = self.start_item.pos()
        end_pos = self.end_item.pos()
        self.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())


class FlowsheetCanvas(QGraphicsView):
    """Canvas for flowsheet editing."""

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setAcceptDrops(True)
        self.flowsheet_graph = nx.DiGraph()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        pos = self.mapToScene(event.pos())
        unit_type = event.mimeData().text()
        if unit_type == "Mixer":
            unit = Mixer()
            unit.component_name = f"Mixer_{len(self.scene.items()) + 1}"
            item = UnitItem(unit, pos.x(), pos.y())
            self.scene.addItem(item)
            self.flowsheet_graph.add_node(unit.component_name, unit=unit, item=item)
        elif unit_type == "Heater":
            unit = Heater()
            unit.component_name = f"Heater_{len(self.scene.items()) + 1}"
            item = UnitItem(unit, pos.x(), pos.y())
            self.scene.addItem(item)
            self.flowsheet_graph.add_node(unit.component_name, unit=unit, item=item)
        # Add more units as needed


class DesktopApp(QMainWindow):
    """Main desktop application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DWSIMpy Desktop")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QHBoxLayout(central_widget)

        # Toolbar
        toolbar = QWidget()
        toolbar_layout = QVBoxLayout(toolbar)

        self.unit_list = QListWidget()
        self.unit_list.addItem("Mixer")
        self.unit_list.addItem("Heater")
        self.unit_list.itemDoubleClicked.connect(self.start_drag)
        self.unit_list.setDragEnabled(True)
        toolbar_layout.addWidget(self.unit_list)

        solve_button = QPushButton("Solve Flowsheet")
        solve_button.clicked.connect(self.solve_flowsheet)
        toolbar_layout.addWidget(solve_button)

        layout.addWidget(toolbar)

        # Canvas
        self.canvas = FlowsheetCanvas()
        layout.addWidget(self.canvas)

        # Set splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(toolbar)
        splitter.addWidget(self.canvas)
        layout.addWidget(splitter)

    def start_drag(self, item):
        """Start drag operation."""
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(item.text())
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.CopyAction)

    def solve_flowsheet(self):
        """Solve the flowsheet."""
        # Placeholder: implement solver integration
        print("Solving flowsheet...")
        # Use the graph to build flowsheet and solve


def main():
    app = QApplication(sys.argv)
    window = DesktopApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()