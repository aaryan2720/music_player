from PyQt5 import QtWidgets, QtGui, QtCore

class PlaylistDialog(QtWidgets.QDialog):
    def __init__(self, data, title, parent=None):
        super().__init__(parent)
        self.data = data
        self.title = title
        self.setWindowTitle(f'Songs in {self.title}')
        self.setGeometry(550, 200, 500, 300)
        self.setMinimumSize(QtCore.QSize(500, 300))
        self.setMinimumSize(QtCore.QSize(500, 300))

        self.playlists_listWidget = QtWidgets.QListWidget(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.playlists_listWidget)
        
        # Iterate through data and add each item to the QListWidget
        for item in data:
            list_item = QtWidgets.QListWidgetItem(item)
            self.playlists_listWidget.addItem(list_item)
