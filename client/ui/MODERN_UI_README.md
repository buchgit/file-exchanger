# Modern Card UI for File Exchanger

A fresh, professional interface design for File Exchanger featuring a clean card-based layout.

---

## Quick Start

### Launch the Modern UI
```bash
cd client
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
python main_modern.py
```

### Launch the Original Glassmorphism UI
```bash
cd client
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
python main.py
```

---

## What's New

### Visual Design
- **Light theme** - Clean, professional appearance
- **Card-based layout** - Each file displayed as an individual card
- **Modern color palette** - Royal blue accents on light slate background
- **Improved typography** - Better readability and hierarchy

### User Experience
- **Sidebar navigation** - Quick access to Inbox, Send, and Admin sections
- **File cards** - Clear presentation of file metadata and actions
- **Status badges** - Color-coded indicators for connection status
- **Better spacing** - More generous whitespace for reduced cognitive load

### Accessibility
- **WCAG AA compliant** - High contrast ratios
- **Clear focus states** - Visible indicators for keyboard navigation
- **Icon + color** - Not relying on color alone for information

---

## Design Comparison

| Feature | Original (Glassmorphism) | Modern Card |
|---------|-------------------------|-------------|
| Theme | Dark purple gradient | Light slate |
| Navigation | Tabs only | Sidebar + Tabs |
| File Display | Table | Cards |
| Primary Color | Purple (#667eea) | Blue (#2563eb) |
| Best For | Low light, creative | Bright light, professional |

See `DESIGN_COMPARISON.md` for detailed comparison.

---

## Files

### Styles
- `modern_style.py` - Complete stylesheet for the modern UI

### Components
- `modern_main_window.py` - Main application window with sidebar
- `modern_inbox_widget.py` - Card-based inbox view
- `modern_send_widget.py` - Modern send file form

### Documentation
- `DESIGN_COMPARISON.md` - Detailed comparison of both designs

---

## Color Palette

```
Primary:      #2563eb (Royal Blue)
Secondary:    #64748b (Slate Gray)
Success:      #10b981 (Emerald Green)
Warning:      #f59e0b (Amber)
Danger:       #ef4444 (Red)
Background:   #f1f5f9 (Light Slate)
Cards:        #ffffff (White)
Border:       #e2e8f0 (Light Border)
```

---

## Features

### Inbox View
- 📄 File cards with metadata
- ⬇ Download button on each card
- ✓ Acknowledge button on each card
- 📊 File count badge
- 💬 Comment display

### Send View
- 👥 Recipient selection with refresh
- 📁 File browser with size display
- 🔢 Part number controls
- 💬 Optional comment field
- 📊 Progress indicator
- ✅ Success/error states

### Main Window
- 🎯 Sidebar navigation
- 👤 User badge with avatar
- 🟢 WebSocket status indicator
- 📱 Responsive layout
- 🎨 Consistent styling

---

## Customization

### Change Primary Color

Edit `modern_style.py`:
```python
PRIMARY = "#2563eb"  # Change to your brand color
```

### Adjust Spacing

Modify in component files:
```python
layout.setContentsMargins(24, 24, 24, 24)  # Increase for more space
layout.setSpacing(20)  # Gap between elements
```

### Add Custom Icons

Replace emoji with QIcon:
```python
from PyQt6.QtGui import QIcon
icon_btn.setIcon(QIcon("path/to/icon.svg"))
```

---

## Screenshots

### Inbox (Modern Card)
```
┌─────────────────────────────────────────────┐
│  📥 Inbox                        [⟳ Refresh]│
│  [2 files]                                  │
├─────────────────────────────────────────────┤
│  ┌───────────────────────────────────────┐  │
│  │ 📄 document.pdf                        │  │
│  │ From: User #3 • Part 1/1 • Received   │  │
│  │ 💬 Please review this document        │  │
│  │ [⬇ Download]  [✓ Acknowledge]         │  │
│  └───────────────────────────────────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │ 📄 image.png                           │  │
│  │ From: User #5 • Part 1/2 • Received   │  │
│  │ [⬇ Download]  [✓ Acknowledge]         │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### Send (Modern Card)
```
┌─────────────────────────────────────────────┐
│  📤 Send File                               │
├─────────────────────────────────────────────┤
│  Recipient                                  │
│  [👤 Select User...           ] [⟳ Refresh]│
│                                             │
│  File                                       │
│  [No file selected            ] [📁 Browse]│
│  📦 2.5 MB                                  │
│                                             │
│  Part Number        Total Parts             │
│  [1    ]            [1    ]                 │
│                                             │
│  Comment (optional)                         │
│  ┌─────────────────────────────────────┐    │
│  │ Add a message...                    │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  [━━━━━━━━━━━━━━━░░░░░] 60%                │
│                                             │
│  [📤 Send File]                             │
└─────────────────────────────────────────────┘
```

---

## Performance

- **Fast rendering** - Solid colors vs. transparency
- **Lower memory** - No blur effects
- **Smooth scrolling** - Optimized card layout
- **Quick startup** - Minimal stylesheet parsing

---

## Browser Support

This is a PyQt6 desktop application, so browser compatibility is not applicable. The UI works on:
- ✅ Windows 10/11
- ✅ Linux (Ubuntu, Fedora, etc.)
- ✅ macOS

---

## Feedback

If you prefer this modern design or have suggestions for improvement, please open an issue.

---

## License

Same as File Exchanger project license.

---

*Created: 2026-03-04*
