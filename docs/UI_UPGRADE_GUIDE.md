# UI Upgrade Guide

## Overview

This guide documents the UI upgrade from the original version to the enhanced modern version.

## Comparison Table

| Feature | Original | New Version |
|---------|----------|-------------|
| Layout | Single page | Tab-based (Dashboard, Sources, Monitor) |
| Theme | Light only | Light + Dark (with local storage) |
| Statistics | None | Dashboard with 4 key metrics |
| Visualization | None | Performance bar chart + health indicators |
| Search | No | Yes (search sources by name) |
| Filters | No | Yes (by type/health) |
| History | No | Recent activity feed |
| Batch Actions | No | Yes (placeholder) |
| Config Export/Import | No | Yes (placeholder) |
| Status Indicators | None | Success/Warning/Error with colors |
| Fixed Save Button | No | Yes (FAB) |
| Responsive | Basic | Enhanced |

## New Features

### 1. Dashboard Tab
- **Statistics Cards**: Total Sources, Success Rate, Avg Response, Data Quality
- **Performance Trend Chart**: Visual representation of 7-day performance
- **Source Health Breakdown**: Progress bars showing healthy/warning/error sources
- **Recent Activity**: Timeline of last events

### 2. Sources Tab (Enhanced)
- **Search Bar**: Real-time search filtering
- **Filter Chips**: Quick filters (All, Movie, TVShow, Healthy, Warning)
- **Batch Actions Button**: For multi-source operations
- **FAB Save Button**: Easy access to save

### 3. Monitor Tab
- **Performance Metrics Table**: Success rate, avg time, last check, status
- **Configuration Actions**: Export/Import/Reset config
- **Health Status Indicators**: Color-coded dots for quick scanning

### 4. Theme Support
- **Light Theme**: Classic blue-based (default)
- **Dark Theme**: Dark mode for low-light usage
- **Persistent Preference**: Saves choice to localStorage

### 5. Visual Improvements
- **CSS Variables**: Easy theming and customization
- **Smooth Transitions**: Hover effects, modal animations
- **Better Spacing**: Improved readability
- **Card Design**: Modern card-based UI
- **Color Coding**: Status indicators with consistent colors

## File Structure

```
configserver/
├── server.py (unchanged)
└── templates/
    ├── index.html (original)
    ├── index.v2.html (NEW - enhanced)
    ├── config.html (unchanged)
    └── source.html (unchanged)
```

## How to Enable

### Option 1: Temporary Testing
1. Start the server normally
2. Navigate to the UI
3. Replace `index.html` with `index.v2.html` in your browser's dev tools
4. Or manually edit the file path temporarily

### Option 2: Permanent Upgrade
1. Backup original `index.html`
2. Rename `index.v2.html` to `index.html`
3. Restart server

## Technical Details

### Theme System
```css
:root { --primary-color: #2196F3; }
[data-theme="dark"] { --primary-color: #1976D2; }
```

### Tab System
```javascript
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
}
```

### Search & Filter
```javascript
function searchSources(query) {
    const items = document.querySelectorAll('.source-item');
    items.forEach(item => {
        item.style.display = item.textContent.toLowerCase().includes(query) ? 'block' : 'none';
    });
}
```

## Next Steps

1. **Backend Integration**: Connect real data to the dashboard
   - Hook up statistics to actual scraping metrics
   - Add real-time status updates
   - Implement config import/export

2. **Testing**: Test responsive behavior on various screen sizes

3. **Additional Features**:
   - Source testing button in UI
   - Real-time scraping logs
   - More visualizations

4. **Mobile Optimization**: Further optimize for small screens

## Screenshots (Concept)

### Dashboard
```
┌─────────────────────────────────────────┐
│ [73] [87%] [1.2s] [95%]                 │
│ [Chart]              [Health Breakdown] │
│ [Recent Activity...]                   │
└─────────────────────────────────────────┘
```

### Sources
```
┌─────────────────────────────────────────┐
│ [Search...] [Filters] [Batch Actions]   │
│ Source 1 [collapsible config]           │
│ Source 2 [collapsible config]           │
│ ...                                     │
└─────────────────────────────────────────┘
```

## Notes

- The upgrade maintains full backward compatibility with existing scraping configurations
- No changes required to scraping source definitions
- Works on same port and same authentication mechanism
