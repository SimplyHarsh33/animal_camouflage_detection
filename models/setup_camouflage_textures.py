#!/usr/bin/env python3
import os
import cv2
import numpy as np

def generate_forest_floor_texture(output_path, size=1024):
    """
    Synthesizes a realistic seamless woodland forest floor texture:
    Dark rich soil, fallen dry autumn leaves (russet/tan/olive), pine needles, and moss.
    """
    np.random.seed(42)
    # 1. Base soil layer (deep earthy brown/loam)
    base = np.zeros((size, size, 3), dtype=np.float32)
    base[:, :] = [28.0, 42.0, 52.0] # BGR deep brown earth

    # Multi-octave Perlin-like soil noise
    for scale in [16, 32, 64, 128]:
        noise = np.random.normal(0, 15, (scale, scale, 3)).astype(np.float32)
        resized_noise = cv2.resize(noise, (size, size), interpolation=cv2.INTER_CUBIC)
        base += resized_noise * (32.0 / scale)

    base = np.clip(base, 15, 85)

    # 2. Add organic moss & lichen patches (olive-khaki & dark moss green)
    moss_mask = np.zeros((size, size), dtype=np.float32)
    for _ in range(8):
        cx, cy = np.random.randint(0, size, 2)
        radius = np.random.randint(80, 220)
        grid_y, grid_x = np.ogrid[:size, :size]
        dist = np.sqrt((grid_x - cx)**2 + (grid_y - cy)**2)
        patch = np.exp(-((dist / radius)**2))
        moss_mask += patch

    moss_mask = cv2.GaussianBlur(moss_mask, (101, 101), 30)
    moss_mask = np.clip(moss_mask / (moss_mask.max() + 1e-5), 0, 1)

    moss_color = np.zeros_like(base)
    moss_color[:, :] = [30.0, 65.0, 45.0] # BGR earthy moss green
    base = base * (1.0 - 0.45 * moss_mask[:, :, None]) + moss_color * (0.45 * moss_mask[:, :, None])

    # 3. Scatter fallen deciduous leaves & dry pine needles
    img = base.astype(np.uint8)

    # Fallen dry autumn leaves (russet, ochre, tawny brown, dark burgundy)
    leaf_colors = [
        (35, 65, 110),   # tawny orange/brown
        (25, 45, 80),    # dark russet
        (40, 85, 125),   # ochre yellow-brown
        (30, 50, 65),    # dark bark brown
        (45, 75, 55)     # dried olive leaf
    ]

    for _ in range(3500):
        lx, ly = np.random.randint(0, size, 2)
        lw = np.random.randint(8, 26)
        lh = int(lw * np.random.uniform(0.4, 0.7))
        rot = np.random.uniform(0, 180)
        col = leaf_colors[np.random.randint(0, len(leaf_colors))]
        col_var = [int(np.clip(c + np.random.randint(-15, 15), 0, 255)) for c in col]
        cv2.ellipse(img, (lx, ly), (lw, lh), rot, 0, 360, col_var, -1)
        # Leaf stem
        ex = int(lx + (lw + 2) * np.cos(np.radians(rot)))
        ey = int(ly + (lw + 2) * np.sin(np.radians(rot)))
        cv2.line(img, (lx, ly), (ex, ey), (15, 25, 35), 1)

    # Pine needles (fine criss-crossed clusters)
    for _ in range(4000):
        nx, ny = np.random.randint(0, size, 2)
        nlen = np.random.randint(12, 32)
        nangle = np.random.uniform(0, np.pi * 2)
        nx2 = int(nx + nlen * np.cos(nangle))
        ny2 = int(ny + nlen * np.sin(nangle))
        needle_col = (20 + np.random.randint(0, 15), 35 + np.random.randint(0, 20), 55 + np.random.randint(0, 25))
        cv2.line(img, (nx, ny), (nx2, ny2), needle_col, 1)

    # Subtle contrast curve
    img = cv2.GaussianBlur(img, (3, 3), 0.5)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"[SUCCESS] Forest floor terrain texture saved: {output_path} ({img.shape})")
    return img

def generate_camouflaged_deer_texture(basecolor_path, texture_path, output_path):
    """
    Applies realistic woodland camouflage patterns to the deer texture map:
    Dappled sunlight spots, disruptive cryptic contour breakups, bark-matching tones.
    Preserves the exact UV unwrapping of the 3D deer mesh.
    """
    if os.path.exists(basecolor_path):
        base_img = cv2.imread(basecolor_path)
    else:
        base_img = np.full((2048, 2048, 3), (45, 60, 75), dtype=np.uint8)

    h, w = base_img.shape[:2]

    # Convert to float for clean multi-scale blending
    b_float = base_img.astype(np.float32)

    # 1. Neutralize artificial red saturation and shift to woodland bark & dried brush palette
    # Standard deer basecolor has mean BGR [48, 60, 72].
    # We blend with oak bark & forest loam palette:
    gray = cv2.cvtColor(base_img, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # Cryptic woodland color ramp
    camou_base = np.zeros_like(b_float)
    camou_base[:, :, 0] = gray * 0.42 + 18.0  # Blue channel (deep shadows)
    camou_base[:, :, 1] = gray * 0.55 + 24.0  # Green channel (moss / lichen undertone)
    camou_base[:, :, 2] = gray * 0.65 + 32.0  # Red channel (warm earthy bark)

    # 2. Multi-scale disruptive contour breakup (Perlin-like macro patterns)
    macro_noise = cv2.resize(np.random.normal(0, 1, (32, 32)), (w, h), interpolation=cv2.INTER_CUBIC)
    macro_noise = (macro_noise - macro_noise.min()) / (macro_noise.max() - macro_noise.min() + 1e-5)
    macro_factor = cv2.GaussianBlur(macro_noise, (65, 65), 20)

    # Shadow banding / tree branch shadow dapples
    shadow_stripes = np.sin(np.linspace(0, 16 * np.pi, h))[:, None] * np.cos(np.linspace(0, 12 * np.pi, w))[None, :]
    shadow_stripes = cv2.GaussianBlur(shadow_stripes, (121, 121), 40)
    shadow_factor = 0.82 + 0.36 * (shadow_stripes - shadow_stripes.min()) / (shadow_stripes.max() - shadow_stripes.min() + 1e-5)

    camou_blend = camou_base * shadow_factor[:, :, None]

    # 3. Dappled Fawn & Woodland Flecks (natural sunlight dapples through tree canopy)
    dapples = np.zeros((h, w), dtype=np.float32)
    np.random.seed(101)
    for _ in range(600):
        dx = np.random.randint(int(w * 0.15), int(w * 0.85))
        dy = np.random.randint(int(h * 0.10), int(h * 0.90))
        rx = np.random.randint(6, 22)
        ry = int(rx * np.random.uniform(0.6, 1.3))
        angle = np.random.uniform(-30, 30)
        cv2.ellipse(dapples, (dx, dy), (rx, ry), angle, 0, 360, 1.0, -1)

    dapples = cv2.GaussianBlur(dapples, (25, 25), 6)
    dapples = np.clip(dapples, 0.0, 1.0)[:, :, None]

    # Dapple color: soft cream / sunlit dried lichen
    dapple_color = np.array([45.0, 68.0, 85.0], dtype=np.float32) # BGR
    camou_final = camou_blend * (1.0 - 0.40 * dapples) + dapple_color * (0.40 * dapples)

    # 4. Blend 50% with original anatomical features (eyes, nose, hooves retain shading)
    result = 0.45 * b_float + 0.55 * camou_final
    result = np.clip(result, 0, 255).astype(np.uint8)

    # Save to both target locations
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, result, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"[SUCCESS] Camouflaged deer texture saved: {output_path} ({result.shape})")

    # Also update deer_texture.png (512x512 downscaled version for dashboard simulation)
    tex_small = cv2.resize(result, (512, 512), interpolation=cv2.INTER_AREA)
    cv2.imwrite(texture_path, tex_small)
    print(f"[SUCCESS] Camouflaged deer simulation sprite saved: {texture_path} ({tex_small.shape})")

if __name__ == "__main__":
    workspace = r"C:\Users\HP\Desktop\animal_camouflage_detection"
    
    # 1. Forest Floor Terrain Texture
    floor_tex_path = os.path.join(workspace, "models", "ground_plane", "materials", "textures", "forest_floor.jpg")
    generate_forest_floor_texture(floor_tex_path, size=1024)

    # 2. Camouflage Deer Textures
    base_deer_path = os.path.join(workspace, "models", "deer", "materials", "textures", "deer_basecolor.jpg")
    sim_deer_path = os.path.join(workspace, "models", "deer", "materials", "textures", "deer_texture.png")
    generate_camouflaged_deer_texture(base_deer_path, sim_deer_path, base_deer_path)
