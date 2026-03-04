"""
Modern Card-Based Stylesheet for File Exchanger
Clean, professional interface with vibrant accents and clear hierarchy
"""

# Color palette
PRIMARY = "#2563eb"        # Royal blue
PRIMARY_DARK = "#1d4ed8"   # Darker blue
PRIMARY_LIGHT = "#3b82f6"  # Lighter blue

SECONDARY = "#64748b"      # Slate gray
SUCCESS = "#10b981"        # Emerald green
WARNING = "#f59e0b"        # Amber
DANGER = "#ef4444"         # Red

BG_MAIN = "#f1f5f9"        # Light slate background
BG_CARD = "#ffffff"        # White cards
BG_HOVER = "#f8fafc"       # Hover state

TEXT_PRIMARY = "#1e293b"   # Dark slate
TEXT_SECONDARY = "#64748b" # Medium slate
TEXT_MUTED = "#94a3b8"     # Light slate

BORDER = "#e2e8f0"         # Light border
BORDER_FOCUS = "#2563eb"   # Focus border

SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
SHADOW_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"

MODERN_STYLESHEET = f"""
/* ============================================
   GLOBAL STYLES
   ============================================ */

QWidget {{
    background: transparent;
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
}}

/* ============================================
   MAIN WINDOW & DIALOGS
   ============================================ */

QMainWindow {{
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #f8fbff, stop: 0.5 {BG_MAIN}, stop: 1 #eaf3ff
    );
}}

QDialog {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
}}

/* ============================================
   CARDS / CONTAINERS
   ============================================ */

QGroupBox {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    margin-top: 16px;
    padding-top: 16px;
    font-weight: 600;
    font-size: 14px;
    color: {TEXT_PRIMARY};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    top: -10px;
    padding: 4px 12px;
    background-color: {PRIMARY};
    color: white;
    border-radius: 8px;
    font-weight: 600;
}}

/* ============================================
   BUTTONS - PRIMARY
   ============================================ */

QPushButton {{
    background-color: {PRIMARY};
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 14px;
    color: white;
}}

QPushButton:hover {{
    background-color: {PRIMARY_LIGHT};
}}

QPushButton:pressed {{
    background-color: {PRIMARY_DARK};
}}

QPushButton:disabled {{
    background-color: {BORDER};
    color: {TEXT_MUTED};
}}

QPushButton#primaryBtn {{
    background-color: {PRIMARY};
    color: white;
}}

QPushButton#primaryBtn:hover {{
    background-color: {PRIMARY_LIGHT};
}}

/* Secondary buttons */
QPushButton#secondaryBtn, QPushButton#cancelBtn, QPushButton#ghostBtn {{
    background-color: transparent;
    border: 1px solid {BORDER};
    color: {TEXT_PRIMARY};
}}

QPushButton#secondaryBtn:hover, QPushButton#cancelBtn:hover, QPushButton#ghostBtn:hover {{
    background-color: {BG_HOVER};
    border-color: {TEXT_SECONDARY};
}}

QPushButton#accentBtn {{
    background-color: #eaf2ff;
    border: 1px solid #bfdbfe;
    color: {PRIMARY_DARK};
}}

QPushButton#accentBtn:hover {{
    background-color: #dbeafe;
}}

/* Icon buttons */
QPushButton#refreshBtn, QPushButton#iconBtn {{
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    padding: 0;
    border-radius: 8px;
    font-size: 18px;
}}

/* Success button */
QPushButton#successBtn {{
    background-color: {SUCCESS};
}}

QPushButton#successBtn:hover {{
    background-color: #059669;
}}

/* Danger button */
QPushButton#dangerBtn {{
    background-color: {DANGER};
}}

QPushButton#dangerBtn:hover {{
    background-color: #dc2626;
}}

/* Table action buttons */
QTableWidget QPushButton {{
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    border-radius: 6px;
    min-width: 80px;
}}

QTableWidget QPushButton#downloadBtn {{
    background-color: {PRIMARY};
}}

QTableWidget QPushButton#downloadBtn:hover {{
    background-color: {PRIMARY_LIGHT};
}}

QTableWidget QPushButton#ackBtn {{
    background-color: {SUCCESS};
}}

QTableWidget QPushButton#ackBtn:hover {{
    background-color: #059669;
}}

/* ============================================
   INPUT FIELDS
   ============================================ */

QLineEdit {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    color: {TEXT_PRIMARY};
    selection-background-color: {PRIMARY_LIGHT};
}}

QLineEdit:focus {{
    border: 2px solid {BORDER_FOCUS};
    padding: 11px 15px;  /* Compensate for border change */
}}

QLineEdit:disabled {{
    background-color: {BG_HOVER};
    color: {TEXT_MUTED};
}}

QLineEdit::placeholder {{
    color: {TEXT_MUTED};
}}

/* ============================================
   TEXT EDIT / TEXTAREA
   ============================================ */

QTextEdit {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    color: {TEXT_PRIMARY};
    selection-background-color: {PRIMARY_LIGHT};
}}

QTextEdit:focus {{
    border: 2px solid {BORDER_FOCUS};
    padding: 11px 15px;
}}

QTextEdit:disabled {{
    background-color: {BG_HOVER};
    color: {TEXT_MUTED};
}}

/* ============================================
   COMBOBOX
   ============================================ */

QComboBox {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    color: {TEXT_PRIMARY};
    min-height: 44px;
}}

QComboBox:hover {{
    border-color: {TEXT_SECONDARY};
}}

QComboBox:focus {{
    border: 2px solid {BORDER_FOCUS};
    padding: 11px 15px;
}}

QComboBox::drop-down {{
    border: none;
    width: 32px;
    padding-right: 8px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {TEXT_SECONDARY};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 4px;
    selection-background-color: {PRIMARY_LIGHT};
    selection-color: white;
    outline: none;
}}

QComboBox QAbstractItemView::item {{
    min-height: 40px;
    padding: 8px 12px;
    border-radius: 6px;
    margin: 2px;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: {BG_HOVER};
}}

QComboBox QAbstractItemView::item:selected {{
    background-color: {PRIMARY};
    color: white;
}}

/* ============================================
   SPINBOX
   ============================================ */

QSpinBox {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 14px;
    color: {TEXT_PRIMARY};
    min-height: 44px;
}}

QSpinBox:focus {{
    border: 2px solid {BORDER_FOCUS};
    padding: 9px 15px;
}}

QSpinBox::up-button, QSpinBox::down-button {{
    border: none;
    background-color: {BG_HOVER};
    width: 28px;
    border-radius: 6px;
    margin: 2px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {BORDER};
}}

QSpinBox::up-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 6px solid {TEXT_PRIMARY};
    margin-bottom: 2px;
}}

QSpinBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {TEXT_PRIMARY};
    margin-top: 2px;
}}

/* ============================================
   TABLES
   ============================================ */

QTableWidget {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    gridline-color: {BORDER};
    selection-background-color: {PRIMARY_LIGHT};
    selection-color: white;
    outline: none;
}}

QTableWidget::item {{
    padding: 12px;
    border-bottom: 1px solid {BORDER};
}}

QTableWidget::item:hover {{
    background-color: {BG_HOVER};
}}

QTableWidget::item:selected {{
    background-color: {PRIMARY};
    color: white;
}}

QHeaderView::section {{
    background-color: {BG_HOVER};
    color: {TEXT_SECONDARY};
    padding: 14px 16px;
    border: none;
    border-bottom: 2px solid {BORDER};
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QHeaderView::section:first {{
    border-top-left-radius: 12px;
}}

QHeaderView::section:last {{
    border-top-right-radius: 12px;
}}

QHeaderView::section:hover {{
    background-color: {BORDER};
}}

QTableCornerButton::section {{
    background-color: {BG_HOVER};
    border: none;
    border-bottom: 2px solid {BORDER};
}}

/* Scrollbars */
QScrollBar:vertical {{
    background-color: transparent;
    width: 10px;
    border-radius: 5px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {BORDER};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {TEXT_SECONDARY};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 10px;
    border-radius: 5px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {BORDER};
    border-radius: 5px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {TEXT_SECONDARY};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ============================================
   TABS
   ============================================ */

QTabWidget::pane {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 0;
}}

QTabBar::tab {{
    background-color: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 14px 24px;
    margin-right: 4px;
    font-weight: 500;
    color: {TEXT_SECONDARY};
}}

QTabBar::tab:hover {{
    color: {TEXT_PRIMARY};
    background-color: {BG_HOVER};
    border-radius: 8px 8px 0 0;
}}

QTabBar::tab:selected {{
    color: {PRIMARY};
    border-bottom: 3px solid {PRIMARY};
    font-weight: 600;
}}

QTabBar::tab:!selected {{
    margin-bottom: 2px;
}}

/* ============================================
   PROGRESS BAR
   ============================================ */

QProgressBar {{
    background-color: {BG_HOVER};
    border: 1px solid {BORDER};
    border-radius: 8px;
    text-align: center;
    height: 12px;
    color: {TEXT_PRIMARY};
    font-weight: 600;
    font-size: 10px;
}}

QProgressBar::chunk {{
    background-color: {PRIMARY};
    border-radius: 6px;
}}

QProgressBar#successProgress::chunk {{
    background-color: {SUCCESS};
}}

QProgressBar#warningProgress::chunk {{
    background-color: {WARNING};
}}

/* ============================================
   LABELS
   ============================================ */

QLabel {{
    color: {TEXT_PRIMARY};
    background: transparent;
}}

QLabel#titleLabel {{
    font-size: 28px;
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

QLabel#headerLabel {{
    font-size: 20px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}

QLabel#cardTitle {{
    font-size: 16px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}

QLabel#emptyState {{
    font-size: 14px;
    color: {TEXT_MUTED};
    padding: 40px;
}}

/* ============================================
   STATUS BAR
   ============================================ */

QStatusBar {{
    background-color: {BG_CARD};
    border-top: 1px solid {BORDER};
    color: {TEXT_SECONDARY};
    font-size: 13px;
    padding: 4px 16px;
}}

QStatusBar::item {{
    border: none;
}}

QStatusBar QLabel {{
    padding: 4px 12px;
}}

/* ============================================
   MENU BAR
   ============================================ */

QMenuBar {{
    background-color: {BG_CARD};
    border-bottom: 1px solid {BORDER};
    padding: 4px 0;
}}

QMenuBar::item {{
    padding: 8px 16px;
    border-radius: 6px;
    margin: 0 4px;
    background: transparent;
}}

QMenuBar::item:selected {{
    background-color: {BG_HOVER};
}}

QMenuBar::item:pressed {{
    background-color: {BORDER};
}}

QMenu {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px;
}}

QMenu::item {{
    padding: 10px 20px;
    border-radius: 6px;
    margin: 2px 0;
}}

QMenu::item:selected {{
    background-color: {BG_HOVER};
}}

QMenu::separator {{
    height: 1px;
    background-color: {BORDER};
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
    background-color: {TEXT_PRIMARY};
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    color: white;
    font-size: 13px;
}}

/* ============================================
   MESSAGE BOX
   ============================================ */

QMessageBox {{
    background-color: {BG_CARD};
}}

QMessageBox QLabel {{
    color: {TEXT_PRIMARY};
    font-size: 14px;
}}

QMessageBox QPushButton {{
    min-width: 100px;
    padding: 10px 20px;
}}

/* ============================================
   UTILITY CLASSES
   ============================================ */

/* Card container */
QWidget#cardWidget {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 20px;
}}

/* Header section */
QWidget#headerWidget {{
    background-color: {BG_CARD};
    border-bottom: 1px solid {BORDER};
    padding: 20px 24px;
}}

/* Success state */
QWidget#successWidget {{
    background-color: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-radius: 8px;
}}

/* Error state */
QWidget#errorWidget {{
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
}}

/* Warning state */
QWidget#warningWidget {{
    background-color: #fffbeb;
    border: 1px solid #fed7aa;
    border-radius: 8px;
}}
"""
