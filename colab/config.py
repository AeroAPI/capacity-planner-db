"""
Python script to recreate the interactive Capacity Planner GUI using ipywidgets,
including all capacity and memory calculations for the Healthy Cluster scenario.

This script should be run in a Jupyter or Colab notebook cell.
"""
from ipywidgets import IntSlider, FloatSlider, VBox, HBox, Layout, HTML, interactive_output
from IPython.display import display
from typing import Dict, Any
import math

# ==============================================================================
# 1. CONFIGURATION DATA 
# ==============================================================================

# --- STYLING ---
LAYOUT_WIDTH = '32%'
STYLE = {'description_width': 'initial'}
TITLE_STYLE = "font-weight: bold; margin-bottom: 5px; color: #1e40af;"
CARD_STYLE_TPL = "border: 1px solid #bfdbfe; border-radius: 0.5rem; padding: 1.5rem; background-color: white;"
CARD_STYLE_WKL = "border: 1px solid #fbcfe8; border-radius: 0.5rem; padding: 1.5rem; background-color: white;"
CARD_STYLE_SERVER = "border: 1px solid #99f6e4; border-radius: 0.5rem; padding: 1.5rem; background-color: white;"
MAIN_HEADER_STYLE = "font-weight: 600; font-size: 1.25rem; color: #4338ca; margin-bottom: 1rem;"
DIVIDER_STYLE = "border-top: 1px solid #E5E7EB; margin-top: 10px; padding-top: 10px;"

# --- FIXED CONSTANTS (from JS baseline) ---
FIXED_CONSTANTS = {
    'CSOP': 0.024,   # Cluster Storage Overhead Pct (2.4%)
    'OMP': 0.17,     # Overhead Memory Pct (17.00%)
    'PI_ENTRY_SIZE': 64, # bytes
    'SI_ENTRY_SIZE': 21, # bytes
    'SI_OVERHEAD_MIB': 16, # MiB
    'SI_DENSITY_FACTOR': 0.75,
    'BYTES_TO_GB': 1024 ** 3,
    'MIB_TO_GB': 1024,
}

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
    'AMPN': 'Available Memory per Node',
    'CSOP': 'Cluster Storage Overhead Pct',
    'OMP': 'Overhead Memory Pct',
}

INPUT_CONFIG = {
    # --- TOPOLOGY ---
    'RF': { 'min': 1, 'max': 5, 'step': 1, 'default': 3, 'suffix': '' },
    'NPC': { 'min': 1, 'max': 150, 'step': 1, 'default': 12, 'suffix': '' },
    'DPN': { 'min': 1, 'max': 32, 'step': 1, 'default': 18, 'suffix': '' },
    'DS': { 'min': 50, 'max': 1000, 'step': 5, 'default': 55, 'suffix': ' GB' },
    'NODES_LOST': { 'min': 0, 'max': 150, 'step': 1, 'default': 1, 'suffix': '' }, 

    # --- WORKLOAD ---
    'MOC': { 'min': 1, 'max': 1000, 'step': 1, 'default': 8, 'suffix': 'Billion' }, 
    'ARS': { 'min': 100, 'max': 4096, 'step': 32, 'default': 250, 'suffix': ' Bytes' },
    'ASEO': { 'min': 0.0, 'max': 5.0, 'step': 0.1, 'default': 1.0, 'suffix': '' },
    'NSI': { 'min': 0, 'max': 32, 'step': 1, 'default': 5, 'suffix': '' },
    'TP': { 'min': 0, 'max': 100, 'step': 5, 'default': 10, 'suffix': ' %' }, 
    
    # --- SERVER SPECS ---
    'AMPN': { 'min': 16, 'max': 256, 'step': 8, 'default': 64, 'suffix': ' GB' }
}


# ==============================================================================
# 2. CORE CALCULATION LOGIC
# ==============================================================================

def calculate_capacity(inputs: Dict[str, Any]) -> Dict[str, float]:
    """Calculates all capacity and memory metrics."""
    
    # --- Input Mapping ---
    RF = inputs['RF']
    NPC = inputs['NPC']
    DPN = inputs['DPN']
    DS = inputs['DS']
    AMPN = inputs['AMPN']
    TP = inputs['TP'] / 100 
    
    # MOC is in Billions in the config, convert to raw count
    MOC = inputs['MOC'] * 1000000000
    ARS = inputs['ARS']
    ASEO = inputs['ASEO']
    NSI = inputs['NSI']
    
    # --- COMMON CALCULATIONS (Capacity and Index Sizing) ---
    results = {}

    results['AMC'] = NPC * AMPN
    results['OMRC'] = results['AMC'] * FIXED_CONSTANTS['OMP']

    PISU_bytes = MOC * RF * FIXED_CONSTANTS['PI_ENTRY_SIZE']
    results['PISU'] = PISU_bytes / FIXED_CONSTANTS['BYTES_TO_GB']

    SI_part_1_bytes = (MOC * RF * ASEO * FIXED_CONSTANTS['SI_ENTRY_SIZE']) / FIXED_CONSTANTS['SI_DENSITY_FACTOR']
    SI_part_2_gb = NSI * FIXED_CONSTANTS['SI_OVERHEAD_MIB'] / FIXED_CONSTANTS['MIB_TO_GB']
    results['SISU'] = (SI_part_1_bytes / FIXED_CONSTANTS['BYTES_TO_GB']) + SI_part_2_gb

    results['TMU'] = results['OMRC'] + results['PISU'] + results['SISU']
    results['TMT'] = results['TMU'] * (1 + TP) 
    
    results['TSAPC'] = NPC * DPN * DS * (1 - FIXED_CONSTANTS['CSOP'])
    TDS_bytes = MOC * RF * ARS
    results['TDS'] = TDS_bytes / FIXED_CONSTANTS['BYTES_TO_GB']
    
    # --- HEALTHY CLUSTER UTILIZATION ---
    results['ASU'] = (results['TDS'] / results['TSAPC']) * 100
    results['TMBU'] = (results['TMU'] / results['AMC']) * 100
    results['TMUT'] = (results['TMT'] / results['AMC']) * 100
    results['TMAPC'] = results['AMC']

    # --- FAILURE SCENARIO CALCULATIONS (Required for Section 3/5 output labels) ---
    nodes_lost = inputs['NODES_LOST']
    effectiveNodes = max(0, NPC - nodes_lost)
    
    results['Fail_TSAPC'] = effectiveNodes * DPN * DS * (1 - FIXED_CONSTANTS['CSOP'])
    results['Fail_AMC'] = effectiveNodes * AMPN
    
    # Utilization Recalculation (Handle Division by Zero)
    results['Fail_ASU'] = (results['Fail_TSAPC'] > 0) and (results['TDS'] / results['Fail_TSAPC']) * 100 or float('inf')
    results['Fail_TMBU'] = (results['Fail_AMC'] > 0) and (results['TMU'] / results['Fail_AMC']) * 100 or float('inf')
    results['Fail_TMUT'] = (results['Fail_AMC'] > 0) and (results['TMT'] / results['Fail_AMC']) * 100 or float('inf')
    
    return results

def render_html_metric(title: str, result_value: float, raw_used: float, raw_total: float, color_class: str, bar_class: str):
    """Generates HTML for a single utilization card with bar."""
    
    util_pct = result_value
    util_display = f"{util_pct:.2f}%"
    bar_width = min(100, util_pct)
    
    if util_pct > 100:
        util_status = "(OVER)"
    elif util_pct > 85:
        util_status = "(HIGH)"
    else:
        util_status = ""

    # Format GB/TB values
    def format_capacity(value):
        if value >= 1024:
            return f"{value / 1024:.2f} TB"
        return f"{value:.2f} GB"

    return f"""
    <div style="{CARD_STYLE_TPL.replace('border-indigo-200', 'border-gray-200')}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h4 style="font-weight: bold; color: #374151;">{title}</h4>
            <span style="font-size: 1.5em; font-weight: bold; color: {color_class};">{util_display} {util_status}</span>
        </div>
        <div style="background-color: #E5E7EB; border-radius: 4px; height: 10px; margin-bottom: 8px;">
            <div style="width: {bar_width}%; height: 10px; border-radius: 4px; background-color: {bar_class};"></div>
        </div>
        <div style="font-size: 0.85em; color: #6B7280;">
            <p>Used: <span style="font-weight: 600; color: #1f2937;">{format_capacity(raw_used)}</span></p>
            <p>Available: <span style="font-weight: 600; color: #1f2937;">{format_capacity(raw_total)}</span></p>
        </div>
    </div>
    """

def get_bar_color_class(utilization, fail_scenario=False):
    """Maps utilization percentage to a Tailwind color class."""
    if fail_scenario:
        if utilization > 100: return "#dc2626"  # Red-700
        if utilization > 85: return "#f97316"   # Orange-500
        return "#f87171" # Red-400
    else:
        if utilization > 90: return "#dc2626"  # Red-600
        if utilization > 75: return "#f97316"   # Orange-500
        if utilization > 50: return "#fbbf24"   # Yellow-500
        return "#10b981" # Green-600

def get_bar_bg_class(utilization, fail_scenario=False):
    """Maps utilization percentage to a Tailwind background class."""
    if fail_scenario:
        if utilization > 100: return "#b91c1c"
        if utilization > 85: return "#f97316"
        return "#ef4444" 
    else:
        if utilization > 90: return "#dc2626"
        if utilization > 75: return "#f97316"
        if utilization > 50: return "#fbbf24"
        return "#10b981"


def calculate_and_display(**kwargs):
    """The function executed by ipywidgets on input change."""
    
    # 1. Calculate Results
    results = calculate_capacity(kwargs)
    
    # 2. Dynamic Constraint Logic (ensures Nodes Lost <= NPC)
    npc_value = kwargs.get('NPC', INPUT_CONFIG['NPC']['default'])
    nodes_lost_value = kwargs.get('NODES_LOST', INPUT_CONFIG['NODES_LOST']['default'])
    
    nodes_lost_widget = widget_map['NODES_LOST']
    nodes_lost_widget.max = npc_value
    
    if nodes_lost_value > npc_value:
        nodes_lost_widget.value = npc_value
        nodes_lost_value = npc_value
        
    # 3. Render Output
    
    # --- SECTION 2: HEALTHY CAPACITY ---
    section_2_html = render_html_metric(
        "Actual Storage Utilization (%)", 
        results['ASU'], 
        results['TDS'], 
        results['TSAPC'], 
        get_bar_color_class(results['ASU']),
        get_bar_bg_class(results['ASU'])
    )
    section_2_html += render_html_metric(
        "Total Memory Base Utilization (%)", 
        results['TMBU'], 
        results['TMU'], 
        results['TMAPC'], 
        get_bar_color_class(results['TMBU']),
        get_bar_bg_class(results['TMBU'])
    )
    section_2_html += render_html_metric(
        "Memory Utilization w/ Tombstones (%)", 
        results['TMUT'], 
        results['TMT'], 
        results['AMC'], 
        get_bar_color_class(results['TMUT']),
        get_bar_bg_class(results['TMUT'])
    )

    
    # --- ASSEMBLE FINAL OUTPUT ---
    
    output_html = f"""
    <div style="width: 100%;">
        <h2 style="{MAIN_HEADER_STYLE.replace('1.25rem', '1.1rem').replace('margin-bottom: 1rem', 'margin-bottom: 0.5rem')}">2. Capacity Analysis (Healthy Cluster)</h2>
        <div style="padding: 10px 0;">
            {section_2_html}
        </div>
        <p style='color:#374151; margin-top: 15px;'>Future analysis panels will display here.</p>
    </div>
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
    
    full_label = DISPLAY_NAMES.get(id, id)
    description_text = full_label

    return SliderClass(
        min=config['min'],
        max=config['max'],
        step=config['step'],
        value=config['default'],
        description=description_text,
        style=STYLE,
        layout=Layout(width='auto')
    )

# ==============================================================================
# 3. WIDGET SETUP AND LAYOUT
# ==============================================================================

# Create a map of widgets for easy access
widget_ids = ['RF', 'NPC', 'DPN', 'DS', 'NODES_LOST', 'MOC', 'ARS', 'ASEO', 'NSI', 'TP', 'AMPN']
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
], layout=Layout(width=LAYOUT_WIDTH, border=CARD_STYLE_TPL))


# 2. Workload Panel Layout
workload_box = VBox([
    HTML(f'<div style="{TITLE_STYLE}; color: #ec4899;">Workload Inputs</div>'), 
    widget_map['MOC'], 
    widget_map['ARS'], 
    widget_map['ASEO'], 
    widget_map['NSI'],
    HTML('<hr style="margin: 10px 0; border-color: #fbcfe8;">'),
    widget_map['TP'],
], layout=Layout(width=LAYOUT_WIDTH, border=CARD_STYLE_WKL))


# 3. Server Specs & Overhead Panel Layout
server_box = VBox([
    HTML(f'<div style="{TITLE_STYLE}; color: #14b8a6;">Server Specs & Overhead</div>'), 
    widget_map['AMPN'],
    HTML('<hr style="margin: 10px 0; border-color: #99f6e4;">'),
    HTML(f'<p style="font-size: 0.9em; color: #6b7280;">{DISPLAY_NAMES["CSOP"]}: {FIXED_CONSTANTS["CSOP"]*100:.2f}%</p>'),
    HTML(f'<p style="font-size: 0.9em; color: #6b7280;">{DISPLAY_NAMES["OMP"]}: {FIXED_CONSTANTS["OMP"]*100:.2f}%</p>'),
], layout=Layout(width=LAYOUT_WIDTH, border=CARD_STYLE_SERVER))


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
    ], layout=Layout(justify_content='space-between', width='100%')), 
    
    HTML('<hr style="margin: 20px 0; border-color: #e5e7eb;">'),
    
    VBox([
        HTML(f'<h3 style="{MAIN_HEADER_STYLE}">2. Capacity and Performance Analysis</h3>'),
        output_area
    ])
])

# Display the application
display(final_layout)
