import sqlparse
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objs as go
from plotly.offline import iplot
from tdfs4ds.utils.lineage import analyze_sql_query
def display_table(df, max_widths=[25, 55, 10], header=["Feature Database", "Feature Table", "# rows"]):
    """
    Display a pandas DataFrame as a formatted table in the console.

    This function formats each row of the DataFrame according to specified maximum column widths.
    It prints out the DataFrame in a tabular format with a header.

    Parameters:
    df (pandas.DataFrame): The DataFrame to be displayed.
    max_widths (list of int, optional): Maximum width of each column in characters. Defaults to [25, 55, 10].
    header (list of str, optional): Column headers to be displayed. Defaults to ["Feature Database", "Feature Table", "# rows"].

    Returns:
    None: This function only prints the table and does not return anything.
    """

    # Create a format string for each row based on the maximum column widths
    row_format = " | ".join("{:<" + str(width) + "." + str(width) + "}" for width in max_widths)

    # Print an empty line for spacing
    print('\n')

    # Print the header row using the format string
    print(row_format.format(*header))

    # Print a separator line, with length based on the total width of all columns and separators
    print("-" * (sum(max_widths) + 2 * (len(max_widths) - 1)))  # Account for separators (' | ')

    # Iterate over each row in the DataFrame and print it using the format string
    for _, row in df.iterrows():
        print(row_format.format(*[str(row[col]) for col in df.columns]))

    # Print an empty line for spacing at the end
    print('\n')
    return

def plot_graph(tddf, root_name='ml__'):
    """
    Visualizes a given dataframe's source-target relationships using a Sankey diagram.

    :param df: pd.DataFrame
        The input dataframe should have two columns: 'source' and 'target'.
        Each row represents a relationship between a source and a target.

    :Note: This function makes use of Plotly's Sankey diagram representation for visualization.

    :return: None
        The function outputs the Sankey diagram and doesn't return anything.
    """

    tddf._DataFrame__execute_node_and_set_table_name(tddf._nodeid, tddf._metaexpr)

    df, node_info = analyze_sql_query(tddf.show_query(), df=None, target=tddf._table_name, root_name=root_name)

    if df['source'].values[0].lower() == df['target'].values[0].lower():
        df = df.iloc[1::, :]

    # Create a list of unique labels combining sources and targets from the dataframe
    labels = list(pd.concat([df['source'], df['target']]).unique())

    # Creating a mapping of node labels to additional information
    node_info_dict = pd.DataFrame(node_info).set_index('target').T.to_dict()

    # Create hovertext for each label using the node_info_map
    hovertexts = [
        f"Columns:<br> {','.join(node_info_dict[label]['columns'])}<br> Query: {sqlparse.format(node_info_dict[label]['query'], reindent=True, keyword_case='upper')}".replace(
            '\n', '<br>').replace('PARTITION BY', '<br>PARTITION BY').replace('USING', '<br>USING').replace(' ON',
                                                                                                            '<br>ON').replace(') ',')<br>').replace(')<br>AS',') AS').replace(', ',',<br>')

        if label in node_info_dict else '' for label in labels]

    # Use the length of 'columns' for the value (thickness) of each link
    values = df['source'].apply(lambda x: len(node_info_dict[x]['columns']) if x in node_info_dict else 1)

    # Convert source and target names to indices based on their position in the labels list
    source_indices = df['source'].apply(lambda x: labels.index(x))
    target_indices = df['target'].apply(lambda x: labels.index(x))

    # Construct the Sankey diagram with nodes (sources & targets) and links (relationships)
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,  # Space between the nodes
            thickness=20,  # Node thickness
            line=dict(color="black", width=0.5),  # Node border properties
            label=labels,  # Labels for nodes
            color="blue",  # Node color
            # hovertext=link_hovertexts  # set hover text for nodes
            customdata=hovertexts,
            hovertemplate=' %{customdata}<extra></extra>',
        ),
        link=dict(
            source=source_indices,  # Link sources
            target=target_indices,  # Link targets
            value=values  # [1] * len(df)  # Assuming equal "flow" for each link. Can be modified if needed.
        )
    )])

    # Customize the layout, such as setting the title and font size
    fig.update_layout(title_text="Hierarchical Data Visualization", font_size=10)

    # Display the Sankey diagram
    fig.show()

    return df



def visualize_graph(df, layout_choice='linear_depth_layout'):
    # Create a directed graph from the DataFrame
    G = nx.from_pandas_edgelist(df, 'source', 'target', create_using=nx.DiGraph())

    # Identifying sources, leaves, and multi-leaf connections
    sources = {node for node, in_degree in G.in_degree() if in_degree == 0}
    leaves = {node for node, out_degree in G.out_degree() if out_degree == 0}
    multi_leaf_connections = {node for node in G.nodes() if sum(1 for _ in G.successors(node) if _ in leaves) > 1}

    # Select layout based on layout_choice
    if layout_choice == "linear_depth_layout":
        pos = linear_depth_layout(G, sources, leaves, multi_leaf_connections)
    elif layout_choice == "segmented_linear_layout":
        pos = segmented_linear_layout(G, sources, leaves, multi_leaf_connections)
    elif layout_choice == "radial_layout":
        pos = radial_layout(G, sources, leaves, multi_leaf_connections)
    else:
        raise ValueError("Invalid layout choice")

    # Prepare plotly traces for edges and nodes
    edge_trace, node_trace = prepare_plotly_traces(G, pos, sources, leaves, multi_leaf_connections)

    # Create the figure with adjusted margins
    fig = go.Figure(data=edge_trace + [node_trace],
                    layout=go.Layout(
                        title='Interactive Graph Visualization',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=40, l=60, r=60, t=40),  # Increase margins
                        annotations=[dict(
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.05, 1.05]),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),

                        # Optional: Adjust the width and height if needed
                        width=1200,  # Width in pixels
                        height=700,  # Height in pixels
                    ))

    # Display the figure
    iplot(fig)

# Define your layout functions here (custom_layout, custom_layout2, radial_layout)
def linear_depth_layout(G, sources, leaves, multi_leaf_connections):
    pos = {}
    left_side = 0.1  # x-coordinate for sources
    right_side = 0.9  # x-coordinate for leaves

    # Initialize positions for sources on the left
    source_y_positions = np.linspace(0, 1, len(sources) + 2)[1:-1]
    for i, source in enumerate(sources):
        pos[source] = np.array([left_side, source_y_positions[i]])

    # Calculate depths based on maximal depth + 1 of direct ancestors
    depths = {node: 0 for node in sources}  # Start with depth 0 for source nodes
    for node in nx.topological_sort(G):
        if node not in sources:
            # Maximum depth of direct ancestors + 1
            depths[node] = max([depths[pred] for pred in G.predecessors(node)], default=-1) + 1

    # Determine the range of depths and allocate positions
    max_depth = max(depths.values(), default=0)
    depth_positions = np.linspace(left_side, right_side, max_depth + 2)[1:-1]  # Exclude positions for sources

    # Assign positions for non-leaf nodes based on their depth
    for node, depth in depths.items():
        if node not in leaves:
            y_positions = np.linspace(0, 1, sum(1 for d in depths.values() if d == depth) + 2)[1:-1]
            idx = list(sorted(node for node, d in depths.items() if d == depth)).index(node)
            pos[node] = np.array([depth_positions[depth], y_positions[idx]])

    # Initialize positions for leaves on the right
    leaf_y_positions = np.linspace(0, 1, len(leaves) + 2)[1:-1]
    for i, leaf in enumerate(leaves):
        pos[leaf] = np.array([right_side, leaf_y_positions[i]])

    return pos


def segmented_linear_layout(G, sources, leaves, multi_leaf_connections):
    pos = {}
    # Define the horizontal positions for each group
    left_side = 0.1  # x-coordinate for sources
    mid_left = 0.3  # x-coordinate for regular nodes
    mid_right = 0.7  # x-coordinate for nodes connected to more than one leaf
    right_side = 0.9  # x-coordinate for leaves

    # Initialize positions for sources on the left
    source_y_positions = np.linspace(0, 1, len(sources) + 2)[1:-1]
    for i, source in enumerate(sources):
        pos[source] = np.array([left_side, source_y_positions[i]])

    # Initialize positions for regular nodes (blue) in the middle-left
    regular_nodes = [node for node in G.nodes() if
                     node not in sources and node not in leaves and node not in multi_leaf_connections]
    regular_y_positions = np.linspace(0, 1, len(regular_nodes) + 2)[1:-1]
    for i, node in enumerate(regular_nodes):
        pos[node] = np.array([mid_left, regular_y_positions[i]])

    # Initialize positions for nodes connected to more than one leaf (purple) in the middle-right
    multi_leaf_y_positions = np.linspace(0, 1, len(multi_leaf_connections) + 2)[1:-1]
    for i, node in enumerate(multi_leaf_connections):
        pos[node] = np.array([mid_right, multi_leaf_y_positions[i]])

    # Initialize positions for leaves on the right
    leaf_y_positions = np.linspace(0, 1, len(leaves) + 2)[1:-1]
    for i, leaf in enumerate(leaves):
        pos[leaf] = np.array([right_side, leaf_y_positions[i]])

    return pos


def radial_layout(G, sources, leaves, multi_leaf_connections):
    pos = {}
    center = np.array([0.5, 0.5])  # Center of the layout

    # Calculate depths based on maximal depth + 1 of direct ancestors
    depths = {node: 0 for node in sources}  # Start with depth 0 for source nodes
    for node in nx.topological_sort(G):
        if node not in sources:
            # Maximum depth of direct ancestors + 1
            depths[node] = max([depths[pred] for pred in G.predecessors(node)], default=-1) + 1
    max_depth = max(depths.values(), default=0)

    # Define the radius for the small circle around the center for sources
    source_radius = 0.05 if len(sources) > 1 else 0  # Only use a circle if there are multiple sources
    radius_increment = (0.4 - source_radius) / (max_depth + 1)  # Radius increment per depth level

    # Positioning sources in a small circle around the center
    source_angle_gap = 2 * np.pi / len(sources)
    for i, source in enumerate(sources):
        angle = i * source_angle_gap
        pos[source] = center + source_radius * np.array([np.cos(angle), np.sin(angle)])

    # Positioning nodes based on their depth
    for depth in range(1, max_depth + 1):  # Start from 1 as 0 is for sources
        nodes_at_depth = [node for node, d in depths.items() if d == depth]
        angle_gap = 2 * np.pi / (len(nodes_at_depth) + 1)
        for i, node in enumerate(nodes_at_depth):
            angle = i * angle_gap
            pos[node] = center + (source_radius + radius_increment * depth) * np.array([np.cos(angle), np.sin(angle)])

    # Ensuring leaves are positioned at the outermost layer
    leaf_angle_gap = 2 * np.pi / (len(leaves) + 1)
    for i, leaf in enumerate(leaves):
        angle = i * leaf_angle_gap
        pos[leaf] = center + (source_radius + radius_increment * (max_depth + 1)) * np.array(
            [np.cos(angle), np.sin(angle)])

    return pos
# Define a helper function to prepare Plotly traces
def prepare_plotly_traces(G, pos, sources, leaves, multi_leaf_connections):
    edge_trace = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace.append(go.Scatter(x=[x0, x1, None], y=[y0, y1, None],
                                     mode='lines',
                                     line=dict(width=0.5, color='gray'),
                                     hoverinfo='none',
                                     marker=dict(size=0),
                                     line_shape='spline',
                                     ))

    node_x, node_y, node_text, node_color = [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        if node in sources:
            node_color.append('green')  # Source in green
        elif node in leaves:
            node_color.append('orange')  # Leaf in orange
        elif node in multi_leaf_connections:
            node_color.append('purple')  # Node with multiple leaf connections in purple
        else:
            node_color.append('blue')  # Regular node in blue

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        marker=dict(color=node_color, size=10),
        textposition="bottom center"
    )

    return edge_trace, node_trace
