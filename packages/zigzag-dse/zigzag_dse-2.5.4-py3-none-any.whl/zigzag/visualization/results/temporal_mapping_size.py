from zigzag.classes.cost_model.cost_model import CostModelEvaluation
from zigzag.utils import pickle_load

def get_temporal_mapping_sizes(cme: CostModelEvaluation):
    """
    Return the size of the temporal tiles at """
    tm_sizes = {}
    layer = cme.layer
    tm = cme.temporal_mapping
    for layer_op, nested_loops in tm.mapping_dic_stationary.items():
        sizes = []
        loops = []
        for l in nested_loops:
            loops += l
            d = {dim: 1 for dim in layer.loop_dim_list}
            for loop in loops:
                loop_dim, loop_size = loop
                d[loop_dim] = d.get(loop_dim, 1) * loop_size
            size = layer.calc_tensor_size(layer_op, d)
            sizes.append(size)
        tm_sizes[layer_op] = sizes
    return tm_sizes

if __name__ == "__main__":
    # Load in a random CostModelEvaluation
    cmes = pickle_load("zigzag/visualization/list_of_cmes.pickle")
    cme = cmes[0]
    sizes = get_temporal_mapping_sizes(cme)
    print(sizes)
    # Prints: {'O': [1, 2352, 2352], 'W': [1, 121, 1452], 'I': [3969, 3969]}