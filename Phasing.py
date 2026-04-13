# Implementation of Fibonacci Ovoid Tunneling
import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

def get_polar_coordinates(led):
    """Convert LED position to polar coordinates"""
    x, y = led
    r = math.sqrt(x**2 + y**2)
    theta = math.atan2(y, x)
    return r, theta

def pulse_width_modulate(f, staircase_val, ovoid_constraint):
    """Simulate PWM for brightness"""
    # Normalize and clamp between 0 and 1
    brightness = abs(math.sin(f * 2 * math.pi + staircase_val)) * ovoid_constraint
    return max(0, min(1, brightness))

def generate_ovoid_staircase(led_matrix, time_step):
    phi = (1 + 5**0.5) / 2  # The Golden Ratio

    brightness_matrix = np.zeros(led_matrix.shape[:2])

    for i in range(led_matrix.shape[0]):
        for j in range(led_matrix.shape[1]):
            led = led_matrix[i][j]
            r, theta = get_polar_coordinates(led)

            # 1. Calculate Fibonacci Step (The Staircase)
            staircase_val = (r * phi) % 1.0

            # 2. The Wave-Break / Overlap Logic
            f = (phi**r) * math.sin(time_step + theta)

            # 3. Spinning Ovoid Geometry
            ovoid_constraint = (r**2) / (math.sin(theta) + phi) if math.sin(theta) + phi != 0 else 0

            # 4. Trigger the EM Pulse
            brightness = pulse_width_modulate(f, staircase_val, ovoid_constraint)
            brightness_matrix[i][j] = brightness

    return brightness_matrix

def create_led_matrix(size=20):
    """Create a grid of LED positions"""
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    return np.stack([X, Y], axis=-1)

def animate_tunneling(frame):
    time_step = frame * 0.1
    brightness = generate_ovoid_staircase(led_matrix, time_step)
    im.set_array(brightness)
    return [im]

if __name__ == "__main__":
    led_matrix = create_led_matrix(50)

    fig, ax = plt.subplots()
    im = ax.imshow(np.zeros((50, 50)), cmap='plasma', vmin=0, vmax=1)
    ax.set_title("Fibonacci Ovoid Tunneling Visualization")

    ani = FuncAnimation(fig, animate_tunneling, frames=100, interval=50, blit=True)
    plt.show()