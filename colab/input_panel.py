"""
Python script to recreate the interactive Topology Panel using ipywidgets,
mimicking the layout and functionality of capacity_planner_mvp2.html.

This script should be run in a Jupyter or Colab notebook cell.
"""
from ipywidgets import IntSlider, FloatSlider, VBox, HBox, Layout, HTML, interactive_output
from IPython.display import display
from typing import Dict, Any

# ==============================================================================
# 1. CONFIGURATION DATA 
# ==============================================================================

# --- STYLING ---
LAYOUT_WIDTH = '400px'
STYLE = {'description_width': 'initial'}
TITLE_STYLE = "font-weight: bold; margin-bottom: 5px; color: #1e40af;"
CARD_STYLE_TPL = "border: 1px solid #bfdbfe; border-radius: 0.5rem; padding: 1.5rem; background-color: white;"
CARD_STYLE_WKL = "border: 1px solid #fbcfe8; border-radius: 0.5rem; padding: 1.5rem; background-color: white;"
MAIN_HEADER_STYLE = "font-weight: 600; font-size: 1.25rem; color: #4338ca; margin-bottom: 1rem;"
DIVIDER_STYLE = "border-top: 1px solid #E5E7EB; margin-top: 10px; padding-top: 10px;"


# --- DESCRIPTIVE DISPLAY NAMES ---
DISPLAY_NAMES = {
    'RF': 'Replication Factor',
    'NPC': 'Nodes per Cluster',
    'DPN': 'Devices per Node',
    'DS': 'Device Size',
    'NODES_LOST': 'Nodes Lost (Failure Scenario)',
    'MOC': 'Master Object Count',
    'ARS': 'Average Record Size',
    'ASEO': 'Avg SI Entries per Object',
    'NSI': 'Number of Secondary Indexes',
    'TP': 'Tombstone Percentage',
}

INPUT_CONFIG = {
    # --- TOPOLOGY ---
    'RF': { 'min': 1, 'max': 5, 'step': 1, 'default': 3, 'suffix': '' },
    'NPC': { 'min': 1, 'max': 150, 'step': 1, 'default': 12, 'suffix': '' },
    'DPN': { 'min': 1, 'max': 32, 'step': 1, 'default': 18, 'suffix': '' },
    'DS': { 'min': 50, 'max': 1000, 'step': 5, 'default': 55, 'suffix': ' GB' },
    'NODES_LOST': { 'min': 1, 'max': 150, 'step': 1, 'default': 1, 'suffix': '' }, 

    # --- WORKLOAD ---
    'MOC': { 'min': 1, 'max': 1000, 'step': 1, 'default': 8, 'suffix': 'Billion' }, 
    'ARS': { 'min': 100, 'max': 4096, 'step': 32, 'default': 250, 'suffix': ' Bytes' },
    'ASEO': { 'min': 0.0, 'max': 5.0, 'step': 0.1, 'default': 1.0, 'suffix': '' },
    'NSI': { 'min': 0, 'max': 32, 'step': 1, 'default': 5, 'suffix': '' },
    'TP': { 'min': 0, 'max': 100, 'step': 5, 'default': 10, 'suffix': ' %' }, 
}


# ==============================================================================
# 2. CALCULATION AND DISPLAY LOGIC
# ==============================================================================

def calculate_and_display(**kwargs):
    """
    Placeholder function to handle all input changes and trigger updates.
    """
    
    npc_value = kwargs.get('NPC', INPUT_CONFIG['NPC']['default'])
    nodes_lost_value = kwargs.get('NODES_LOST', INPUT_CONFIG['NODES_LOST']['default'])
    
    # 1. Dynamic Constraint Logic (ensures Nodes Lost <= NPC)
    nodes_lost_widget = widget_map['NODES_LOST']
    nodes_lost_widget.max = npc_value
    
    if nodes_lost_value > npc_value:
        nodes_lost_widget.value = npc_value
        nodes_lost_value = npc_value # Use corrected value for display
        
    # 2. Display Current Input State
    output_html = f"""
        <h4 style="font-weight: bold; color: #4b5563;">Current Configuration State:</h4>
        <ul style="margin-top: 5px; list-style: disc; margin-left: 20px;">
            <li>{DISPLAY_NAMES['RF']}: {kwargs.get('RF')}</li>
            <li>{DISPLAY_NAMES['NPC']}: {npc_value}</li>
            <li>{DISPLAY_NAMES['DPN']}: {kwargs.get('DPN')}</li>
            <li>{DISPLAY_NAMES['NODES_LOST']}: {nodes_lost_value}</li>
            <li>{DISPLAY_NAMES['MOC']}: {kwargs.get('MOC')} {INPUT_CONFIG['MOC']['suffix']}</li>
            <li>{DISPLAY_NAMES['ARS']}: {kwargs.get('ARS')} {INPUT_CONFIG['ARS']['suffix']}</li>
        </ul>
        <p style='color:#374151; margin-top: 15px;'>Capacity and Performance analysis will display here in future steps.</p>
    """
    return HTML(value=output_html)

def create_slider(id: str) -> IntSlider | FloatSlider:
    """
    Helper to create a slider widget based on the INPUT_CONFIG, 
    using DISPLAY_NAMES for the label.
    """
    config = INPUT_CONFIG[id]
    is_float = config.get('step', 1) < 1.0
    SliderClass = FloatSlider if is_float else IntSlider
    
    # FIX: Retrieve the full descriptive name and unit suffix
    full_label = DISPLAY_NAMES.get(id, id)
    suffix = config.get('suffix', '').strip()
    
    # Combine the full label and suffix for a clean description
    description_text = f"{full_label}{f' ({suffix})' if suffix else ''}"

    return SliderClass(
        min=config['min'],
        max=config['max'],
        step=config['step'],
        value=config['default'],
        description=full_label, # Use the full name for the primary description
        style=STYLE,
        layout=Layout(width='auto')
    )

# ==============================================================================
# 3. WIDGET SETUP AND LAYOUT
# ==============================================================================

# Create a map of widgets for easy access
widget_ids = ['RF', 'NPC', 'DPN', 'DS', 'NODES_LOST', 'MOC', 'ARS', 'ASEO', 'NSI', 'TP']
widget_map: Dict[str, Any] = {}
for id in widget_ids:
    widget_map[id] = create_slider(id)


# 1. Topology Panel Layout
topology_box = VBox([
    HTML(f'<div style="{TITLE_STYLE}">Topology</div>'), 
    widget_map['RF'], 
    widget_map['NPC'], 
    widget_map['DPN'], 
    widget_map['DS'],
    HTML('<hr style="margin: 10px 0; border-color: #bfdbfe;">'),
    HTML(f'<div style="{TITLE_STYLE}; color: #8b5cf6;">Resilience Input</div>'),
    widget_map['NODES_LOST'],
    HTML('<p style="font-size: 0.8em; color: #6b7280; margin-top: 5px;">Nodes Lost must be ≤ Nodes per Cluster.</p>')
], layout=Layout(width='32%', border=CARD_STYLE_TPL))


# 2. Workload Panel Layout
workload_box = VBox([
    HTML(f'<div style="{TITLE_STYLE}; color: #ec4899;">Workload Inputs</div>'), 
    widget_map['MOC'], 
    widget_map['ARS'], 
    widget_map['ASEO'], 
    widget_map['NSI'],
    HTML('<hr style="margin: 10px 0; border-color: #fbcfe8;">'),
    widget_map['TP'],
], layout=Layout(width='32%', border=CARD_STYLE_WKL))


# 3. Server Specs & Overhead Panel Layout (Placeholder)
server_box = VBox([
    HTML(f'<div style="{TITLE_STYLE}; color: #14b8a6;">Server Specs & Overhead</div>'), 
    HTML('<p style="font-size: 0.9em; color: #6b7280;">Input will be added later.</p>'),
], layout=Layout(width='32%', border="1px solid #99f6e4; border-radius: 0.5rem; padding: 1.5rem; background-color: white;"))


# 4. Interactive Output Area (Must map all widgets used by calculate_and_display)
output_area = interactive_output(
    calculate_and_display, 
    {k: widget_map[k] for k in widget_ids} # Maps all widgets used
)

# 5. Assemble Final Layout
final_layout = VBox([
    HTML(f'<h1 style="{MAIN_HEADER_STYLE}">1. System & Workload Configuration</h1>'),
    HBox([
        topology_box,
        workload_box,
        server_box
    ], layout=Layout(justify_content='space-between')), # Space between panels
    
    HTML('<hr style="margin: 20px 0; border-color: #e5e7eb;">'),
    
    VBox([
        HTML(f'<h3 style="{MAIN_HEADER_STYLE}">Output / Console</h3>'),
        output_area
    ])
])

# Display the application
display(final_layout)
