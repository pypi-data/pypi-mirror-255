import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

class VMMC_model:
    def __init__(self, base_types_strands, interaction_strengths, base_colors, container_height=10, container_depth=10):
        self.base_types_strands = base_types_strands
        self.interaction_strengths = interaction_strengths
        self.base_colors = base_colors  # Include base_colors as an attribute
        self.container_height = container_height
        self.container_depth = container_depth
        self.base_colors = base_colors

    def _concatenate_bases(self):
        return np.concatenate(self.base_types_strands)

    def _initialize_positions(self):
        N = sum(len(strand) for strand in self.base_types_strands)
        num_strands = len(self.base_types_strands)
        positions = np.zeros((N, 3))
        current_index = 0
        y_spacing = self.container_height / (num_strands + 1)  # Evenly distribute along y-axis
        z_spacing = self.container_depth / (N + 1)  # Evenly distribute along z-axis
        for i, strand in enumerate(self.base_types_strands):
            strand_length = len(strand)
            x_spacing = self.container_depth / (strand_length + 1)  # Spread out along x-axis
            for j in range(strand_length):
                positions[current_index + j] = ((j + 1) * x_spacing, (i + 1) * y_spacing, (current_index + j + 1) * z_spacing)
            current_index += strand_length
        return positions

    def _apply_periodic_boundaries(self, pos):
        pos[:, 1] = pos[:, 1] % self.container_height
        pos[:, 1] = np.where(pos[:, 1] < 0, self.container_height + pos[:, 1], pos[:, 1])
        pos[:, 2] = pos[:, 2] % self.container_depth
        pos[:, 2] = np.where(pos[:, 2] < 0, self.container_depth + pos[:, 2], pos[:, 2])
        return pos

    def _base_specific_interaction_energy(self, r, base_i, base_j, epsilon=1.0, sigma=1.0):
        base_pair = (base_i, base_j)
        interaction_strength = self.interaction_strengths.get(base_pair, 0)
        epsilon_scaled = epsilon * interaction_strength
        V_rep = 0
        V_attr = 0
        if r < sigma:
            V_rep = 1e6
        elif sigma < r < 2.5 * sigma:
            V_attr = -epsilon_scaled
        return V_rep + V_attr

    def _total_potential_energy_with_bases(self, positions, bases, epsilon=1.0, sigma=1.0):
        energy = 0.0
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                r = np.linalg.norm(positions[i] - positions[j])
                energy += self._base_specific_interaction_energy(r, bases[i], bases[j], epsilon, sigma)
        return energy

    def identify_cluster(self, seed_index, positions, threshold=1.5):
        cluster = [seed_index]
        for i, pos in enumerate(positions):
            if i != seed_index and np.linalg.norm(positions[seed_index] - pos) < threshold:
                cluster.append(i)
        return cluster

    def propose_move(self, cluster_indices, positions, max_step=0.5):
        direction = np.random.rand(3) - 0.5
        direction /= np.linalg.norm(direction)
        step_size = np.random.rand() * max_step
        new_positions = positions.copy()
        for index in cluster_indices:
            new_positions[index] += direction * step_size
        return new_positions

    def update(self, frame):
        seed_index = np.random.randint(len(self.positions))
        cluster = self.identify_cluster(seed_index, self.positions)
        
        # Calculate initial energy with base types
        initial_energy = self._total_potential_energy_with_bases(self.positions, self.base_types)
        
        # Propose move
        new_positions = self.propose_move(cluster, self.positions)
        
        # Apply periodic boundary conditions only in the y-direction
        new_positions[:, 1] %= self.container_height
        
        # Calculate final energy with base types
        final_energy = self._total_potential_energy_with_bases(new_positions, self.base_types)
        
        # Metropolis criterion
        delta_energy = final_energy - initial_energy
        if delta_energy <= 0 or np.exp(-delta_energy) > np.random.rand():
            self.positions = new_positions
        
        # Update the scatter plot
        self.scatter._offsets3d = (self.positions[:, 0], self.positions[:, 1], self.positions[:, 2])
        self.scatter.set_color(self.base_colors)  # Set colors
        
        # Update lines connecting bases
        self.current_index = 0
        for line, strand_length in zip(self.lines, self.strand_lengths):
            strand_pos = self.positions[self.current_index:self.current_index + strand_length]
            line.set_data(strand_pos[:, 0], strand_pos[:, 1])
            line.set_3d_properties(strand_pos[:, 2])
            self.current_index += strand_length
        
        # Update angle
        self.angle = (self.angle + 2) % 360
        self.ax.view_init(elev=20, azim=self.angle)


    def animate(self, frames=100, interval=50):
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_zlim(0, 10)
        self.scatter = self.ax.scatter(self.positions[:, 0], self.positions[:, 1], self.positions[:, 2], c=self.base_colors)
        self.num_tracked = 5
        self.paths = [np.zeros((0, 3)) for _ in range(self.num_tracked)]
        self.lines = [self.ax.plot([], [], [], 'k')[0] for _ in range(len(self.base_types_strands))]
        self.angle = 0
        self.ani = FuncAnimation(self.fig, self.update, frames=frames, interval=interval)
        plt.show()

    def save_animation(self, filename, writer='ffmpeg', fps=10):
        self.ani.save(filename, writer=writer, fps=fps)

base_types_strand1 = np.array(['A', 'T', 'C', 'G', 'G', 'G', 'C', 'G'])
base_types_strand2 = np.array(['T', 'A', 'G', 'C', 'G', 'C', 'C', 'G'])
base_types_strand3 = np.array(['A', 'T', 'T', 'T', 'A', 'A', 'T', 'A'])
base_types_strand4 = np.array(['T', 'A', 'A', 'T', 'T', 'T', 'A', 'T'])
base_types_strand5 = np.array(['G', 'C', 'A', 'T', 'C', 'G', 'A', 'T'])
base_types_strand6 = np.array(['T', 'G', 'C', 'A', 'T', 'G', 'C', 'A'])


base_types_strands = [base_types_strand1, base_types_strand2, base_types_strand3, base_types_strand4, base_types_strand5, base_types_strand6]

interaction_strengths = {
    ('A', 'T'): 1.0,
    ('T', 'A'): 1.0,
    ('G', 'C'): 1.5,
    ('C', 'G'): 1.5,
}

# Define colors for each base
base_colors_dict = {'A': 'r', 'T': 'b', 'C': 'y', 'G': 'g'}
base_colors = np.array([base_colors_dict[base] for strand in base_types_strands for base in strand])

# Instantiate VMMC_model with base_colors included
vmmc_model = VMMC_model(base_types_strands, interaction_strengths, base_colors)
vmmc_model.base_types = vmmc_model._concatenate_bases()
vmmc_model.positions = vmmc_model._initialize_positions()
vmmc_model.strand_lengths = [len(strand) for strand in vmmc_model.base_types_strands]
vmmc_model.current_index = 0

# Run animation and save
vmmc_model.animate(frames=100, interval=50)
vmmc_model.save_animation('particle_movement_with_3d_interactions_rotating.mp4')