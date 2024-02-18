from PIL import Image, ImageDraw

# Create a list to store frames
frames = []

# Create frames
for i in range(10):
    print("Creating frame", i)
    # Create a new image
    image = Image.new("RGB", (200, 200), "white")
    
    # Draw something on the image (e.g., a rectangle)
    draw = ImageDraw.Draw(image)
    draw.rectangle([i * 20, 50, i * 20 + 30, 150], fill="blue")

    # Append the frame to the list
    frames.append(image)

# Save the frames as an animated GIF
frames[0].save("animated.gif", save_all=True, append_images=frames[1:], duration=100, loop=0)

