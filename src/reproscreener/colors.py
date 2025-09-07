"""
IBM Carbon Design System Color Palettes
=======================================

This module provides comprehensive IBM Carbon color palettes for data visualization.
All color values are provided exactly as specified in the IBM Carbon Design System.

Usage:
    from reproscreener.colors import CATEGORICAL_LIGHT, CATEGORICAL_2_LIGHT_OPTION_1
    
    # For 3 groups using option 1
    colors = CATEGORICAL_3_LIGHT_OPTION_1
"""

# ===== CATEGORICAL PALETTES =====

# Full categorical palette - Light
CATEGORICAL_LIGHT = [
    "#6929c4",  # Purple 70
    "#1192e8",  # Cyan 50
    "#005d5d",  # Teal 70
    "#9f1853",  # Magenta 70
    "#fa4d56",  # Red 50
    "#570408",  # Red 90
    "#198038",  # Green 60
    "#002d9c",  # Blue 80
    "#ee538b",  # Magenta 50
    "#b28600",  # Yellow 50
    "#009d9a",  # Teal 50
    "#012749",  # Cyan 90
    "#8a3800",  # Orange 70
    "#a56eff"   # Purple 50
]

# Full categorical palette - Dark
CATEGORICAL_DARK = [
    "#8a3ffc",  # Purple 60
    "#33b1ff",  # Cyan 40
    "#007d79",  # Teal 60
    "#ff7eb6",  # Magenta 40
    "#fa4d56",  # Red 50
    "#fff1f1",  # Red 10
    "#6fdc8c",  # Green 30
    "#4589ff",  # Blue 50
    "#d12771",  # Magenta 60
    "#d2a106",  # Yellow 40
    "#08bdba",  # Teal 40
    "#bae6ff",  # Cyan 20
    "#ba4e00",  # Orange 60
    "#d4bbff"   # Purple 30
]

# ===== 1 COLOR GROUP =====

# 1 Color group - Light
CATEGORICAL_1_LIGHT_OPTION_1 = ["#6929c4"]  # Purple 70
CATEGORICAL_1_LIGHT_OPTION_2 = ["#002d9c"]  # Blue 80
CATEGORICAL_1_LIGHT_OPTION_3 = ["#1192e8"]  # Cyan 50
CATEGORICAL_1_LIGHT_OPTION_4 = ["#005d5d"]  # Teal 70

# 1 Color group - Dark
CATEGORICAL_1_DARK_OPTION_1 = ["#d4bbff"]  # Purple 30
CATEGORICAL_1_DARK_OPTION_2 = ["#4589ff"]  # Blue 50
CATEGORICAL_1_DARK_OPTION_3 = ["#33b1ff"]  # Cyan 40
CATEGORICAL_1_DARK_OPTION_4 = ["#08bdba"]  # Teal 40

# ===== 2 COLOR GROUP =====

# 2 color group - Light
CATEGORICAL_2_LIGHT_OPTION_1 = ["#6929c4", "#009d9a"]  # Purple 70, Teal 50
CATEGORICAL_2_LIGHT_OPTION_2 = ["#8a3ffc", "#570408"]  # Purple 60, Red 90
CATEGORICAL_2_LIGHT_OPTION_3 = ["#9f1853", "#570408"]  # Magenta 70, Red 90
CATEGORICAL_2_LIGHT_OPTION_4 = ["#1192e8", "#005d5d"]  # Cyan 50, Teal 70
CATEGORICAL_2_LIGHT_OPTION_5 = ["#009d9a", "#002d9c"]  # Teal 50, Blue 80

# 2 color group - Dark
CATEGORICAL_2_DARK_OPTION_1 = ["#8a3ffc", "#08bdba"]  # Purple 60, Teal 40
CATEGORICAL_2_DARK_OPTION_2 = ["#8a3ffc", "#ff7eb6"]  # Purple 60, Magenta 40
CATEGORICAL_2_DARK_OPTION_3 = ["#ff7eb6", "#fff1f1"]  # Magenta 40, Red 10
CATEGORICAL_2_DARK_OPTION_4 = ["#4589ff", "#bae6ff"]  # Blue 50, Cyan 20
CATEGORICAL_2_DARK_OPTION_5 = ["#007d79", "#6fdc8c"]  # Teal 60, Green 30

# ===== 3 COLOR GROUP =====

# 3 color group - Light
CATEGORICAL_3_LIGHT_OPTION_1 = ["#a56eff", "#005d5d", "#9f1853"]  # Purple 50, Teal 70, Magenta 70
CATEGORICAL_3_LIGHT_OPTION_2 = ["#9f1853", "#fa4d56", "#570408"]  # Magenta 70, Red 50, Red 90
CATEGORICAL_3_LIGHT_OPTION_3 = ["#a56eff", "#005d5d", "#002d9c"]  # Purple 50, Teal 70, Blue 80
CATEGORICAL_3_LIGHT_OPTION_4 = ["#ee538b", "#1192e8", "#6929c4"]  # Magenta 50, Cyan 50, Purple 70
CATEGORICAL_3_LIGHT_OPTION_5 = ["#012749", "#6929c4", "#009d9a"]  # Cyan 90, Purple 70, Teal 50

# 3 color group - Dark
CATEGORICAL_3_DARK_OPTION_1 = ["#8a3ffc", "#08bdba", "#bae6ff"]  # Purple 60, Teal 40, Cyan 20
CATEGORICAL_3_DARK_OPTION_2 = ["#8a3ffc", "#ff7eb6", "#fff1f1"]  # Purple 60, Magenta 40, Red 10
CATEGORICAL_3_DARK_OPTION_3 = ["#4589ff", "#08bdba", "#d4bbff"]  # Blue 50, Teal 40, Purple 30
CATEGORICAL_3_DARK_OPTION_4 = ["#4589ff", "#6fdc8c", "#fff1f1"]  # Blue 50, Green 30, Red 10
CATEGORICAL_3_DARK_OPTION_5 = ["#012749", "#6fdc8c", "#bae6ff"]  # Teal 60, Green 30, Cyan 20

# ===== 4 COLOR GROUP =====

# 4 color group - Light
CATEGORICAL_4_LIGHT_OPTION_1 = ["#9f1853", "#fa4d56", "#570408", "#a56eff"]  # Magenta 70, Red 50, Red 90, Purple 50
CATEGORICAL_4_LIGHT_OPTION_2 = ["#6929c4", "#012749", "#009d9a", "#ee538b"]  # Purple 70, Cyan 90, Teal 50, Magenta 50
CATEGORICAL_4_LIGHT_OPTION_3 = ["#009d9a", "#002d9c", "#a56eff", "#9f1853"]  # Teal 50, Blue 80, Purple 50, Magenta 70

# 4 color group - Dark
CATEGORICAL_4_DARK_OPTION_1 = ["#8a3ffc", "#08bdba", "#bae6ff", "#4589ff"]  # Purple 60, Teal 40, Cyan 20, Blue 50
CATEGORICAL_4_DARK_OPTION_2 = ["#4589ff", "#08bdba", "#d4bbff", "#fff1f1"]  # Blue 50, Teal 40, Purple 30, Red 10
CATEGORICAL_4_DARK_OPTION_3 = ["#007d79", "#fff1f1", "#33b1ff", "#6fdc8c"]  # Teal 60, Red 10, Cyan 40, Green 30

# ===== MONOCHROMATIC PALETTES =====

# Monochromatic - Blue
MONOCHROMATIC_BLUE = [
    "#edf5ff",  # Blue 10
    "#d0e2ff",  # Blue 20
    "#a6c8ff",  # Blue 30
    "#78a9ff",  # Blue 40
    "#4589ff",  # Blue 50
    "#0f62fe",  # Blue 60
    "#0043ce",  # Blue 70
    "#002d9c",  # Blue 80
    "#001d6c",  # Blue 90
    "#001141"   # Blue 100
]

# Monochromatic - Purple
MONOCHROMATIC_PURPLE = [
    "#f6f2ff",  # Purple 10
    "#e8daff",  # Purple 20
    "#d4bbff",  # Purple 30
    "#be95ff",  # Purple 40
    "#a56eff",  # Purple 50
    "#8a3ffc",  # Purple 60
    "#6929c4",  # Purple 70
    "#491d8b",  # Purple 80
    "#31135e",  # Purple 90
    "#1c0f30"   # Purple 100
]

# Monochromatic - Cyan
MONOCHROMATIC_CYAN = [
    "#e5f6ff",  # Cyan 10
    "#bae6ff",  # Cyan 20
    "#82cfff",  # Cyan 30
    "#33b1ff",  # Cyan 40
    "#1192e8",  # Cyan 50
    "#0072c3",  # Cyan 60
    "#00539a",  # Cyan 70
    "#003a6d",  # Cyan 80
    "#012749",  # Cyan 90
    "#061727"   # Cyan 100
]

# Monochromatic - Teal
MONOCHROMATIC_TEAL = [
    "#d9fbfb",  # Teal 10
    "#9ef0f0",  # Teal 20
    "#3ddbd9",  # Teal 30
    "#08bdba",  # Teal 40
    "#009d9a",  # Teal 50
    "#007d79",  # Teal 60
    "#005d5d",  # Teal 70
    "#004144",  # Teal 80
    "#022b30",  # Teal 90
    "#081a1c"   # Teal 100
]

# ===== DIVERGING PALETTES =====

# Red-Cyan Diverging Palette
DIVERGING_RED_CYAN = [
    "#750e13",  # Red 80
    "#a2191f",  # Red 70
    "#da1e28",  # Red 60
    "#fa4d56",  # Red 50
    "#ff8389",  # Red 40
    "#ffb3b8",  # Red 30
    "#ffd7d9",  # Red 20
    "#fff1f1",  # Red 10
    "#e5f6ff",  # Cyan 10
    "#bae6ff",  # Cyan 20
    "#82cfff",  # Cyan 30
    "#33b1ff",  # Cyan 40
    "#1192e8",  # Cyan 50
    "#0072c3",  # Cyan 60
    "#00539a",  # Cyan 70
    "#003a6d"   # Cyan 80
]

# Purple-Teal Diverging Palette
DIVERGING_PURPLE_TEAL = [
    "#491d8b",  # Purple 80
    "#6929c4",  # Purple 70
    "#8a3ffc",  # Purple 60
    "#a56eff",  # Purple 50
    "#be95ff",  # Purple 40
    "#d4bbff",  # Purple 30
    "#e8daff",  # Purple 20
    "#f6f2ff",  # Purple 10
    "#d9fbfb",  # Teal 10
    "#9ef0f0",  # Teal 20
    "#3ddbd9",  # Teal 30
    "#08bdba",  # Teal 40
    "#009d9a",  # Teal 50
    "#007d79",  # Teal 60
    "#005d5d",  # Teal 70
    "#004144"   # Teal 80
]

# ===== ALERT PALETTES =====

# Alert - Light
ALERT_LIGHT = [
    "#da1e28",  # Red 60
    "#ff832b",  # Orange 40
    "#f1c21b",  # Yellow 30
    "#198038"   # Green 60
]

# Alert - Dark
ALERT_DARK = [
    "#fa4d56",  # Red 50
    "#ff832b",  # Orange 40
    "#f1c21b",  # Yellow 30
    "#24a148"   # Green 50
]

# ===== METRIC GROUPING COLORS =====

# Color mappings for metric groups using Carbon Palette 3-color option 1
METRIC_GROUP_COLORS_LIGHT = {
    "Method": "#a56eff",    # Purple 50
    "Data": "#005d5d",      # Teal 70  
    "Experiment": "#9f1853" # Magenta 70
}

METRIC_GROUP_COLORS_DARK = {
    "Method": "#8a3ffc",    # Purple 60
    "Data": "#08bdba",      # Teal 40
    "Experiment": "#ff7eb6" # Magenta 40
}

# ===== CONVENIENCE MAPPINGS =====

# For backwards compatibility with existing code
carbon_palette_1 = {
    "LLaMA 3.2": CATEGORICAL_3_LIGHT_OPTION_1[0],  # Purple 50
    "Regex": CATEGORICAL_3_LIGHT_OPTION_1[1],      # Teal 70
    "GPT-4": CATEGORICAL_3_LIGHT_OPTION_1[2]       # Magenta 70
}

# Quick access to commonly used palettes
CARBON_3_LIGHT_1 = CATEGORICAL_3_LIGHT_OPTION_1
CARBON_3_DARK_1 = CATEGORICAL_3_DARK_OPTION_1
