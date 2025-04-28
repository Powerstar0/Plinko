import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle

# Parameters
num_levels = 10   # Number of peg levels
num_balls = 2   # Total balls to drop
ball_paths = []   # Store all ball paths for display
positions = []    # Final positions for histogram

# Peg positions
peg_x = []
peg_y = []
start_pegs = 3  # Start with 3 pegs at the top

for level in range(num_levels):
    num_pegs = start_pegs + level
    start_x = -(num_pegs - 1) / 2
    for i in range(num_pegs):
        peg_x.append(start_x + i)
        peg_y.append(-level)

# Calculate the possible final positions
min_pos = -(num_levels + start_pegs - 1) // 2
max_pos = (num_levels + start_pegs - 1) // 2
bins = np.arange(min_pos - 0.5, max_pos + 1.5, 1)  # bin edges
bin_positions = list(range(min_pos, max_pos + 1))  # Center positions for bins

# Function to simulate a single ball path
def drop_ball_path():
    path = []
    x = 0.0  # Start at center top
    path.append((x, 0.5))  # Starting position slightly above top pegs
    
    for level in range(num_levels):
        # Determine the number of pegs at this level
        num_pegs = start_pegs + level
        start_x = -(num_pegs - 1) / 2
        
        # The ball can go left or right at each level
        move = np.random.choice([-0.5, 0.5])
        x += move
        
        # Add point at peg level but between pegs
        path.append((x, -level))
    
    # Add final path point to the bin
    path.append((x, -num_levels - 0.5))
    
    # The final bin position is determined by rounding the final x-position
    final_position = int(round(x))
    return path, final_position

# Animation update function
def update(frame):
    path, position = drop_ball_path()
    ball_paths.append((path, position))
    positions.append(position)
    
    ax1.clear()
    ax2.clear()
    
    # Draw bins with labels
    bin_width = 0.8
    bin_height = 1.0
    bin_bottom = -num_levels - 1
    
    # Count balls in each bin for coloring
    bin_counts = {pos: positions.count(pos) for pos in bin_positions}
    
    for pos in bin_positions:
        bin_x = pos - bin_width/2
        # Color intensity based on number of balls
        balls_in_bin = bin_counts.get(pos, 0)
        intensity = min(1.0, 0.3 + balls_in_bin / 20)  # Darker as more balls accumulate
        rect = Rectangle((bin_x, bin_bottom), bin_width, bin_height, 
                         edgecolor='black', facecolor=f'C0', alpha=intensity)
        ax1.add_patch(rect)
        
        # Add bin label
        ax1.text(pos, bin_bottom - 0.3, f"{pos}", 
                 ha='center', va='top', fontsize=8, color='black')
    
    # Draw pegs
    ax1.plot(peg_x, peg_y, 'ko', markersize=5)
    
    # Draw previous ball paths (faded)
    max_visible_paths = 20  # Limit how many previous paths to show
    for i, (old_path, _) in enumerate(ball_paths[-max_visible_paths:-1] if len(ball_paths) > 1 else []):
        if old_path:
            old_x, old_y = zip(*old_path)
            alpha = 0.1  # Faded previous paths
            ax1.plot(old_x, old_y, 'b-', alpha=alpha, linewidth=1)
            # Add ball at final position
            ax1.plot(old_x[-1], old_y[-1], 'bo', alpha=0.5, markersize=4)
    
    # Draw current ball path
    if path:
        path_x, path_y = zip(*path)
        ax1.plot(path_x, path_y, 'r-', linewidth=2)
        ax1.plot(path_x[-1], path_y[-1], 'ro', markersize=6)
    
    # Configure Galton board plot
    ax1.set_xlim(min_pos - 1, max_pos + 1)
    ax1.set_ylim(bin_bottom - 0.5, 1)
    ax1.set_aspect('equal')
    ax1.set_title("Galton Board")
    ax1.axis('off')
    
    # Draw histogram - updated in real-time
    counts, edges, patches = ax2.hist(positions, bins=bins, edgecolor='black', 
                                     rwidth=0.8, color='skyblue')
    
    # Draw bin position labels on histogram x-axis to match board
    ax2.set_xticks(bin_positions)
    ax2.set_xticklabels([str(pos) for pos in bin_positions])
    
    # Configure histogram plot
    ax2.set_xlim(min_pos - 1, max_pos + 1)
    max_count = max(10, max(counts) * 1.1) if len(counts) > 0 else 10  # Add 10% margin
    ax2.set_ylim(0, max_count)
    ax2.set_title(f"Distribution (Ball {len(positions)} of {num_balls})")
    ax2.set_xlabel("Final Position")
    ax2.set_ylabel("Number of Balls")
    ax2.grid(axis='y', alpha=0.3)
    
    # Calculate and display statistics
    if len(positions) > 1:
        mean = np.mean(positions)
        variance = np.var(positions)
        std_dev = np.std(positions)
        
        # Display statistics on the plot
        stats_text = f"Mean: {mean:.2f}\nVariance: {variance:.2f}\nStd Dev: {std_dev:.2f}"
        ax2.text(0.02, 0.95, stats_text, transform=ax2.transAxes, 
                 bbox=dict(facecolor='white', alpha=0.8), fontsize=10,
                 verticalalignment='top')
    
    # Add normal distribution curve overlay
    if len(positions) > 10:
        mean = np.mean(positions)
        std = np.std(positions)
        
        if std > 0:  # Avoid division by zero
            # Create points for the normal distribution curve
            x = np.linspace(min_pos - 1, max_pos + 1, 100)
            # Calculate PDF
            pdf = (1/(std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean)/std)**2)
            # Scale to match the histogram area
            total_area = len(positions)  # Total area under histogram
            y = pdf * total_area  # Scale to match total area
            
            ax2.plot(x, y, 'r-', linewidth=2, label='Normal Distribution')
            ax2.legend(loc='upper right')
    
    # End the animation if we've reached the target number of balls
    if len(positions) >= num_balls:
        ani.event_source.stop()
        
        # Print final statistics to console when animation completes
        final_mean = np.mean(positions)
        final_variance = np.var(positions)
        final_std = np.std(positions)
        print(f"\nFinal Statistics after {len(positions)} balls:")
        print(f"Mean: {final_mean:.4f}")
        print(f"Variance: {final_variance:.4f}")
        print(f"Standard Deviation: {final_std:.4f}")

# Set up plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
fig.suptitle("Galton Board Demonstration", fontsize=16)

# Start the animation - one ball at a time
ani = animation.FuncAnimation(fig, update, frames=num_balls, repeat=False, interval=100)
plt.tight_layout()
plt.show()