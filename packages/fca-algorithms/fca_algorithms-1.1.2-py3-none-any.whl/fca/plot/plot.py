import networkx as nx
from networkx.drawing import to_latex

from collections import deque
from matplotlib import pyplot as plt
from random import randint

from ..border_hasse import calculate_hasse


def plot_relational_attributes(
    lattices, sizes_of_lattices, G, pos, ax, edge_colours=None
):
    edges_to_add = []

    if edge_colours is None:
        edge_colours = []

    edges_by_colour = []

    edges_by_style = ["--", "-.", ":"]
    for i, lattice in enumerate(lattices):
        for j, concept in enumerate(lattice.concepts):
            for attr_id in concept.A:
                attr = concept.context.A[attr_id]
                if hasattr(
                    attr, "concepts"
                ):  # This is to avoid importing RelationalAttribute (circular dependency)
                    number_of_relations = len(attr.concepts)
                    for _ in range(len(edge_colours), number_of_relations):
                        edge_colours.append("#%06X" % randint(0, 0xFFFFFF))
                    for l, tpl in enumerate(attr.concepts):
                        lattice_id, concept_id, c = tpl
                        idx_offset = 0 if i == 0 else sizes_of_lattices[i - 1]
                        idx_target_offset = (
                            0 if lattice_id == 0 else sizes_of_lattices[lattice_id - 1]
                        )
                        source_concept_id = j + idx_offset
                        target_concept_id = concept_id + idx_target_offset
                        if len(edges_by_colour) <= l:
                            edges_by_colour.append([])
                        if source_concept_id == target_concept_id:
                            continue
                        if target_concept_id not in G.neighbors(source_concept_id):
                            G.add_edge(source_concept_id, target_concept_id)
                            edges_by_colour[l].append(
                                (source_concept_id, target_concept_id)
                            )
                            edges_to_add.append((source_concept_id, target_concept_id))

    for i, edges in enumerate(edges_by_colour):
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=edges,
            width=3,
            alpha=0.7,
            edge_color=edge_colours[i],
            style=edges_by_style,
            arrowsize=13,
            connectionstyle="arc3,rad=0.2",
            ax=ax,
        )
        ax.plot(
            [], color=edge_colours[i], linestyle=edges_by_style[i % len(edges_by_style)]
        )

    legend = ax.legend(
        [f"{i}" for i in range(len(edge_colours))],
        fontsize=14,
        markerscale=2,
        loc="upper left",
    )

    # Let's only pass the text here
    legend.set_title("Relation indexes")

    # Object of class 'matplotlib.text.Text'. We can use any of the methods
    # we have used for the label texts above.
    title = legend.get_title()
    title.set_color("black")
    title.set_family("Roboto Mono")
    title.set_weight("bold")
    title.set_size(18)

    # Customize legend patch
    legend.legendPatch.set_facecolor("#d1afe8")
    legend.legendPatch.set_edgecolor("#a9a9a9")
    legend.legendPatch.set_linewidth(3)

    return edges_to_add


def plot_lattices(lattices, edge_colours=None):
    sizes_of_lattices = [len(lattice.concepts) for lattice in lattices]
    fig, ax, offset = None, None, 0
    G, pos = nx.DiGraph(), dict()
    for i, lattice in enumerate(lattices):
        idx_offset = 0 if fig is None else idx_offset + sizes_of_lattices[i - 1]
        fig, ax, diameter = lattice.plot(
            show_plot=False,
            fig=fig,
            ax=ax,
            offset=offset,
            idx_offset=idx_offset,
            G=G,
            pos=pos,
        )
        offset += diameter

    edges_to_add = plot_relational_attributes(
        lattices, sizes_of_lattices, G, pos, ax, edge_colours=edge_colours
    )

    plt.show()


def plot_from_hasse(
    hasse,
    concepts_by_id,
    only_attributes=True,
    show_plot=True,
    save_plot: str = None,
    ax=None,
    fig=None,
    offset=0,
    idx_offset=0,
    G=None,
    pos=None,
    amount_of_objects=None,
    amount_of_attributes=None,
    print_latex=False,
):
    if G is None:
        G = nx.DiGraph()

    if pos is None:
        pos = dict()

    for u in range(len(hasse)):
        G.add_node(u + idx_offset, size=10)

    edges_to_add = []
    for u in range(len(hasse)):
        for w in hasse[u]:
            G.add_edge(u + idx_offset, w + idx_offset)
            edges_to_add.append((u + idx_offset, w + idx_offset))

    top_node_idx = look_for_top_node_idx(concepts_by_id, amount_of_objects)
    bottom_node_idx = look_for_bottom_node_idx(concepts_by_id, amount_of_attributes)
    distances, diameter = _compute_distances(
        hasse, from_node=top_node_idx, to_node=bottom_node_idx
    )
    middle = diameter / 2
    for i in range(len(distances)):
        level_i_len = len(distances[i])
        new_middle = level_i_len / 2
        for idx, node in enumerate(distances[i]):
            horizontal_position = idx / level_i_len
            pos[node + idx_offset] = (
                horizontal_position * level_i_len - new_middle,
                -i,
            )

    # FIXME: this is for RCA
    if offset > 0:
        pos[idx_offset] = (
            pos[len(hasse) - 1 + idx_offset][0] + offset,
            len(distances) + (1 if len(distances[-1]) == 0 else 0),
        )

    if ax is None or fig is None:
        fig, ax = plt.subplots()
    nx.draw_networkx_edges(
        G, pos, edgelist=edges_to_add, edge_color="blue", arrowsize=13, width=1.3, ax=ax
    )
    nodes = nx.draw_networkx_nodes(G, pos=pos, ax=ax)

    annot = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(20, 20),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="w"),
        arrowprops=dict(arrowstyle="->"),
    )
    annot.set_visible(False)

    edges_annotations = (
        []
    )  # Here I can perhaps put the relational edges as annotation and hide/show them on hover

    def update_annot(ind):
        node = ind["ind"][0]
        xy = pos[node]
        annot.xy = xy
        node_attr = {"node": node}
        node_attr.update(
            {
                "A": concepts_by_id[node].hr_A(),
            }
        )
        if not only_attributes:
            node_attr.update(
                {
                    "O": concepts_by_id[node].hr_O(),
                }
            )
        text = "\n".join(f"{k}: {v}" for k, v in node_attr.items())
        annot.set_text(text)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = nodes.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    # plt.savefig('this.png')
    if show_plot:
        plt.show()

    if save_plot:
        if save_plot.endswith("dot"):
            nx.nx_pydot.write_dot(G, save_plot)

        if save_plot.endswith("gexf"):
            for node in G:
                G.nodes[node]["viz"] = dict()
                G.nodes[node]["viz"]["position"] = {
                    "x": float(pos[node][0]) * 100,
                    "y": float(pos[node][1]) * 100,
                }
                concept = concepts_by_id[node]
                attributes_so_far = set(concept.A)
                for p in concept.parents:
                    attributes_so_far.difference_update(p.A)
                G.nodes[node][
                    "label"
                ] = f"{','.join([concept.context.A[j] for j in attributes_so_far])}"
            nx.write_gexf(G, save_plot)

    if print_latex:
        print(to_latex(G))

    return fig, ax, diameter


def _compute_distances(hasse, from_node=0, to_node=None):
    if to_node is None:
        to_node = len(hasse) - 1
    distances = [None for _ in range(len(hasse))]
    distances[from_node] = 0
    queue = deque([from_node])
    maximum_distance = 0
    while queue:
        u = queue.popleft()
        for w in hasse[u]:
            if distances[w] is None:
                distances[w] = distances[u] + 1
                maximum_distance = max(maximum_distance, distances[w])
                queue.append(w)
    res_distances = [[] for _ in range(maximum_distance + 1)]
    diameter = 0
    for node in range(len(hasse)):
        if distances[node] is None:
            # This is done to put the unreachable nodes in the plot
            # which could exist due to the incrementallity
            distances[node] = 1
        res_distances[distances[node]].append(node)
        diameter = max(diameter, len(res_distances[distances[node]]))

    if (
        to_node not in res_distances[maximum_distance]
        and len(res_distances[maximum_distance]) > 1
    ):
        current_distance = maximum_distance
        removed = False
        while not removed:
            if to_node in res_distances[current_distance]:
                res_distances[current_distance].remove(to_node)
                res_distances.append([to_node])
                removed = True
            else:
                current_distance -= 1
    return res_distances, diameter


def to_node(u, concepts_by_id):
    return str(concepts_by_id[u])


def look_for_top_node_idx(concepts_by_id, amount_of_objects):
    if amount_of_objects is None:
        return 0
    for i, c in enumerate(concepts_by_id):
        if len(c.O) == amount_of_objects:
            return i


def look_for_bottom_node_idx(concepts_by_id, amount_of_attributes):
    if amount_of_attributes is None:
        return len(concepts_by_id) - 1
    for i, c in enumerate(concepts_by_id):
        if len(c.A) == amount_of_attributes:
            return i
