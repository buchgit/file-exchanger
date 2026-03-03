"""
Glassmorphism stylesheet for File Exchanger
Modern frosted-glass UI with vibrant gradients and depth effects
"""

# Color palette
GLASS_PRIMARY = "rgba(255, 255, 255, 0.1)"
GLASS_SECONDARY = "rgba(255, 255, 255, 0.05)"
GLASS_BORDER = "rgba(255, 255, 255, 0.2)"
GLASS_HOVER = "rgba(255, 255, 255, 0.15)"
GLASS_PRESSED = "rgba(255, 255, 255, 0.2)"

TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "rgba(255, 255, 255, 0.7)"
TEXT_MUTED = "rgba(255, 255, 255, 0.5)"

ACCENT_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2)"
BG_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f0c29, stop:0.5 #302b63, stop:1 #24243e)"
CARD_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255,255,255,0.1), stop:1 rgba(255,255,255,0.05))"

BUTTON_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2)"
BUTTON_HOVER = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c8eee, stop:1 #8b5cbf)"

SUCCESS_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #11998e, stop:1 #38ef7d)"
DANGER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #eb3349, stop:1 #f45c43)"

GLASS_STYLEHEET = f"""
/* ============================================
   GLOBAL STYLES
   ============================================ */

QWidget {{
    background: transparent;
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
    font-size: 14px;
}}

/* ============================================
   MAIN WINDOW & DIALOGS
   ============================================ */

QMainWindow {{
    background: {BG_GRADIENT};
}}

QDialog {{
    background: {BG_GRADIENT};
}}

/* ============================================
   GLASS CARD / CONTAINER
   ============================================ */

QGroupBox {{
    background: {CARD_GRADIENT};
    border: 1px solid {GLASS_BORDER};
    border-radius: 16px;
    margin-top: 20px;
    padding-top: 16px;
    font-weight: 600;
    font-size: 15px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 20px;
    top: 8px;
    padding: 0 12px;
    color: {TEXT_PRIMARY};
    background: {BUTTON_GRADIENT};
    border-radius: 8px;
}}

/* ============================================
   BUTTONS
   ============================================ */

QPushButton {{
    background: {BUTTON_GRADIENT};
    border: 1px solid {GLASS_BORDER};
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 14px;
    color: {TEXT_PRIMARY};
    min-height: 20px;
}}

QPushButton:hover {{
    background: {BUTTON_HOVER};
    border: 1px solid rgba(255, 255, 255, 0.3);
}}

QPushButton:pressed {{
    background: {GLASS_PRESSED};
    padding: 13px 23px 11px 25px;
}}

QPushButton:disabled {{
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: {TEXT_MUTED};
}}

/* Small icon buttons */
QPushButton#refreshBtn, QPushButton#smallBtn {{
    min-width: 28px;
    max-width: 28px;
    min-height: 28px;
    max-height: 28px;
    padding: 0;
    border-radius: 8px;
}}

/* Table buttons */
QTableWidget QPushButton {{
    padding: 8px 16px;
    font-size: 13px;
    border-radius: 8px;
}}

/* ============================================
   INPUT FIELDS
   ============================================ */

QLineEdit {{
    background: {GLASS_PRIMARY};
    border: 1px solid {GLASS_BORDER};
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 14px;
    color: {TEXT_PRIMARY};
    selection-background-color: #667eea;
}}

QLineEdit:focus {{
    border: 1px solid rgba(102, 126, 234, 0.5);
    background: {GLASS_HOVER};
}}

QLineEdit:disabled {{
    background: {GLASS_SECONDARY};
    color: {TEXT_MUTED};
}}

QLineEdit::placeholder {{
    color: {TEXT_MUTED};
}}

/* ============================================
   TEXT EDIT / TEXTAREA
   ============================================ */

QTextEdit {{
    background: {GLASS_PRIMARY};
    border: 1px solid {GLASS_BORDER};
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 14px;
    color: {TEXT_PRIMARY};
    selection-background-color: #667eea;
}}

QTextEdit:focus {{
    border: 1px solid rgba(102, 126, 234, 0.5);
    background: {GLASS_HOVER};
}}

QTextEdit:disabled {{
    background: {GLASS_SECONDARY};
    color: {TEXT_MUTED};
}}

/* ============================================
   COMBOBOX
   ============================================ */

QComboBox {{
    background: {GLASS_PRIMARY};
    border: 1px solid {GLASS_BORDER};
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 14px;
    color: {TEXT_PRIMARY};
}}

QComboBox:hover {{
    background: {GLASS_HOVER};
    border: 1px solid rgba(255, 255, 255, 0.3);
}}

QComboBox:focus {{
    border: 1px solid rgba(102, 126, 234, 0.5);
    background: {GLASS_HOVER};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {TEXT_PRIMARY};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background: rgba(30, 30, 50, 0.95);
    border: 1px solid {GLASS_BORDER};
    border-radius: 12px;
    padding: 8px;
    selection-background-color: #667eea;
    selection-color: {TEXT_PRIMARY};
    outline: none;
}}

QComboBox QAbstractItemView::item {{
    min-height: 40px;
    padding: 8px 12px;
    border-radius: 8px;
    margin: 2px 0;
}}

QComboBox QAbstractItemView::item:hover {{
    background: rgba(102, 126, 234, 0.3);
}}

QComboBox QAbstractItemView::item:selected {{
    background: #667eea;
    color: {TEXT_PRIMARY};
}}

/* ============================================
   SPINBOX
   ============================================ */

QSpinBox {{
    background: {GLASS_PRIMARY};
    border: 1px solid {GLASS_BORDER};
    border-radius: 12px;
    padding: 10px 16px;
    font-size: 14px;
    color: {TEXT_PRIMARY};
}}

QSpinBox:focus {{
    border: 1px solid rgba(102, 126, 234, 0.5);
    background: {GLASS_HOVER};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    border: none;
    background: {GLASS_HOVER};
    width: 24px;
    border-radius: 6px;
    margin: 2px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background: {GLASS_HOVER};
}}

QSpinBox::up-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 6px solid {TEXT_PRIMARY};
}}

QSpinBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {TEXT_PRIMARY};
}}

/* ============================================
   TABLES
   ============================================ */

QTableWidget {{
    background: {GLASS_PRIMARY};
    border: 1px solid {GLASS_BORDER};
    border-radius: 16px;
    gridline-color: rgba(255, 255, 255, 0.1);
    selection-background-color: rgba(102, 126, 234, 0.3);
    selection-color: {TEXT_PRIMARY};
    outline: none;
}}

QTableWidget::item {{
    padding: 10px;
    border-radius: 8px;
}}

QTableWidget::item:hover {{
    background: rgba(255, 255, 255, 0.05);
}}

QTableWidget::item:selected {{
    background: rgba(102, 126, 234, 0.4);
}}

QHeaderView::section {{
    background: {BUTTON_GRADIENT};
    color: {TEXT_PRIMARY};
    padding: 12px 16px;
    border: none;
    border-bottom: 1px solid {GLASS_BORDER};
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    font-weight: 600;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QHeaderView::section:first {{
    border-top-left-radius: 16px;
}}

QHeaderView::section:last {{
    border-top-right-radius: 16px;
    border-right: none;
}}

QHeaderView::section:hover {{
    background: {BUTTON_HOVER};
}}

QTableCornerButton::section {{
    background: {BUTTON_GRADIENT};
    border: none;
    border-bottom: 1px solid {GLASS_BORDER};
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    border-radius: 5px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {GLASS_BORDER};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: rgba(255, 255, 255, 0.3);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    border-radius: 5px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: {GLASS_BORDER};
    border-radius: 5px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background: rgba(255, 255, 255, 0.3);
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ============================================
   TABS
   ============================================ */

QTabWidget::pane {{
    background: {GLASS_PRIMARY};
    border: 1px solid {GLASS_BORDER};
    border-radius: 16px;
    padding: 0;
}}

QTabBar::tab {{
    background: {GLASS_SECONDARY};
    border: 1px solid {GLASS_BORDER};
    border-bottom: none;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    padding: 12px 24px;
    margin-right: 4px;
    font-weight: 500;
    color: {TEXT_SECONDARY};
}}

QTabBar::tab:hover {{
    background: {GLASS_HOVER};
}}

QTabBar::tab:selected {{
    background: {BUTTON_GRADIENT};
    color: {TEXT_PRIMARY};
    border: 1px solid rgba(255, 255, 255, 0.3);
}}

QTabBar::tab:!selected {{
    margin-top: 8px;
}}

/* ============================================
   PROGRESS BAR
   ============================================ */

QProgressBar {{
    background: {GLASS_SECONDARY};
    border: 1px solid {GLASS_BORDER};
    border-radius: 12px;
    text-align: center;
    height: 20px;
    color: {TEXT_PRIMARY};
    font-weight: 600;
    font-size: 12px;
}}

QProgressBar::chunk {{
    background: {BUTTON_GRADIENT};
    border-radius: 10px;
}}

/* ============================================
   CHECKBOX
   ============================================ */

QCheckBox {{
    color: {TEXT_PRIMARY};
    spacing: 10px;
    font-size: 14px;
}}

QCheckBox::indicator {{
    width: 22px;
    height: 22px;
    border-radius: 6px;
    background: {GLASS_PRIMARY};
    border: 1px solid {GLASS_BORDER};
}}

QCheckBox::indicator:hover {{
    border: 1px solid rgba(102, 126, 234, 0.5);
    background: {GLASS_HOVER};
}}

QCheckBox::indicator:checked {{
    background: {BUTTON_GRADIENT};
    border: 1px solid rgba(102, 126, 234, 0.8);
}}

/* ============================================
   LABELS
   ============================================ */

QLabel {{
    color: {TEXT_PRIMARY};
    background: transparent;
}}

QLabel#titleLabel {{
    font-size: 24px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
}}

QLabel#subtitleLabel {{
    font-size: 14px;
    color: {TEXT_SECONDARY};
}}

QLabel#statusLabel {{
    font-size: 13px;
    color: {TEXT_MUTED};
}}

/* ============================================
   STATUS BAR
   ============================================ */

QStatusBar {{
    background: {GLASS_PRIMARY};
    border-top: 1px solid {GLASS_BORDER};
    color: {TEXT_SECONDARY};
    font-size: 13px;
}}

QStatusBar::item {{
    border: none;
}}

/* ============================================
   MENU BAR
   ============================================ */

QMenuBar {{
    background: {GLASS_PRIMARY};
    border-bottom: 1px solid {GLASS_BORDER};
    padding: 4px 0;
}}

QMenuBar::item {{
    padding: 8px 16px;
    border-radius: 8px;
    margin: 0 4px;
    background: transparent;
}}

QMenuBar::item:selected {{
    background: {GLASS_HOVER};
}}

QMenuBar::item:pressed {{
    background: {GLASS_PRESSED};
}}

QMenu {{
    background: rgba(30, 30, 50, 0.98);
    border: 1px solid {GLASS_BORDER};
    border-radius: 12px;
    padding: 8px;
}}

QMenu::item {{
    padding: 10px 20px;
    border-radius: 8px;
    margin: 2px 0;
}}

QMenu::item:selected {{
    background: {GLASS_HOVER};
}}

QMenu::separator {{
    height: 1px;
    background: {GLASS_BORDER};
    margin: 6px 10px;
}}

/* ============================================
   SCROLL AREA
   ============================================ */

QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

/* ============================================
   TOOLTIP
   ============================================ */

QToolTip {{
    background: rgba(30, 30, 50, 0.95);
    border: 1px solid {GLASS_BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}

/* ============================================
   MESSAGE BOX
   ============================================ */

QMessageBox {{
    background: {BG_GRADIENT};
}}

QMessageBox QLabel {{
    color: {TEXT_PRIMARY};
}}

QMessageBox QPushButton {{
    min-width: 100px;
}}
"""
