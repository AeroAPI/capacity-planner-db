"""
Main execution script for the interactive Capacity Planner GUI (Colab/Jupyter). v2

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
DIVIDER_STYLE = "border-top: 1px solid #E5E7EB; margin-top: 10px; padding-top: 10px;"

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

def render_html_performance(title: str, results: Dict[str, float], tput_key: str, iops_key: str, node_tput_key: str, node_iops_key: str, is_failure: bool = False, inputs: Dict[str, Any] = None):
    """Generates HTML for performance cards (Sections 4 & 5)."""
    
    tput_val = results.get(tput_key, 0)
    iops_val = results.get(iops_key, 0)
    node_tput_val = results.get(node_tput_key, 0)
    node_iops_val = results.get(node_iops_key, 0)
    
    
    def format_performance(value, unit):
        if not math.isfinite(value) or value == 0: return 'N/A ' + unit
        return f"{value:,.0f} {unit}"

    color_class = "#f97316" if is_failure else "#10b981"
    border_class = "#fecaca" if is_failure else "#bbf7d0"
    
    npc = inputs.get('NPC', 0)
    dpn = inputs.get('DPN', 0)
    lost = inputs.get('NODES_LOST', 0)
    effective_nodes = max(0, npc - lost)

    return f"""
    <div style="{CARD_STYLE_CAPACITY.replace('border-indigo-200', 'border-gray-200').replace('bbf7d0', border_class)}">
        <h4 style="font-weight: bold; color: {color_class}; margin-bottom: 10px;">{title}</h4>
        
        <div style="{DIVIDER_STYLE.replace('10px', '5px')}" >
            <p style="font-weight: 700; color: #374151;">Throughput</p>
            <span style="font-size: 1.5em; font-weight: bold; color: {color_class};">{format_performance(tput_val, 'MB/s')}</span>
        </div>

        <div style="font-size: 0.85em; color: #6B7280; margin-top: 5px;">
            <p>{'Nodes Available' if is_failure else 'Total Nodes'}: <span style="font-weight: 600; color: #1f2937;">{effective_nodes if is_failure else npc}</span></p>
            <p>Throughput per Node: <span style="font-weight: 600; color: #1f2937;">{format_performance(node_tput_val, 'MB/s')}</span></p>
        </div>
        
        <div style="{DIVIDER_STYLE.replace('10px', '5px')}">
            <p style="font-weight: 700; color: #374151;">IOPS</p>
            <span style="font-size: 1.5em; font-weight: bold; color: {color_class};">{format_performance(iops_val, 'K')}</span>
        </div>
         <div style="font-size: 0.85em; color: #6B7280; margin-top: 5px;">
            <p>IOPS per Node: <span style="font-weight: 600; color: #1f2937;">{format_performance(node_iops_val, 'K')}</span></p>
            <p>Devices per Node: <span style="font-weight: 600; color: #1f2937;">{dpn}</span></p>
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
    
    description_text = full_label

    return SliderClass(
        min=config_item['min'],
        max=config_item['max'],
        step=config_item['step'],
        value=config_item['default'],
        description=description_text,
        style=STYLE,
        layout=Layout(width='auto')
    )

# ==============================================================================
# 3. INTERACTIVE CORE LOGIC (Links UI to Calculator)
# ==============================================================================

def calculate_and_display(**kwargs):
    """The function executed by ipywidgets on input change."""
    
    # 1. Calculate Results using the external calculator
    # The MOC value must be converted from 'Billion' back to raw scale before passing to calculator.
    
    # Create clean input dictionary for the calculator (scaling MOC correctly)
    calculator_inputs = kwargs.copy()
    # MOC is input value * 10^9
    calculator_inputs['MOC'] = kwargs['MOC'] * 1000000000 
    # TP is input value (0-100) / 100
    calculator_inputs['TP'] = kwargs['TP'] / 100 
    
    results = calculator.calculate_capacity(calculator_inputs)
    
    # 2. Dynamic Constraint Logic (ensures Nodes Lost <= NPC)
    npc_value = kwargs.get('NPC', config.INPUT_CONFIG['NPC']['default'])
    nodes_lost_value = kwargs.get('NODES_LOST', config.INPUT_CONFIG['NODES_LOST']['default'])
    
    if 'NODES_LOST' in widget_map:
        nodes_lost_widget = widget_map['NODES_LOST']
        nodes_lost_widget.max = npc_value
        if nodes_lost_value > npc_value:
            nodes_lost_widget.value = npc_value
            nodes_lost_value = npc_value
            
    # 3. Get raw inputs for display context
    display_inputs = {
        'NPC': kwargs.get('NPC', 0),
        'DPN': kwargs.get('DPN', 0),
        'NODES_LOST': kwargs.get('NODES_LOST', 0),
    }

    
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
    
    # --- SECTION 4: HEALTHY PERFORMANCE ---
    section_4_html = render_html_performance(
        "Healthy Cluster Peak Performance", results, 'Healthy_TPUT', 'Healthy_IOPS', 'TPUT_Node', 'IOPS_Node', is_failure=False, inputs=display_inputs
    )
    
    # --- SECTION 5: FAILURE PERFORMANCE ---
    section_5_html = render_html_performance(
        "Failure Remaining Performance", results, 'Fail_TPUT', 'Fail_IOPS', 'TPUT_Node', 'IOPS_Node', is_failure=True, inputs=display_inputs
    )


    # --- ASSEMBLE FINAL OUTPUT ---
    
    # ROW 2 (Capacity)
    capacity_col_1 = VBox([
        HTML(f'<h3 style="{MAIN_HEADER_STYLE.replace("1.25rem", "1.0rem").replace("color: #4338ca", "color: #10b981")}">2. Capacity Analysis (Healthy Cluster)</h3>'),
        HTML(value=section_2_html)
    ])
    capacity_col_2 = VBox([
        HTML(f'<h3 style="{MAIN_HEADER_STYLE.replace("1.25rem", "1.0rem").replace("color: #4338ca", "color: #8b5cf6")}">3. Capacity Analysis (Failure Scenario)</h3>'),
        HTML(value=section_3_html)
    ])
    combined_capacity_output = HBox([capacity_col_1, capacity_col_2], 
                           layout=Layout(justify_content='space-between', width='100%'))

    # ROW 3 (Performance)
    performance_col_1 = VBox([
        HTML(f'<h3 style="{MAIN_HEADER_STYLE.replace("1.25rem", "1.0rem").replace("color: #4338ca", "color: #f97316")}">4. Performance Analysis (Healthy Cluster)</h3>'),
        HTML(value=section_4_html)
    ])
    performance_col_2 = VBox([
        HTML(f'<h3 style="{MAIN_HEADER_STYLE.replace("1.25rem", "1.0rem").replace("color: #4338ca", "color: #ef4444")}">5. Performance Analysis (Failure Scenario)</h3>'),
        HTML(value=section_5_html)
    ])
    combined_performance_output = HBox([performance_col_1, performance_col_2], 
                           layout=Layout(justify_content='space-between', width='100%'))

    # ROW 4 (Calculations) - Placeholder text added for completeness
    calculations_html = HTML(f'<p style="padding: 10px; color:#6b7280;">6. Calculations and Definitions Table would display here.</p>')

    
    final_output = VBox([combined_capacity_output, combined_performance_output, calculations_html])
    
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
        HTML(f'<p style="font-size: 0.9em; color: #6b7280;">{config.DISPLAY_NAMES["CSOP"]}: {config.CLUSTER_STORAGE_OVERHEAD_PCT*100:.2f}%</p>'),
        HTML(f'<p style="font-size: 0.9em; color: #6b7280;">{config.DISPLAY_NAMES["OMP"]}: {config.OVERHEAD_MEMORY_PCT*100:.2f}%</p>'),
        HTML(f'<p style="font-size: 0.9em; color: #6b7280;">Throughput per Disk: {config.THROUGHPUT_PER_DISK_MBPS:,.0f} MB/s</p>'),
        HTML(f'<p style="font-size: 0.9em; color: #6b7280;">IOPS per Disk: {config.IOPS_PER_DISK_K:,.0f} K</p>'),
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
