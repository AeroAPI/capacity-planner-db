"""
Main Interactive Widget (v116).

Sets up the ipywidgets layout and displays the calculated capacity and 
performance metrics for both Healthy and Failure Scenarios, using modular imports.
"""
from ipywidgets import IntSlider, FloatSlider, VBox, HBox, Layout, HTML, interactive_output
from IPython.display import display
from typing import Dict, Any
import math
import config
import calculator

# ==============================================================================
# 1. WIDGET SETUP AND LAYOUT HELPERS
# ==============================================================================

# --- STYLING ---
LAYOUT_WIDTH = '32%'
STYLE = {'description_width': 'initial'}
TITLE_STYLE = "font-weight: bold; margin-bottom: 5px; color: #1e40af;"
MAIN_HEADER_STYLE = "font-weight: 600; font-size: 1.25rem; color: #4338ca; margin-bottom: 1rem;"

CARD_STYLE_TPL = "border: 1px solid #bfdbfe; border-radius: 0.5rem; padding: 1.5rem; background-color: white;"
CARD_STYLE_WKL = "border: 1px solid #fbcfe8; border-radius: 0.5rem; padding: 1.5rem; background-color: white;"
CARD_STYLE_SERVER = "border: 1px solid #99f6e4; border-radius: 0.5rem; padding: 1.5rem; background-color: white;"


def create_slider(id: str) -> IntSlider | FloatSlider:
    """
    Helper to create a slider widget based on the INPUT_CONFIG, 
    using DISPLAY_NAMES for the label.
    """
    cfg = config.INPUT_CONFIG[id]
    is_float = cfg.get('step', 1) < 1.0
    SliderClass = FloatSlider if is_float else IntSlider
    
    full_label = config.DISPLAY_NAMES.get(id, id)
    description_text = full_label

    return SliderClass(
        min=cfg['min'],
        max=cfg['max'],
        step=cfg['step'],
        value=cfg['default'],
        description=description_text,
        style=STYLE,
        layout=Layout(width='auto')
    )

def render_html_metric(title: str, result_value: float, raw_used: float, raw_total: float, color_class: str):
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
        if value < 0.1 and value != 0:
            return f"{value * 1024:.2f} MB"
        return f"{value:.2f} GB"

    return f"""
    <div style="border: 1px solid #E5E7EB; border-radius: 8px; padding: 15px; margin-bottom: 15px; background-color: white;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h4 style="font-weight: bold; color: #374151;">{title}</h4>
            <span style="font-size: 1.5em; font-weight: bold; color: {color_class};">{util_display} {util_status}</span>
        </div>
        <div style="background-color: #E5E7EB; border-radius: 4px; height: 10px; margin-bottom: 8px;">
            <div style="width: {bar_width}%; height: 10px; border-radius: 4px; background-color: {color_class};"></div>
        </div>
        <div style="font-size: 0.85em; color: #6B7280;">
            <p>Used: <span style="font-weight: 600; color: #1f2937;">{format_capacity(raw_used)}</span></p>
            <p>Available: <span style="font-weight: 600; color: #1f2937;">{format_capacity(raw_total)}</span></p>
        </div>
    </div>
    """

def render_performance_metric(title: str, cluster_value: float, node_value: float, effective_nodes: int, node_loss: int, unit: str, color_class: str, fail_scenario=False):
    """Generates HTML for a single performance card (Section 4/5)."""
    
    def format_perf(value):
        if not math.isfinite(value) or math.isnan(value):
            return "N/A"
        return f"{value:,.0f}"
    
    color_style = "color: #dc2626;" if fail_scenario else "color: #f97316;"

    content_rows = [
        f"<p>Nodes: <span style='font-weight: 600;'>{effective_nodes:,}</span></p>",
        f"<p>Per Node: <span style='font-weight: 600;'>{format_perf(node_value)} {unit}</span></p>",
    ]
    if fail_scenario:
        content_rows.append(f"<p>Nodes Lost: <span style='font-weight: 600;'>{node_loss:,}</span></p>")
        
    return f"""
    <div style="border: 1px solid #E5E7EB; border-radius: 8px; padding: 15px; margin-bottom: 15px; background-color: white;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h4 style="font-weight: bold; color: #374151;'>{title}</h4>
            <span style="font-size: 1.5em; font-weight: bold; {color_style};">{format_perf(cluster_value)} {unit}</span>
        </div>
        <div style="font-size: 0.85em; color: #6B7280; padding-top: 5px; border-top: 1px solid #E5E7EB;">
            {''.join(content_rows)}
        </div>
    </div>
    """

def get_color_capacity(utilization, fail_scenario=False):
    """Determines color for capacity utilization text."""
    if not math.isfinite(utilization): return "#dc2626"
    if fail_scenario:
        if utilization > 100: return "#dc2626"  # Red-700
        return "#f87171" # Red-400
    else:
        if utilization > 90: return "#dc2626"  # Red-600
        if utilization > 75: return "#f97316"   # Orange-500
        return "#10b981" # Green-600

def get_color_performance(value, fail_scenario=False):
    """Determines color for performance text based on value (higher is generally better)."""
    if not math.isfinite(value): return "#dc2626"
    if fail_scenario:
        return "#b91c1c" # Deep Red for Failure
    return "#f97316" # Orange for Healthy Performance


def calculate_and_display(**kwargs):
    """The function executed by ipywidgets on input change."""
    
    # 1. Calculate Results
    results = calculator.calculate_capacity(kwargs)
    
    # 2. Dynamic Constraint Logic (ensures Nodes Lost <= NPC)
    npc_value = kwargs.get('NPC', config.INPUT_CONFIG['NPC']['default'])
    nodes_lost_value = kwargs.get('NODES_LOST', config.INPUT_CONFIG['NODES_LOST']['default'])
    
    nodes_lost_widget = widget_map['NODES_LOST']
    nodes_lost_widget.max = npc_value
    
    if nodes_lost_value > npc_value:
        nodes_lost_widget.value = npc_value
        nodes_lost_value = npc_value
        
    # 3. Render Output
    
    # --- SECTION 2: HEALTHY CAPACITY ---
    section_2_html = VBox([
        HTML(value=f'<h4 style="color: #10b981; font-weight: bold; margin-bottom: 0.5rem;">2. Capacity Analysis (Healthy Cluster)</h4>'),
        HTML(value=render_html_metric("Actual Storage Utilization (%)", results['ASU'], results['TDS'], results['TSAPC'], get_color_capacity(results['ASU']))),
        HTML(value=render_html_metric("Total Memory Base Utilization (%)", results['TMBU'], results['TMU'], results['TMAPC'], get_color_capacity(results['TMBU']))),
        HTML(value=render_html_metric("Memory Utilization w/ Tombstones (%)", results['TMUT'], results['TMT'], results['AMC'], get_color_capacity(results['TMUT'])))
    ])

    # --- SECTION 3: FAILURE CAPACITY ---
    section_3_html = VBox([
        HTML(value=f'<h4 style="color: #8b5cf6; font-weight: bold; margin-bottom: 0.5rem;">3. Capacity Analysis (Failure Scenario)</h4>'),
        HTML(value=render_html_metric("Failure Storage Utilization (%)", results['Fail_ASU'], results['TDS'], results['Fail_TSAPC'], get_color_capacity(results['Fail_ASU'], True))),
        HTML(value=render_html_metric("Failure Memory Base Utilization (%)", results['Fail_TMBU'], results['TMU'], results['Fail_AMC'], get_color_capacity(results['Fail_TMBU'], True))),
        HTML(value=render_html_metric("Failure Memory w/ Tombstones (%)", results['Fail_TMUT'], results['TMT'], results['Fail_AMC'], get_color_capacity(results['Fail_TMUT'], True)))
    ])

    # --- SECTION 4: HEALTHY PERFORMANCE ---
    section_4_html = VBox([
        HTML(value=f'<h4 style="color: #f97316; font-weight: bold; margin-bottom: 0.5rem;">4. Performance Analysis (Healthy Cluster)</h4>'),
        HTML(value=render_performance_metric("Peak Cluster Throughput (MB/s)", results['Healthy_TPUT'], results['TPUT_Node'], npc_value, 0, "MB/s", get_color_performance(results['Healthy_TPUT']))),
        HTML(value=render_performance_metric("Estimated Cluster IOPS (K)", results['Healthy_IOPS'], results['IOPS_Node'], npc_value, 0, "K", get_color_performance(results['Healthy_IOPS']))),
    ])
    
    # --- SECTION 5: FAILURE PERFORMANCE ---
    section_5_html = VBox([
        HTML(value=f'<h4 style="color: #dc2626; font-weight: bold; margin-bottom: 0.5rem;">5. Performance Analysis (Failure Scenario)</h4>'),
        HTML(value=render_performance_metric("Remaining Throughput (MB/s)", results['Fail_TPUT'], results['TPUT_Node'], npc_value - nodes_lost_value, nodes_lost_value, "MB/s", get_color_performance(results['Fail_TPUT'], True))),
        HTML(value=render_performance_metric("Remaining IOPS (K)", results['Fail_IOPS'], results['IOPS_Node'], npc_value - nodes_lost_value, nodes_lost_value, "K", get_color_performance(results['Fail_IOPS'], True))),
    ])
    
    # --- ASSEMBLE FINAL OUTPUT ---
    
    # Row 1: Capacity (S2/S3)
    capacity_row = HBox([section_2_html, section_3_html], layout=Layout(justify_content='space-between', width='100%'))
    
    # Row 2: Performance (S4/S5)
    performance_row = HBox([section_4_html, section_5_html], layout=Layout(justify_content='space-between', width='100%'))
    
    output_vbox = VBox([
        capacity_row,
        HTML('<hr style="margin: 20px 0; border-color: #e5e7eb;">'),
        performance_row,
        HTML('<hr style="margin: 20px 0; border-color: #e5e7eb;">'),
        # Placeholder for Section 6 (Calculations)
        HTML(f'<h3 style="font-weight: bold; color: #6b7280;">6. Calculations and Definitions (To be built)</h3>'),
    ])
    
    return output_vbox

# [REMAINDER OF WIDGET SETUP AND LAYOUT]

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
    HTML(f'<p style="font-size: 0.9em; color: #6b7280;">{config.DISPLAY_NAMES["CSOP"]}: {config.CLUSTER_STORAGE_OVERHEAD_PCT*100:.2f}%</p>'),
    HTML(f'<p style="font-size: 0.9em; color: #6b7280;">{config.DISPLAY_NAMES["OMP"]}: {config.OVERHEAD_MEMORY_PCT*100:.2f}%</p>'),
    HTML(f'<p style="font-size: 0.9em; color: #6b7280;">Throughput per Disk: {config.THROUGHPUT_PER_DISK_MBPS:,} MB/s</p>'),
    HTML(f'<p style="font-size: 0.9em; color: #6b7280;">IOPS per Disk: {config.IOPS_PER_DISK_K:,} K</p>'),
], layout=Layout(width=LAYOUT_WIDTH, border=CARD_STYLE_SERVER))


# 4. Interactive Output Area (Must map all widgets used by calculate_and_display)
output_area = interactive_output(
    calculate_and_display, 
    {k: widget_map[k] for k in widget_ids} # Maps all widgets used
)

# 5. Assemble Final Layout
if __name__ == '__main__':
    display(VBox([
        HTML(f'<h1 style="{MAIN_HEADER_STYLE}">1. System & Workload Configuration</h1>'),
        HBox([
            topology_box,
            workload_box,
            server_box
        ], layout=Layout(justify_content='space-between', width='100%')), 
        
        HTML('<hr style="margin: 20px 0; border-color: #e5e7eb;">'),
        
        HTML(f'<h3 style="{MAIN_HEADER_STYLE}">2. Capacity and Performance Analysis</h3>'),
        output_area
    ]))
