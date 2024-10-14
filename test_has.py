import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Step 1: Load the data
file_path = r'dataset\GLB.Ts+dSST.csv' # Ensure the correct file path
data = pd.read_csv(file_path)

# Step 2: Clean the dataset
data = data.apply(pd.to_numeric, errors='coerce')
data = data.dropna()

# Step 3: Extract the relevant data for plotting
years = data['Year'].values
months = data.columns[1:13]  # Columns for Jan to Dec
monthly_data = data[months].values
# print(monthly_data)
# Step 4: Create the polar plot
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))
ax.set_theta_direction(-1)  # Set clockwise direction
ax.set_theta_offset(np.pi / 2.0)  # Start at the top
ax.set_facecolor('black')  # Set background color

# Step 5: Normalize temperature anomalies
anomalies = monthly_data.flatten()
norm_anomalies = (anomalies - anomalies.min()) / (anomalies.max() - anomalies.min())

# Create month labels
month_labels = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

# Define the base circle radius (nothing will be drawn in this inner radius)
base_circle_radius = 250  # Updated base circle radius

# Define the gap between circles for each year
gap_between_years = 10  # Distance between each year circle

# Step 6: Function to update the animation frame
def update(frame):
    ax.clear()  # Clear the plot for each frame
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2.0)
    ax.set_facecolor('black')

    # Set limits for the spiral
    r_min = base_circle_radius  # Start plotting outside the base circle
    r_max = base_circle_radius + len(years) * gap_between_years

    # Plot the base circle
    theta_base = np.linspace(0, 2 * np.pi, 100)
    # ax.plot(theta_base, np.ones_like(theta_base) * base_circle_radius, color='gray', lw=2, alpha=0.8)

    # Plot climate data for each year forming a spiral
    for i, year in enumerate(years[:frame + 1]):
        theta = np.linspace(0, 2 * np.pi, 12)  # One full rotation for 12 months
        radius = r_min + (i * gap_between_years)  # Increased gap for each year
        
        # Get the temperature anomalies for this year
        anomalies = monthly_data[i, :]
        
        # Map the temperature anomalies to colors
        colors = plt.cm.RdYlBu_r((anomalies - anomalies.min()) / (anomalies.max() - anomalies.min()))
        
        # Plot the year data in a spiral pattern
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        # print("x = ",x,"y = ", y)
        print("Year: ", year)
        # ax.plot(x, y, color=colors.mean(axis=0), lw=2, alpha=0.8)
        ax.plot(theta, np.ones_like(theta) * radius, color=colors.mean(axis=0), lw=2, alpha=0.8)

    # Set labels and display current year
    ax.text(np.pi / 2.0, 0, f'{years[frame]}', ha='center', va='center', fontsize=24, color='yellow')

    # Add month labels
    for i, label in enumerate(month_labels):
        ax.text(i / 12.0 * 2 * np.pi, r_max + 5, label, color='yellow', fontsize=12, ha='center')

    # Reference temperature circles
    ax.set_ylim(0, r_max + 10)

# Step 7: Create the animation
ani = FuncAnimation(fig, update, frames=len(years), interval=100, repeat=False)

# Step 8: Show the plot
plt.show()
