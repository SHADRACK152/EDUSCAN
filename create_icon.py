"""
Create a simple EDUSCAN icon using PIL (Python Imaging Library)
Run this to generate icon.ico for the application
"""

from PIL import Image, ImageDraw
import os

def create_eduscan_icon():
    """Create EDUSCAN application icon"""
    
    # Create image with blue background (professional)
    size = (256, 256)
    background_color = (9, 105, 218)  # GitHub blue
    img = Image.new('RGB', size, background_color)
    draw = ImageDraw.Draw(img)
    
    # Draw outer circle for face detection theme
    circle_color = (255, 255, 255)  # White
    margin = 30
    draw.ellipse(
        [margin, margin, size[0]-margin, size[1]-margin],
        outline=circle_color,
        width=4
    )
    
    # Draw face detection grid lines (simplified)
    grid_color = (230, 237, 243)  # Light blue
    mid_x, mid_y = size[0] // 2, size[1] // 2
    
    # Vertical lines
    draw.line([(mid_x - 30, 60), (mid_x - 30, 196)], fill=grid_color, width=2)
    draw.line([(mid_x + 30, 60), (mid_x + 30, 196)], fill=grid_color, width=2)
    
    # Horizontal lines
    draw.line([(60, mid_y - 30), (196, mid_y - 30)], fill=grid_color, width=2)
    draw.line([(60, mid_y + 30), (196, mid_y + 30)], fill=grid_color, width=2)
    
    # Draw check mark at bottom (attendance success)
    check_color = (26, 127, 55)  # GitHub green
    # Simplified check mark
    draw.line([(80, 140), (95, 155)], fill=check_color, width=5)
    draw.line([(95, 155), (140, 110)], fill=check_color, width=5)
    
    # Save as ICO
    assets_dir = 'assets'
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    icon_path = os.path.join(assets_dir, 'icon.ico')
    img.save(icon_path, 'ICO', sizes=[256])
    
    print(f"✅ Icon created: {icon_path}")
    return icon_path

def create_simple_icon():
    """Create a simpler icon with just geometric shapes"""
    
    size = (256, 256)
    # Modern dark blue background
    img = Image.new('RGB', size, (13, 17, 23))
    draw = ImageDraw.Draw(img)
    
    # Draw professional blue circle
    circle_margin = 30
    draw.ellipse(
        [circle_margin, circle_margin, 
         size[0]-circle_margin, size[1]-circle_margin],
        outline=(255, 255, 255),
        width=4
    )
    
    # Draw inner design
    inner_margin = 50
    draw.ellipse(
        [inner_margin, inner_margin,
         size[0]-inner_margin, size[1]-inner_margin],
        outline=(89, 166, 255),
        width=3
    )
    
    # Draw checkmark symbol
    draw.line([(80, 140), (100, 160)], fill=(26, 127, 55), width=6)
    draw.line([(100, 160), (160, 100)], fill=(26, 127, 55), width=6)
    
    assets_dir = 'assets'
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    icon_path = os.path.join(assets_dir, 'icon.ico')
    img.save(icon_path, 'ICO')
    
    print(f"✅ Simple icon created: {icon_path}")
    return icon_path

if __name__ == "__main__":
    try:
        # Try to create detailed icon
        create_eduscan_icon()
    except Exception as e:
        print(f"⚠️  Could not create detailed icon: {e}")
        print("Creating simple icon instead...")
        try:
            create_simple_icon()
        except Exception as e2:
            print(f"❌ Icon creation failed: {e2}")
            print("Please create assets/icon.ico manually")
