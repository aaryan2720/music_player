from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction,QMessageBox, QFileDialog, QListWidgetItem
from PyQt5.QtMultimedia import QMediaPlayer,QMediaContent
from music import Ui_MusicApp
from db_functions import create_tables,delete_db_table,get_playlist_tables,delete_all_songs_from_db_table,delete_songs_from_db_table,add_songs_to_database_table, fetch_all_songs_from_db
from PyQt5 import QtWidgets ,QtGui
import os
from playlist_popup import PlaylistDialog
import songs
import time
import random

def create_db_dir():
    os.mkdir('.dbs', exist_ok= True)
class ModernMusicPlayer(QMainWindow, Ui_MusicApp):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Remove default title bar
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Create player
        self.player = QMediaPlayer()
        self.initial_volume = 20
        self.player.setVolume(self.initial_volume)
        self.volume_dial.setValue(self.initial_volume)
        self.volume_label.setText(f"{self.initial_volume}")

        # Initial position of the window
        self.initialPosition = self.pos()

        # Timer slider
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_slider)
        self.timer.start(1000)

        global slide_index
        slide_index = 0

        # Connections
        self.player.mediaStatusChanged.connect(self.song_finished)
        self.player.mediaChanged.connect(self.slideshow)
        self.music_slider.sliderMoved.connect(self.set_player_position)
        self.add_songs_btn.clicked.connect(self.add_songs)
        self.play_btn.clicked.connect(self.play_songs)
        self.pause_btn.clicked.connect(self.pause_and_unpause)
        self.stop_btn.clicked.connect(self.stop_song)
        self.next_btn.clicked.connect(self.next_song)
        self.previous_btn.clicked.connect(self.previous_song)
        self.volume_dial.valueChanged.connect(self.set_volume)
        self.shuffle_songs_btn.clicked.connect(self.toggle_shuffle)
        self.loop_one_btn.clicked.connect(self.toggle_loop)
        self.delete_selected_btn.clicked.connect(self.remove_selected_song)
        self.delete_all_songs_btn.clicked.connect(self.remove_all_songs)
        self.song_list_btn.clicked.connect(self.switch_to_song_tab)
        self.playlists_btn.clicked.connect(self.switch_to_playlist_tab)
        self.favourites_btn.clicked.connect(self.switch_to_favorites_tab)
        self.actionPlay.triggered.connect(self.play_songs)
        self.actionPause_Unpause.triggered.connect(self.play_songs)
        self.actionPlay.triggered.connect(self.pause_and_unpause)
        self.actionNext.triggered.connect(self.next_song)
        self.actionPrevious.triggered.connect(self.previous_song)
        self.actionStop.triggered.connect(self.stop_song)
        self.add_to_fav_btn.clicked.connect(self.add_song_to_favourites)
        self.delete_all_favourites_btn.clicked.connect(self.remove_all_songs_from_favorites)
        self.delete_selected_favourite_btn.clicked.connect(self.remove_songs_from_favorites)
        self.actionAdd_all_to_Favouries.triggered.connect(self.add_song_to_favourites)
        self.actionAdd_Selected_to_Favourites.triggered.connect(self.add_song_to_favourites)
        self.actionRemove_Selected_Favourite.triggered.connect(self.remove_songs_from_favorites)
        self.actionRemove_All_Favourites.triggered.connect(self.remove_all_songs_from_favorites)
        
        self.playlists_listWidget.itemDoubleClicked.connect(self.show_playlist_contents)
        self.remove_selected_playlist_btn.clicked.connect(self.delete_playlist)
        self.remove_all_playlists_btn.clicked.connect(self.delete_all_playlist)
        self.add_to_playlist_btn.clicked.connect(self.add_all_current_songs_to_a_playlist)
        self.new_playlist_btn.clicked.connect(self.new_playlist)

        try:

            self.load_selected_playlist_btn.clicked.connect(
                lambda: self.load_playlists_songs_to_current_list(self.playlists_listWidget.currentItem().text())
            )
            self.actionLoad_Selected_Playlist.triggered.connect(
                    self.load_selected_playlist_btn.clicked.connect(
                    lambda: self.load_playlists_songs_to_current_list(self.playlists_listWidget.currentItem().text())
                )
            )
        except:
            pass

        self.actionSave_all_to_a_playlist.triggered.connect(self.add_all_current_songs_to_a_playlist)
        self.actionSave_Selected_to_a_Playlist.triggered.connect(self.add_a_song_to_a_playlist)
        self.actionDelete_All_Playlists.triggered.connect(self.delete_all_playlist)
        self.actionDelete_Selected_Playlist.triggered.connect(self.delete_playlist)
        self.show()
    



        # Set default values for flags
        self.stopped = False
        self.looped = False
        self.is_shuffled = False

        self.playlist_context_menu()
        self.loaded_songs_context_menu()
        self.favorite_songs_context_menu()

        # Database stuff
        create_tables('favourites')
        self.load_playlists()
        self.load_favourites_into_app()

    def set_player_position(self):
        if not self.stopped and self.player.state() == QMediaPlayer.PlayingState:
            self.player.setPosition(self.music_slider.value())

    def song_finished(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.next_song()

    def move_slider(self):
        if self.stopped:
            return
        elif self.player.state() == QMediaPlayer.PlayingState:
            self.music_slider.setMinimum(0)
            self.music_slider.setMaximum(self.player.duration())
            slider_position = self.player.position()
            self.music_slider.setValue(slider_position)

            current_time = time.strftime("%H:%M:%S", time.gmtime(self.player.position() / 1000))
            song_duration = time.strftime("%H:%M:%S", time.gmtime(self.player.duration() / 1000))

            self.time_label.setText(f"{current_time}/{song_duration}")

    def add_songs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, caption="Add songs to the app", directory="C:\\",
            filter="Supported Files (*.mp3; *.mpeg; *.ogg; *.m4a; *.MP3;*.wma;*.acc;*.amr)"
        )
        if files:
            for file in files:
                songs.current_song_list.append(file)
                item = QListWidgetItem(QIcon(":/img/utils/images/MusicListItem.png"), os.path.basename(file))
                self.loaded_songs_listWidget.addItem(item)

    def play_songs(self):
        try:
            global stopped
            stopped = False
            if self.stackedWidget.currentIndex() == 0:

                current_selection = self.loaded_songs_listWidget.currentRow()
                current_song = songs.current_song_list[current_selection]
            
            elif self.stackedWidget.currentIndex() == 2:
                current_selection = self.favourites_listWidget.currentRow()
                current_song = songs.favorites_songs_list[current_selection]


            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()

            self.current_song_name.setText(f"{os.path.basename(current_song)}")
            self.current_song_path.setText(f"{os.path.dirname(current_song)}")

        except Exception as e:
            print(f"play song error: {e}")

    def pause_and_unpause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def stop_song(self):
        try:
            self.player.stop()
        except Exception as f:
            print(f"stop song error: {f}")

    def set_volume(self):
        try:
            self.initial_volume = self.volume_dial.value()
            self.player.setVolume(self.initial_volume)
        except Exception as g:
            print(f"volume error: {g}")

    def default_next(self):
        try:
            if self.stackedWidget.currentIndex() == 0:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().path()[1:]
                song_index = songs.current_song_list.index(current_song_url)
                next_index = (song_index + 1) % len(songs.current_song_list)
                next_song = songs.current_song_list[next_index]
                self.loaded_songs_listWidget.setCurrentRow(next_index)

            
            elif self.stackedWidget.currentIndex() == 2:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().path()[1:]
                song_index = songs.favorites_songs_list.index(current_song_url)
                next_index = (song_index + 1) % len(songs.favorites_songs_list)
                next_song = songs.favorites_songs_list[next_index]
                self.favourites_listWidget.setCurrentRow(next_index)
            
            
            self.play_next_song(next_song, next_index)



        except Exception as h:
            print(f"default next error: {h}")

    def looped_next(self):
        try:
            current_media = self.player.media()
            current_song_url = current_media.canonicalUrl().path()[1:]

            song_index = songs.current_song_list.index(current_song_url)
            self.play_next_song(current_song_url, song_index)

        except Exception as h:
            print(f"looped next error: {h}")

    def shuffled_next(self):
        try:
            if self.stackedWidget.currentIndex == 0:
                next_index = random.randint(0, len(songs.current_song_list) - 1)
                next_song = songs.current_song_list[next_index]
                self.loaded_songs_listWidget.setCurrentRow(next_index)

            elif self.stackedWidget.currentIndex == 2:
                next_index = random.randint(0, len(songs.favorites_songs_list) - 1)
                next_song = songs.favorites_songs_list[next_index]
                self.favourites_listWidget.setCurrentRow(next_index)


            
            self.play_next_song(next_song, next_index)

        except Exception as h:
            print(f"shuffled next error: {h}")

    def play_next_song(self, next_song, next_index):
        song_url = QMediaContent(QUrl.fromLocalFile(next_song))
        self.player.setMedia(song_url)
        self.player.play()
        self.loaded_songs_listWidget.setCurrentRow(next_index)

        self.current_song_name.setText(f"{os.path.basename(next_song)}")
        self.current_song_path.setText(f"{os.path.dirname(next_song)}")

    def next_song(self):
        try:
            if self.is_shuffled:
                self.shuffled_next()
            elif self.looped:
                self.looped_next()
            else:
                self.default_next()

        except Exception as h:
            print(f"Next song error: {h}")

    def previous_song(self):
        try:
            current_media = self.player.media()
            current_song_url = current_media.canonicalUrl().path()[1:]

            song_index = songs.current_song_list.index(current_song_url)
            previous_index = (song_index - 1) % len(songs.current_song_list)
            previous_song = songs.current_song_list[previous_index]
            self.play_next_song(previous_song, previous_index)

        except Exception as i:
            print(f"previous song error: {i}")

    def toggle_loop(self):
        try:
            self.looped = not self.looped
            self.shuffle_songs_btn.setEnabled(not self.looped)

        except Exception as h:
            print(f"looping song error: {h}")

    def toggle_shuffle(self):
        try:
            self.is_shuffled = not self.is_shuffled
            self.loop_one_btn.setEnabled(not self.is_shuffled)

        except Exception as h:
            print(f"Shuffling song error: {h}")

    def remove_selected_song(self):
        try:
            if self.loaded_songs_listWidget.count() == 0:
                QMessageBox.information(
                    self, 'Remove Selected Song ',
                    'Playlist is empty'
                )
                return

            current_index = self.loaded_songs_listWidget.currentRow()
            self.loaded_songs_listWidget.takeItem(current_index)
            songs.current_song_list.pop(current_index)
        except Exception as e:
            print(f"Error in removing selected Song: {e}")

    def remove_all_songs(self):
        try:
            if self.loaded_songs_listWidget.count() == 0:
                QMessageBox.information(
                    self, 'Remove all Songs ',
                    'Playlist is empty'
                )
                return
            question = QMessageBox.question(
                self, 'Remove all songs',
                'This action will remove all songs from the list\n'
                'Continue?',
                QMessageBox.Yes | QMessageBox.Cancel
            )
            if question == QMessageBox.Yes:
                self.stop_song()
                self.loaded_songs_listWidget.clear()
                songs.current_song_list.clear()
        except Exception as e:
            print(f"Error in removing all song: {e}")

    def switch_to_favorites_tab(self):
        self.stackedWidget.setCurrentIndex(2)

    def switch_to_playlist_tab(self):
        self.stackedWidget.setCurrentIndex(1)

    def switch_to_song_tab(self):
        self.stackedWidget.setCurrentIndex(0)

    def load_favourites_into_app(self):
        favorites_songs = fetch_all_songs_from_db('favourites')
        songs.favorites_songs_list.clear()
        self.favourites_listWidget.clear()

        for favourite in favorites_songs:
            songs.favorites_songs_list.append(favourite)
            self.favourites_listWidget.addItem(
                QListWidgetItem(
                    QIcon(":/img/utils/images/like.png"),
                    os.path.basename(favourite)
                )
                )

    def add_song_to_favourites(self):
        current_index = self.loaded_songs_listWidget.currentRow()
        if current_index is None:
            QMessageBox.information(
                self, 'Add songs to favourites',
                'Select a song to add to favorites'
            )
            return
        try:
            song = songs.current_song_list[current_index]
            add_songs_to_database_table(song=f"{song}", table='favourites')
            self.load_favourites_into_app()
        except Exception as e:
            print(f"Adding song to favorites error: {e}")

    #remove songs from favorites
    def remove_songs_from_favorites(self):
        if self.favourites_listWidget.count() == 0:
            QMessageBox.information(
                self, 'Remove song from favorites ',
                'Favourites list is empty'
            )
            return

        current_index = self.favourites_listWidget.currentRow()
        if current_index is None:
            QMessageBox.information(
                self, 'Remove song from favorites',
                'Select a song to remove'
            )
            return

        try:
            song = songs.favorites_songs_list[current_index]
            delete_songs_from_db_table(song=f"{song}", table="favourites")
            self.load_favourites_into_app()

        except Exception as e:
            print(f"Removing favorite error: {e}")
    
     #remove all songs from favorites
    def remove_all_songs_from_favorites(self):
        if self.favourites_listWidget.count() == 0:
            QMessageBox.information(
                self, 'Remove song from favorites ',
                'Favourites list is empty'
            )
            return
        question = QMessageBox.question(
            self, 'Remove all favorite songs from ?',
            'This action will remove all favorite songs from favorites.\nContinue?',
            QMessageBox.Yes | QMessageBox.Cancel

        )
        if question == QMessageBox.Yes:
            try:
                delete_all_songs_from_db_table(table="favourites")
                self.load_favourites_into_app()

            except Exception as e:
                print(f"Removing favorite error: {e}")

    #playist function 
    # load playlist into app 
    def load_playlists(self):
        playlists = get_playlist_tables()
        playlists.remove('favourites')
        self.playlists_listWidget.clear()
        for playlist in playlists:
            self.playlists_listWidget.addItem(
                QListWidgetItem(
                    QIcon(":/img/utils/images/dialog-music.png"),
                    playlist
                )
            )
    #create a new playlist
    def new_playlist(self):
     try:
        existing = get_playlist_tables()
        name,_ = QtWidgets.QInputDialog.getText(
            self, "Create a new playlist,",
            "Enter the name of your new playlist:"
        )
        if name.strip() == "":
            QMessageBox.information(self, 'Name error ', 'Playlist name cannot be empty',)
            return
        else:
            if name not in existing:
                create_tables(f"{name}")
                self.load_playlists()
            elif name in existing :
                caution = QMessageBox.question(
            self, 'replace playlist',
            f'A playlist with name "{name} "already exists.\nDo you want to replace it?',
            QMessageBox.Yes | QMessageBox.No
                )
                if caution == QMessageBox.Yes:
                    delete_db_table(f'{name}')
                    create_tables(f'{name}')
                    self.load_playlists()

     except Exception as e:
        print(f"playlist error: {e}")
    

    #delete a playlist
    def delete_playlist(self):
        playlist = self.playlists_listWidget.currentItem().text()
        try :
            delete_db_table(playlist)
        except Exception as e :
            print(f"Deleting playlist error: {e}")
        
        finally:
            self.load_playlists()
        
    #delette all playlist
    def delete_all_playlist(self):
        playlists = get_playlist_tables()
        playlists.remove('favourites')
        caution  = QMessageBox.question(
            self, 'delete all playlist  ?',
            'This action will remove all playlist from this menu.\nContinue?',
            QMessageBox.Yes | QMessageBox.Cancel

        )
        if caution == QMessageBox.Yes:
            try:
                for playlist in playlists:
                    delete_db_table(playlist)
            except Exception as e:
                print(f"deleting all playlist from this menu error: {e}")
            finally:
                self.load_playlists()
    
    #adding a song to a playlist
    def add_a_song_to_a_playlist(self):
        options = get_playlist_tables()
        options.remove('favourites')
        options.insert(0,'--Click to Select--')
        playlist, _ = QtWidgets.QInputDialog.getItem(
            self, 'Add song to playlist',
            'choose desired playlist', options,editable=False
        )

        if playlist == '--Click to Select--':
            QMessageBox.information(
                self, "Add song to playlist", "No playlist selected"

            )
            return
        try:
            current_index = self.loaded_songs_listWidget.currentRow()
            song = songs.current_song_list[current_index]

        except Exception as e:
           QMessageBox.information(self, ' Unsuccessful', 'No song selected')
           return
        add_songs_to_database_table(
            song=song, table=playlist
        )
        self.load_playlists()
    
    def add_all_current_songs_to_a_playlist(self):
        options = get_playlist_tables()
        options.remove('favourites')
        options.insert(0, '--Click to Select--')
        playlist, _ = QtWidgets.QInputDialog.getItem(
            self, 'Add songs to playlist',
            'Choose the desired playlist', options, editable=False
        )

        if playlist == '--Click to Select--':
            QMessageBox.information(
                self, "Add songs to playlist", "No playlist selected"
            )
            return

        selected_items = self.loaded_songs_listWidget.selectedItems()

        if not selected_items:
            QMessageBox.information(
                self, 'Add songs to playlist',
                "No songs selected in the loaded songs list"
            )
            return

        try:
            for item in selected_items:
                current_index = self.loaded_songs_listWidget.row(item)
                song = songs.current_song_list[current_index]
                add_songs_to_database_table(song=song, table=playlist)
            self.load_playlists()
        except Exception as e:
            print(f"Error adding songs to playlist: {e}")

    def add_currently_playing_to_a_playlist(self):
        if not self.player.state() == QMediaPlayer.PlayingState:
            QMessageBox.information(
                self, 'Add currently playing song to playlist',
                'No song is playing in queue'
            )
            return
        options = get_playlist_tables()
        options.remove('favourites')
        options.insert(0,'--Click to Select--')
        playlist, _ = QtWidgets.QInputDialog.getItem(
            self, 'Add song to playlist',
            'choose desired playlist', options,editable=False
        )

        if playlist == '--Click to Select--':
            QMessageBox.information(
                self, "Add song to playlist", "No playlist selected"

            )
            return
        current_media = self.player.media()
        song = current_media.canonicalUrl().path()[1:]
        add_songs_to_database_table(song=song, table=playlist)
        self.load_playlists()

    def load_playlists_songs_to_current_list(self, playlist):
        try :
            playlist_songs = fetch_all_songs_from_db(playlist)
            if len(playlist_songs) == 0:
                QMessageBox.information(
                    self, 'load playlist song',
                    'playlist is empty'

                )
                return
            for song in playlist_songs:
                songs.current_song_list.append(song)
                self.loaded_songs_listWidget.addItem(
                    QListWidgetItem(
                        QIcon(':/img/utils/images/MusicListItem.png'),
                        os.path.basename(song)
                    )
                )
        except Exception as e:
            print(f"loading song from :{playlist}:{e}")

    #show playlist contents
    def show_playlist_contents(self):
     try:
        print("show_playlist_contents called")
        current_item = self.playlists_listWidget.currentItem()
        if current_item:
            playlist = current_item.text()
            print(f"Selected playlist: {playlist}")
            songs = fetch_all_songs_from_db(playlist)
            print(f"Songs in playlist: {songs}")
            playlist_dialog = PlaylistDialog(songs, f'{playlist}')
            print("PlaylistDialog created")
            playlist_dialog.exec_()
        else:
            print("No playlist selected.")
     except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"show playlist contents error: {e}")



    #context menu
    def playlist_context_menu(self):
        self.playlists_listWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.playlists_listWidget.addAction(self.actionLoad_Selected_Playlist)
        separator = QAction(self)
        separator.setSeparator(True)
        self.playlists_listWidget.addAction(self.actionDelete_Selected_Playlist)
        self.playlists_listWidget.addAction(self.actionDelete_All_Playlists)
    
    def loaded_songs_context_menu(self):
        self.loaded_songs_listWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.loaded_songs_listWidget.addAction(self.actionPlay)
        self.loaded_songs_listWidget.addAction(self.actionPause_Unpause)
        separator = QAction(self)
        separator.setSeparator(True)
        self.loaded_songs_listWidget.addAction(self.actionPrevious)
        self.loaded_songs_listWidget.addAction(self.actionNext)
        self.loaded_songs_listWidget.addAction(self.actionStop)
        separator = QAction(self)
        separator.setSeparator(True)
        self.loaded_songs_listWidget.addAction(self.actionAdd_Selected_to_Favourites)
        self.loaded_songs_listWidget.addAction(self.actionAdd_all_to_Favouries)
        separator = QAction(self)
        separator.setSeparator(True)
        self.loaded_songs_listWidget.addAction(self.actionSave_Selected_to_a_Playlist)
        self.loaded_songs_listWidget.addAction(self.actionSave_all_to_a_playlist)
    
    def favorite_songs_context_menu(self):
        self.favourites_listWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.favourites_listWidget.addAction(self.actionRemove_Selected_Favourite)
        self.favourites_listWidget.addAction(self.actionRemove_All_Favourites)

    def slideshow(self):
        images_path = os.path.join(os.getcwd(), os.path.join('utils', 'bg_imgs'))
        images = os.listdir(images_path)
        images.remove('bg_overlay.png')
        
        global slide_index

        if slide_index < len(images):
            next_slide = images[slide_index]
            next_image = QtGui.QPixmap(os.path.join(images_path, f"{next_slide}"))
            self.background_image.setPixmap(next_image)
            slide_index += 1
        else:
            slide_index = 0  # Reset slide_index to loop through the images again


        
    

