"""
Main execution script for the interactive Capacity Planner GUI (Colab/Jupyter).

Sets up UI widgets and links them to the calculator logic.
"""
from ipywidgets import IntSlider, FloatSlider, VBox, HBox, Layout, HTML, interactive_output
from IPython.display import display
from typing import Dict, Any
import math
import config
import calculator

# ==============================================================================
# 1. STYLING & HELPER FUNCTIONS
# ==============================================================================

LAYOUT_WIDTH = '32%'
STYLE = {'description_width': 'initial'}
TITLE_STYLE = "font-weight: bold; margin-bottom: 5px; color: #1e40af;"
CARD_STYLE_TPL = "border: 1px solid #bfdbfe; border-radius: 0.5rem; padding: 1.5rem; background-color: white;"
CARD_STYLE_WKL = "border: 1px solid #fbcfe8; border-radius: 0.5rem; padding: 1.5rem; background-color: white;"
CARD_STYLE_SERVER = "border: 1px solid #99f6e4; border-radius: 0.5rem; padding: 1.5rem; background-color: white;"
CARD_STYLE_CAPACITY = "border: 1px solid #bbf7d0; border-radius: 0.5rem; padding: 1.5rem; background-color: white;"
MAIN_HEADER_STYLE = "font-weight: 600; font-size: 1.25rem; color: #4338ca; margin-bottom: 1rem;"

def get_bar_color_class(utilization, fail_scenario=False):
    """Maps utilization percentage to an appropriate color."""
    if not math.isfinite(utilization) or utilization > 100: return "#dc2626"
    if fail_scenario:
        if utilization > 85: return "#f97316"
        return "#f87171"
    else:
        if utilization > 90: return "#dc2626"
        if utilization > 75: return "#f97316"
        if utilization > 50: return "#fbbf24"
        return "#10b981"

def get_bar_bg_class(utilization, fail_scenario=False):
    """Maps utilization percentage to a background color."""
    if not math.isfinite(utilization) or utilization > 100: return "#b91c1c"
    if fail_scenario:
        if utilization > 85: return "#f97316"
        return "#ef4444" 
    else:
        if utilization > 90: return "#dc2626"
        if utilization > 75: return "#f97316"
        if utilization > 50: return "#fbbf24"
        return "#10b981"

def format_capacity_label(value):
    """Formats GB value to GB or TB."""
    if not math.isfinite(value): return 'N/A'
    if value >= 1024:
        return f"{value / 1024:,.2f} TB"
    return f"{value:,.2f} GB"

def render_html_metric(title: str, results: Dict[str, float], metric_key: str, used_key: str, total_key: str, is_failure: bool = False):
    """Generates HTML for a single utilization card with bar and raw values."""
    
    util_pct = results.get(metric_key, 0)
    raw_used = results.get(used_key, 0)
    raw_total = results.get(total_key, 0)
    
    util_display = f"{util_pct:.2f}%" if math.isfinite(util_pct) else "FATAL"
    bar_width = min(100, util_pct)
    
    color_class = get_bar_color_class(util_pct, is_failure)
    bar_class = get_bar_bg_class(util_pct, is_failure)

    return f"""
    <div style="{CARD_STYLE_CAPACITY.replace('border-indigo-200', 'border-gray-200').replace('bbf7d0', 'd1d5db')}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h4 style="font-weight: bold; color: #374151;">{title}</h4>
            <span style="font-size: 1.5em; font-weight: bold; color: {color_class};">{util_display}</span>
        </div>
        <div style="background-color: #E5E7EB; border-radius: 4px; height: 10px; margin-bottom: 8px;">
            <div style="width: {bar_width}%; height: 10px; border-radius: 4px; background-color: {bar_class};"></div>
        </div>
        <div style="font-size: 0.85em; color: #6B7280;">
            <p>Used: <span style="font-weight: 600; color: #1f2937;">{format_capacity_label(raw_used)}</span></p>
            <p>Available: <span style="font-weight: 600; color: #1f2937;">{format_capacity_label(raw_total)}</span></p>
        </div>
    </div>
    """

def create_slider(id: str) -> IntSlider | FloatSlider:
    """Helper to create a slider widget based on the INPUT_CONFIG."""
    config_item = config.INPUT_CONFIG[id]
    is_float = config_item.get('step', 1) < 1.0
    SliderClass = FloatSlider if is_float else IntSlider
    
    # Use DISPLAY_NAMES for the slider label
    full_label = config.DISPLAY_NAMES.get(id, id)
    
    description_text = f"{full_label}{f' ({config_item.get('suffix').strip()})' if config_item.get('suffix') else ''}"

    return SliderClass(
        min=config_item['min'],
        max=config_item['max'],
        step=config_item['step'],
        value=config_item['default'],
        description=full_label,
        style=STYLE,
        layout=Layout(width='auto')
    )

# ==============================================================================
# 3. INTERACTIVE CORE LOGIC (Links UI to Calculator)
# ==============================================================================

def calculate_and_display(**kwargs):
    """The function executed by ipywidgets on input change."""
    
    # 1. Calculate Results using the external calculator
    results = calculator.calculate_capacity(kwargs)
    
    # 2. Dynamic Constraint Logic (ensures Nodes Lost <= NPC)
    npc_value = kwargs.get('NPC', config.INPUT_CONFIG['NPC']['default'])
    nodes_lost_value = kwargs.get('NODES_LOST', config.INPUT_CONFIG['NODES_LOST']['default'])
    
    # Update max value of NODES_LOST widget (must be done outside the calculation output function)
    if 'NODES_LOST' in widget_map:
        nodes_lost_widget = widget_map['NODES_LOST']
        nodes_lost_widget.max = npc_value
        if nodes_lost_value > npc_value:
            nodes_lost_widget.value = npc_value
            nodes_lost_value = npc_value
            
    # 3. Render Output
    
    # --- SECTION 2: HEALTHY CAPACITY ---
    section_2_html = render_html_metric(
        "Actual Storage Utilization (%)", results, 'ASU', 'TDS', 'TSAPC'
    )
    section_2_html += render_html_metric(
        "Total Memory Base Utilization (%)", results, 'TMBU', 'TMU', 'TMAPC'
    )
    section_2_html += render_html_metric(
        "Memory Utilization w/ Tombstones (%)", results, 'TMUT', 'TMT', 'AMC'
    )

    
    # --- SECTION 3: FAILURE CAPACITY ---
    section_3_html = render_html_metric(
        "Failure Storage Utilization (%)", results, 'Fail_ASU', 'TDS', 'Fail_TSAPC', is_failure=True
    )
    section_3_html += render_html_metric(
        "Failure Memory Base Utilization (%)", results, 'Fail_TMBU', 'TMU', 'Fail_AMC', is_failure=True
    )
    section_3_html += render_html_metric(
        "Failure Memory w/ Tombstones (%)", results, 'Fail_TMUT', 'TMT', 'Fail_AMC', is_failure=True
    )


    # --- ASSEMBLE FINAL OUTPUT ---
    
    # Create the two columns for capacity output
    capacity_col_1 = VBox([
        HTML(f'<h3 style="{MAIN_HEADER_STYLE.replace("1.25rem", "1.0rem").replace("color: #4338ca", "color: #10b981")}">2. Capacity Analysis (Healthy Cluster)</h3>'),
        HTML(value=section_2_html)
    ])
    
    capacity_col_2 = VBox([
        HTML(f'<h3 style="{MAIN_HEADER_STYLE.replace("1.25rem", "1.0rem").replace("color: #4338ca", "color: #8b5cf6")}">3. Capacity Analysis (Failure Scenario)</h3>'),
        HTML(value=section_3_html)
    ])
    
    
    # Combine the two columns into a horizontal output
    combined_output = HBox([capacity_col_1, capacity_col_2], 
                           layout=Layout(justify_content='space-between', width='100%'))

    # Placeholder for future performance section
    placeholder = HTML(f'<p style="padding: 10px; color:#6b7280;">Future Performance Analysis sections (4 & 5) will be added here.</p>')

    final_output = VBox([combined_output, placeholder])
    
    return final_output

# ==============================================================================
# 4. WIDGET SETUP AND LAYOUT
# ==============================================================================

if __name__ == '__main__':
    # Add NODES_LOST to the widget map for use in the display constraint check
    widget_ids = list(config.INPUT_CONFIG.keys())
    widget_map: Dict[str, Any] = {}
    for id in widget_ids:
        widget_map[id] = create_slider(id)
        
    # 1. Assemble Input Panels
    topology_box = VBox([
        HTML(f'<div style="{TITLE_STYLE}">Topology</div>'), 
        widget_map['RF'], widget_map['NPC'], widget_map['DPN'], widget_map['DS'],
        HTML('<hr style="margin: 10px 0; border-color: #bfdbfe;">'),
        HTML(f'<div style="{TITLE_STYLE}; color: #8b5cf6;">Resilience Input</div>'),
        widget_map['NODES_LOST'],
        HTML('<p style="font-size: 0.8em; color: #6b7280; margin-top: 5px;">Nodes Lost must be ≤ Nodes per Cluster.</p>')
    ], layout=Layout(width=LAYOUT_WIDTH, border=CARD_STYLE_TPL))

    workload_box = VBox([
        HTML(f'<div style="{TITLE_STYLE}; color: #ec4899;">Workload Inputs</div>'), 
        widget_map['MOC'], widget_map['ARS'], widget_map['ASEO'], widget_map['NSI'],
        HTML('<hr style="margin: 10px 0; border-color: #fbcfe8;">'),
        widget_map['TP'],
    ], layout=Layout(width=LAYOUT_WIDTH, border=CARD_STYLE_WKL))

    server_box = VBox([
        HTML(f'<div style="{TITLE_STYLE}; color: #14b8a6;">Server Specs & Overhead</div>'), 
        widget_map['AMPN'],
        HTML('<hr style="margin: 10px 0; border-color: #99f6e4;">'),
        HTML(f'<p style="font-size: 0.9em; color: #6b7280;">{config.DISPLAY_NAMES["CSOP"]}: {config.FIXED_CONSTANTS["CSOP"]*100:.2f}%</p>'),
        HTML(f'<p style="font-size: 0.9em; color: #6b7280;">{config.DISPLAY_NAMES["OMP"]}: {config.FIXED_CONSTANTS["OMP"]*100:.2f}%</p>'),
    ], layout=Layout(width=LAYOUT_WIDTH, border=CARD_STYLE_SERVER))

    # 2. Interactive Output Area 
    output_container = interactive_output(
        calculate_and_display, 
        {k: widget_map[k] for k in widget_ids} # Maps all widgets used
    )

    # 3. Display Final Layout
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
            output_container
        ])
    ])

    # Display the application
    display(final_layout)
