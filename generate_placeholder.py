from PIL import Image, ImageDraw, ImageFont
import os

# Ensure static/img directory exists
os.makedirs('static/img', exist_ok=True)

# Create a simple placeholder image
img = Image.new('RGB', (200, 200), color=(255, 255, 255))
draw = ImageDraw.Draw(img)
draw.rectangle([(0, 0), (199, 199)], outline=(0, 0, 0), width=2)
draw.rectangle([(20, 20), (180, 180)], outline=(0, 0, 0), width=2)

# Add text if possible
try:
    font = ImageFont.load_default()
    draw.text((40, 90), "QR Placeholder", fill=(0, 0, 0), font=font)
except Exception as e:
    print(f"Error adding text: {e}")

# Save the file
img.save('static/img/qr-placeholder.png')
print("QR placeholder image created at static/img/qr-placeholder.png")

# Run this script once to generate the placeholder image
if __name__ == "__main__":
    print("Placeholder image generation completed.")
