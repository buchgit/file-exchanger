from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from api import ApiClient, ApiWorker
import config
from ui.admin_widget import AdminWidget
from ui.inbox_widget import InboxWidget
from ui.modern_style import MODERN_STYLESHEET
from ui.send_widget import SendWidget
from ws_thread import WsThread


class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, token: str, user_info: dict, api_client: ApiClient):
        super().__init__()
        self._token = token
        self._user_info = user_info
        self._api = api_client
        self._ws: WsThread | None = None
        self._workers: list[ApiWorker] = []
        self._nav_buttons: list[QPushButton] = []

        self.setWindowTitle(f"File Exchanger - {user_info['username']}")
        self.setMinimumSize(1200, 750)
        self.setStyleSheet(MODERN_STYLESHEET)

        self._build_ui()
        self._build_menu()
        self._start_ws()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central_widget = QWidget()
        central_widget.setObjectName("cardWidget")
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = self._build_header()
        main_layout.addWidget(header)

        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        content_layout.addWidget(sidebar)

        main_content = QWidget()
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.setContentsMargins(24, 24, 24, 24)
        main_content_layout.setSpacing(20)

        self._tabs = QTabWidget()
        self._tabs.setObjectName("contentTabs")
        self._tabs.currentChanged.connect(self._sync_nav_state)

        self._inbox = InboxWidget(self._api, self._token)
        self._inbox.request_logout.connect(self._handle_401)
        self._tabs.addTab(self._inbox, "Inbox")

        self._send = SendWidget(self._api, self._token, self._user_info.get("id", 0))
        self._send.request_logout.connect(self._handle_401)
        self._tabs.addTab(self._send, "Send")

        if self._user_info.get("is_admin"):
            self._admin = AdminWidget(self._api, self._token, self._user_info.get("id", 0))
            self._admin.request_logout.connect(self._handle_401)
            self._tabs.addTab(self._admin, "Admin")
        else:
            self._admin = None

        main_content_layout.addWidget(self._tabs)
        content_layout.addWidget(main_content, 1)
        main_layout.addWidget(content_widget, 1)

        self._ws_status_label = QLabel("WS: connecting...")
        self._ws_status_label.setStyleSheet("color: #f59e0b; font-weight: 600;")
        status_bar = QStatusBar()
        status_bar.addPermanentWidget(self._ws_status_label)
        self.setStatusBar(status_bar)

        self.setCentralWidget(central_widget)
        self._sync_nav_state(0)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("headerWidget")
        header.setFixedHeight(80)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 16, 24, 16)

        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        app_title = QLabel("File Exchanger")
        app_title.setObjectName("titleLabel")
        app_title.setStyleSheet("font-size: 24px; font-weight: 700; color: #1e293b;")

        user_subtitle = QLabel(f"Logged in as: {self._user_info['username']}")
        user_subtitle.setObjectName("subtitleLabel")
        user_subtitle.setStyleSheet("font-size: 13px; color: #64748b;")

        title_layout.addWidget(app_title)
        title_layout.addWidget(user_subtitle)

        layout.addWidget(title_container)
        layout.addStretch()
        layout.addWidget(self._build_user_badge())
        return header

    def _build_user_badge(self) -> QWidget:
        badge = QFrame()
        badge.setFrameStyle(QFrame.Shape.Box)
        badge.setStyleSheet(
            """
            QFrame {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 8px 16px;
            }
            """
        )
        badge_layout = QHBoxLayout(badge)
        badge_layout.setContentsMargins(12, 8, 12, 8)
        badge_layout.setSpacing(10)

        initial = self._user_info["username"][0].upper() if self._user_info.get("username") else "U"
        avatar = QLabel(initial)
        avatar.setStyleSheet(
            """
            QLabel {
                min-width: 26px;
                max-width: 26px;
                min-height: 26px;
                max-height: 26px;
                border-radius: 13px;
                background-color: #2563eb;
                color: white;
                font-size: 13px;
                font-weight: 700;
                qproperty-alignment: AlignCenter;
            }
            """
        )

        details = QWidget()
        details_layout = QVBoxLayout(details)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(0)

        username = QLabel(self._user_info["username"])
        username.setStyleSheet("font-weight: 600; font-size: 14px; color: #1e293b;")

        role = QLabel("Administrator" if self._user_info.get("is_admin") else "User")
        role.setStyleSheet("font-size: 12px; color: #64748b;")

        details_layout.addWidget(username)
        details_layout.addWidget(role)

        badge_layout.addWidget(avatar)
        badge_layout.addWidget(details)
        return badge

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setFixedWidth(120)
        sidebar.setStyleSheet(
            """
            QWidget {
                background-color: #f8fafc;
                border-right: 1px solid #e2e8f0;
            }
            """
        )
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        nav_buttons = [("Inbox", 0), ("Send", 1)]
        if self._user_info.get("is_admin"):
            nav_buttons.append(("Admin", 2))

        for label, tab_index in nav_buttons:
            btn = QPushButton(label)
            btn.setFixedHeight(46)
            btn.setCheckable(True)
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    border: 1px solid transparent;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 600;
                    color: #64748b;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #e2e8f0;
                    color: #2563eb;
                }
                QPushButton:checked {
                    background-color: #dbeafe;
                    color: #2563eb;
                    border: 1px solid #2563eb;
                }
                """
            )
            btn.clicked.connect(lambda checked, i=tab_index: self._tabs.setCurrentIndex(i))
            self._nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        host_label = QLabel(config.SERVER_HOST)
        host_label.setObjectName("statusLabel")
        host_label.setWordWrap(True)
        host_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(host_label)

        return sidebar

    def _build_menu(self) -> None:
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        help_menu = menubar.addMenu("Help")

        change_pw_action = file_menu.addAction("Change Password")
        change_pw_action.triggered.connect(self._on_change_password)

        file_menu.addSeparator()

        logout_action = file_menu.addAction("Log Out")
        logout_action.triggered.connect(self._on_logout)

        quit_action = file_menu.addAction("Quit")
        quit_action.triggered.connect(self._on_quit)

        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self._on_about)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _sync_nav_state(self, tab_index: int) -> None:
        for idx, button in enumerate(self._nav_buttons):
            button.setChecked(idx == tab_index)

    # ------------------------------------------------------------------
    # WebSocket
    # ------------------------------------------------------------------

    def _start_ws(self) -> None:
        self._ws = WsThread(self._token)
        self._ws.new_file.connect(self._on_new_file)
        self._ws.connected.connect(self._on_ws_connected)
        self._ws.disconnected.connect(self._on_ws_disconnected)
        self._ws.error.connect(lambda _: self._ws_status_label.setText("WS: error"))
        self._ws.start()

    def _stop_ws(self) -> None:
        if self._ws is not None:
            self._ws.stop()
            self._ws = None

    def _on_ws_connected(self) -> None:
        self._ws_status_label.setText("WS: connected")
        self._ws_status_label.setStyleSheet("color: #10b981; font-weight: 600;")

    def _on_ws_disconnected(self) -> None:
        self._ws_status_label.setText("WS: reconnecting...")
        self._ws_status_label.setStyleSheet("color: #f59e0b; font-weight: 600;")

    def _on_new_file(self, data: dict) -> None:
        self._inbox._on_new_file_notification(data)

    # ------------------------------------------------------------------
    # Menu slots
    # ------------------------------------------------------------------

    def _on_change_password(self) -> None:
        from ui.main_window import _ChangePasswordDialog

        dialog = _ChangePasswordDialog(self._api, self._token, parent=self)
        dialog.setStyleSheet(MODERN_STYLESHEET)
        dialog.exec()

    def _on_logout(self) -> None:
        self._stop_ws()
        config.clear_session()
        self.hide()
        self.logout_requested.emit()

    def _on_quit(self) -> None:
        self._stop_ws()
        QApplication.quit()

    def _on_about(self) -> None:
        QMessageBox.about(
            self,
            "About File Exchanger",
            "<h3>File Exchanger</h3>"
            "<p>Version 1.0.0</p>"
            "<p>A secure file exchange application with real-time notifications.</p>"
            "<p>Built with FastAPI and PyQt6</p>",
        )

    # ------------------------------------------------------------------
    # 401 handler
    # ------------------------------------------------------------------

    def _handle_401(self) -> None:
        self._stop_ws()
        config.clear_session()
        self.hide()
        self.logout_requested.emit()

    # ------------------------------------------------------------------
    # Close event
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        if self._ws is not None:
            self._ws.stop()
            self._ws.wait(3000)
        event.accept()
