import matplotlib.pyplot as plt
import matplotlib.patches as patches

def visualize_model(model, max_layers_per_subplot=10):
    """
    Visualizes the architecture of a PyTorch model by plotting its layers as colored blocks.

    Parameters:
    - model: The PyTorch model to visualize. The model should be an instance of a class derived from torch.nn.Module.
    - max_layers_per_subplot: The maximum number of layers to display in a single subplot. Default is 10.

    The function parses the model's layers, organizes them into a readable format, and then uses matplotlib to draw a diagram with each layer represented as a block. The layers are arranged vertically, with connections indicated by lines between blocks. This visualization helps in understanding the model's structure at a glance.
    """

    def convert_layers_to_architecture(layers_dict):
        architecture = []
        for name, layer in layers_dict.items():
            if name:
                parent_name = name.rsplit('.', 1)[0] if '.' in name else name
                if not any(parent_name in d.get('parent', '') for d in architecture):
                    layer_info = {"layer": str(layer), "parent": parent_name}
                    architecture.append(layer_info)
        return architecture

    layers_dict = {name: module for name, module in model.named_modules() if name}
    architecture = convert_layers_to_architecture(layers_dict)

    # Determine the number of subplots needed
    num_layers = len(architecture)
    num_subplots = (num_layers + max_layers_per_subplot - 1) // max_layers_per_subplot

    def draw_block(ax, center_x, center_y, width, height, text, color='lightgrey'):
        block = patches.Rectangle((center_x - width / 2, center_y - height / 2), width, height,
                                  linewidth=1, edgecolor='black', facecolor=color)
        ax.add_patch(block)
        ax.text(center_x, center_y, text, ha='center', va='center', fontsize=8, wrap=True)
        return center_y - height / 2

    def draw_architecture(ax, architecture_subset):
        layer_width = 0.8
        layer_height = 0.1
        vertical_spacing = 0.1
        current_y = 0

        for i, layer in enumerate(architecture_subset):
            layer_text = layer["layer"]
            if len(layer_text) > 30:
                layer_text = '\n'.join([layer_text[:30], layer_text[30:]])
            color = 'lightblue' if 'block' in layer['parent'].lower() else 'lightgrey'
            bottom_y = draw_block(ax, 0.5, current_y, layer_width, layer_height, layer_text, color=color)

            if i < len(architecture_subset) - 1:
                next_layer_top_y = bottom_y - vertical_spacing + layer_height / 2
                ax.plot([0.5, 0.5], [bottom_y, next_layer_top_y], 'k-')
                current_y = next_layer_top_y - layer_height / 2

        ax.set_xlim(0, 1)
        ax.set_ylim(bottom_y - 0.1, 0.1)
        ax.axis('off')

    fig, axs = plt.subplots(num_subplots, 1, figsize=(6, 8 * num_subplots))

    if num_subplots == 1:
        axs = [axs]  

    for i, ax in enumerate(axs):
        start_idx = i * max_layers_per_subplot
        end_idx = start_idx + max_layers_per_subplot
        architecture_subset = architecture[start_idx:end_idx]
        draw_architecture(ax, architecture_subset)

    plt.show()
