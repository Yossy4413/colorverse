import os
import subprocess

def ensure_dirs():
    os.makedirs("assets/social", exist_ok=True)

def generate_rasters():
    # We will use ImageMagick or Inkscape if installed, but since we can't guarantee,
    # we'll build a simple PIL script that draws a raster approximation of the icon
    # if a direct SVG renderer isn't easily scriptable without heavy dependencies like cairosvg.
    # Actually, let's just draw the "C" neon logo directly using pure Pillow for 100% reliability
    
    from PIL import Image, ImageDraw, ImageFilter
    
    def create_neon_icon(size):
        # Create base image
        img = Image.new('RGBA', (size, size), (11, 12, 16, 255)) # #0b0c10
        
        # Transparent layer for glow
        glow_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw_glow = ImageDraw.Draw(glow_layer)
        
        # Transparent layer for text/core
        core_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw_core = ImageDraw.Draw(core_layer)
        
        # Math for the C arc
        center = size / 2
        radius = size * 0.35
        thickness = size * 0.08
        
        box = [center - radius, center - radius, center + radius, center + radius]
        
        # Draw Glow
        # We draw multiple times for blur
        draw_glow.arc(box, start=45, end=315, fill=(69, 243, 255, 255), width=int(thickness))
        
        # Draw accent lines
        # line 1
        l1_start = (center - radius*0.3, center - radius*0.3)
        l1_end = (center + radius*0.3, center + radius*0.3)
        draw_glow.line([l1_start, l1_end], fill=(69, 243, 255, 255), width=int(thickness*0.6))
        
        # line 2
        l2_start = (center - radius*0.5, center - radius*0.1)
        l2_end = (center + radius*0.1, center + radius*0.5)
        draw_glow.line([l2_start, l2_end], fill=(69, 243, 255, 255), width=int(thickness*0.6))
        
        # Apply blur to glow layer
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=size*0.04))
        
        # Draw Core (White)
        draw_core.arc(box, start=45, end=315, fill=(255, 255, 255, 255), width=int(thickness*0.5))
        draw_core.line([l1_start, l1_end], fill=(255, 255, 255, 255), width=int(thickness*0.3))
        draw_core.line([l2_start, l2_end], fill=(255, 255, 255, 255), width=int(thickness*0.3))
        
        # Composite
        final = Image.alpha_composite(img, glow_layer)
        final = Image.alpha_composite(final, core_layer)
        
        return final

    # Generate the Master 1024
    master = create_neon_icon(1024)
    master.save("assets/social/master_1024.png")
    
    # Generate Social Profiles
    master.resize((800, 800), Image.Resampling.LANCZOS).save("assets/social/instagram_800.png")
    master.resize((500, 500), Image.Resampling.LANCZOS).save("assets/social/pixiv_500.png")
    master.resize((400, 400), Image.Resampling.LANCZOS).save("assets/social/twitter_400.png")
    
    # Generate Favicons (need RGBA without dark background for some, but user asked for simple, let's keep the dark bg for contrast)
    master.resize((64, 64), Image.Resampling.LANCZOS).save("assets/favicon-64x64.png")
    master.resize((32, 32), Image.Resampling.LANCZOS).save("assets/favicon-32x32.png")
    
    # ICO format supports multiple sizes
    icon_sizes = [(16,16), (32,32), (48,48), (64,64)]
    master.save("assets/favicon.ico", format="ICO", sizes=icon_sizes)
    print("Brand assets (Favicons, Social Images) generated successfully.")

if __name__ == "__main__":
    ensure_dirs()
    generate_rasters()
