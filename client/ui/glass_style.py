"""
Forge UI stylesheet for File Exchanger
Dark navy / charcoal with electric teal accent — compact, sharp, professional
"""

# ── Palette ────────────────────────────────────────────────────────────────
BG_APP      = "#0C1018"
BG_SURFACE  = "#141B26"
BG_CARD     = "#1B2540"
BG_INPUT    = "#090D15"

BORDER      = "#28374A"
BORDER_LT   = "#3A5070"

ACCENT      = "#2ECBAB"
ACCENT_HV   = "#3FDFBF"
ACCENT_DIM  = "rgba(46, 203, 171, 0.12)"
ACCENT_RING = "rgba(46, 203, 171, 0.40)"

SUCCESS     = "#22C55E"
DANGER      = "#E84C3D"
DANGER_DIM  = "rgba(232, 76, 61, 0.12)"
WARNING     = "#F59E0B"

TEXT        = "#DCE6F0"
TEXT2       = "#7A8FA8"
TEXT_MUTED  = "#4A5C6D"

GLASS_STYLEHEET = f"""
/* ═══════════════════════════════════════════
   GLOBAL
   ═══════════════════════════════════════════ */

QWidget {{
    background: transparent;
    color: {TEXT};
    font-family: 'Segoe UI', 'SF Pro Text', -apple-system, sans-serif;
    font-size: 13px;
}}

/* ═══════════════════════════════════════════
   WINDOWS / DIALOGS
   ═══════════════════════════════════════════ */

QMainWindow {{
    background: {BG_APP};
}}

QDialog {{
    background: {BG_SURFACE};
}}

/* ═══════════════════════════════════════════
   GROUP BOX  (card containers)
   ═══════════════════════════════════════════ */

QGroupBox {{
    background: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    margin-top: 22px;
    padding-top: 10px;
    font-size: 13px;
    color: {TEXT};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    top: 6px;
    padding: 2px 10px;
    color: {ACCENT};
    background: transparent;
    border: none;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}

/* ═══════════════════════════════════════════
   BUTTONS  —  compact by default
   ═══════════════════════════════════════════ */

QPushButton {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 600;
    font-size: 13px;
    color: {TEXT};
}}

QPushButton:hover {{
    background: #243350;
    border-color: {ACCENT};
    color: {ACCENT};
}}

QPushButton:pressed {{
    background: {BG_SURFACE};
    border-color: #27B99A;
}}

QPushButton:disabled {{
    background: {BG_SURFACE};
    border-color: {BG_CARD};
    color: {TEXT_MUTED};
}}

/* Primary CTA */
QPushButton#primaryBtn {{
    background: {ACCENT};
    border-color: {ACCENT};
    color: {BG_APP};
    font-weight: 700;
    font-size: 14px;
    padding: 8px 24px;
    border-radius: 8px;
}}

QPushButton#primaryBtn:hover {{
    background: {ACCENT_HV};
    border-color: {ACCENT_HV};
    color: {BG_APP};
}}

QPushButton#primaryBtn:pressed {{
    background: #27B99A;
}}

QPushButton#primaryBtn:disabled {{
    background: #1B3530;
    border-color: #1B3530;
    color: #4A7A6D;
}}

/* Danger */
QPushButton#dangerBtn {{
    background: transparent;
    border-color: {DANGER};
    color: {DANGER};
    font-weight: 600;
}}

QPushButton#dangerBtn:hover {{
    background: {DANGER_DIM};
    border-color: #FF6B5A;
    color: #FF6B5A;
}}

QPushButton#dangerBtn:disabled {{
    border-color: #4A2C28;
    color: #4A2C28;
}}

/* Ghost / secondary */
QPushButton#ghostBtn {{
    background: transparent;
    border-color: {BORDER};
    color: {TEXT2};
    font-weight: 500;
}}

QPushButton#ghostBtn:hover {{
    background: {BG_CARD};
    color: {TEXT};
    border-color: {BORDER_LT};
}}

/* Accent outline */
QPushButton#accentBtn {{
    background: {ACCENT_DIM};
    border-color: {ACCENT_RING};
    color: {ACCENT};
    font-weight: 600;
}}

QPushButton#accentBtn:hover {{
    background: rgba(46, 203, 171, 0.20);
    border-color: {ACCENT};
}}

/* Table cell buttons — tighter padding */
QTableWidget QPushButton {{
    padding: 5px 10px;
    font-size: 12px;
    border-radius: 5px;
    margin: 3px 4px;
}}

/* ═══════════════════════════════════════════
   INPUTS
   ═══════════════════════════════════════════ */

QLineEdit {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 13px;
    color: {TEXT};
    selection-background-color: {ACCENT};
    selection-color: {BG_APP};
}}

QLineEdit:focus {{
    border-color: {ACCENT};
    background: #0A1020;
}}

QLineEdit:disabled {{
    background: {BG_SURFACE};
    color: {TEXT_MUTED};
}}

QLineEdit::placeholder {{
    color: {TEXT_MUTED};
}}

QTextEdit {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 13px;
    color: {TEXT};
    selection-background-color: {ACCENT};
    selection-color: {BG_APP};
}}

QTextEdit:focus {{
    border-color: {ACCENT};
}}

QTextEdit:disabled {{
    background: {BG_SURFACE};
    color: {TEXT_MUTED};
}}

/* ═══════════════════════════════════════════
   COMBOBOX
   ═══════════════════════════════════════════ */

QComboBox {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 13px;
    color: {TEXT};
}}

QComboBox:hover {{
    border-color: {BORDER_LT};
}}

QComboBox:focus {{
    border-color: {ACCENT};
}}

QComboBox::drop-down {{
    border: none;
    width: 26px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {TEXT2};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px;
    selection-background-color: {ACCENT};
    selection-color: {BG_APP};
    outline: none;
    color: {TEXT};
}}

QComboBox QAbstractItemView::item {{
    min-height: 34px;
    padding: 5px 10px;
    border-radius: 5px;
    margin: 2px 0;
}}

QComboBox QAbstractItemView::item:hover {{
    background: {ACCENT_DIM};
}}

QComboBox QAbstractItemView::item:selected {{
    background: {ACCENT};
    color: {BG_APP};
}}

/* ═══════════════════════════════════════════
   SPINBOX
   ═══════════════════════════════════════════ */

QSpinBox {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: {TEXT};
}}

QSpinBox:focus {{
    border-color: {ACCENT};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    border: none;
    background: {BG_SURFACE};
    width: 20px;
    border-radius: 4px;
    margin: 2px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background: {BG_CARD};
}}

QSpinBox::up-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid {TEXT2};
}}

QSpinBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {TEXT2};
}}

/* ═══════════════════════════════════════════
   TABLES
   ═══════════════════════════════════════════ */

QTableWidget {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 10px;
    gridline-color: {BG_CARD};
    selection-background-color: {ACCENT_DIM};
    selection-color: {TEXT};
    outline: none;
    font-size: 13px;
    alternate-background-color: #0E1622;
}}

QTableWidget::item {{
    padding: 8px 12px;
    border: none;
}}

QTableWidget::item:hover {{
    background: {BG_SURFACE};
}}

QTableWidget::item:selected {{
    background: {ACCENT_DIM};
}}

QHeaderView::section {{
    background: {BG_SURFACE};
    color: {TEXT2};
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid {BORDER};
    border-right: 1px solid {BG_CARD};
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}}

QHeaderView::section:first {{
    border-top-left-radius: 10px;
}}

QHeaderView::section:last {{
    border-top-right-radius: 10px;
    border-right: none;
}}

QHeaderView::section:hover {{
    background: {BG_CARD};
    color: {TEXT};
}}

QTableCornerButton::section {{
    background: {BG_SURFACE};
    border: none;
    border-bottom: 1px solid {BORDER};
}}

/* ═══════════════════════════════════════════
   TABS
   ═══════════════════════════════════════════ */

QTabWidget::pane {{
    background: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    top: -1px;
}}

QTabBar::tab {{
    background: transparent;
    border: 1px solid transparent;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 9px 20px;
    margin-right: 2px;
    font-weight: 500;
    font-size: 13px;
    color: {TEXT2};
}}

QTabBar::tab:hover {{
    background: {BG_SURFACE};
    color: {TEXT};
}}

QTabBar::tab:selected {{
    background: {BG_SURFACE};
    color: {ACCENT};
    border-color: {BORDER};
    border-bottom: 1px solid {BG_SURFACE};
    font-weight: 600;
}}

QTabBar::tab:!selected {{
    margin-top: 4px;
}}

/* ═══════════════════════════════════════════
   PROGRESS BAR
   ═══════════════════════════════════════════ */

QProgressBar {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    text-align: center;
    height: 14px;
    color: {TEXT};
    font-weight: 600;
    font-size: 11px;
}}

QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: 4px;
}}

/* ═══════════════════════════════════════════
   CHECKBOX
   ═══════════════════════════════════════════ */

QCheckBox {{
    color: {TEXT};
    spacing: 8px;
    font-size: 13px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    background: {BG_INPUT};
    border: 1px solid {BORDER};
}}

QCheckBox::indicator:hover {{
    border-color: {ACCENT};
}}

QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}

/* ═══════════════════════════════════════════
   LABELS
   ═══════════════════════════════════════════ */

QLabel {{
    color: {TEXT};
    background: transparent;
}}

QLabel#titleLabel {{
    font-size: 22px;
    font-weight: 700;
    color: {ACCENT};
    letter-spacing: -0.3px;
}}

QLabel#subtitleLabel {{
    font-size: 13px;
    color: {TEXT2};
}}

QLabel#statusLabel {{
    font-size: 12px;
    color: {TEXT2};
}}

QLabel#sectionTitle {{
    font-size: 16px;
    font-weight: 700;
    color: {TEXT};
}}

/* ═══════════════════════════════════════════
   STATUS BAR
   ═══════════════════════════════════════════ */

QStatusBar {{
    background: {BG_SURFACE};
    border-top: 1px solid {BORDER};
    color: {TEXT2};
    font-size: 12px;
}}

QStatusBar::item {{
    border: none;
}}

/* ═══════════════════════════════════════════
   MENU BAR
   ═══════════════════════════════════════════ */

QMenuBar {{
    background: {BG_SURFACE};
    border-bottom: 1px solid {BORDER};
    padding: 2px 0;
}}

QMenuBar::item {{
    padding: 6px 14px;
    border-radius: 6px;
    margin: 2px 4px;
    background: transparent;
    color: {TEXT2};
    font-size: 13px;
}}

QMenuBar::item:selected {{
    background: {BG_CARD};
    color: {TEXT};
}}

QMenuBar::item:pressed {{
    background: #243350;
    color: {ACCENT};
}}

QMenu {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 6px;
}}

QMenu::item {{
    padding: 8px 16px;
    border-radius: 6px;
    margin: 1px 0;
    color: {TEXT};
    font-size: 13px;
}}

QMenu::item:selected {{
    background: {ACCENT_DIM};
    color: {ACCENT};
}}

QMenu::separator {{
    height: 1px;
    background: {BORDER};
    margin: 4px 8px;
}}

/* ═══════════════════════════════════════════
   SCROLLBARS
   ═══════════════════════════════════════════ */

QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {BORDER_LT};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 4px;
    min-width: 24px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {BORDER_LT};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ═══════════════════════════════════════════
   MISC
   ═══════════════════════════════════════════ */

QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

QToolTip {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    color: {TEXT};
    font-size: 12px;
}}

QMessageBox {{
    background: {BG_SURFACE};
}}

QMessageBox QLabel {{
    color: {TEXT};
}}

QMessageBox QPushButton {{
    min-width: 80px;
}}
"""
