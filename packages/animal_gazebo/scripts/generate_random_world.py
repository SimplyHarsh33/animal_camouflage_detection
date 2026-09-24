#!/usr/bin/env python3
"""
Procedural Wildlife World Generator for Gazebo Simulation.
Generates randomized, realistic forest environments with domain randomization:
  - Organic Poisson-disc vegetation distribution (Oak & Pine trees).
  - Rock boulder clusters for natural cover.
  - Perimeter tree barrier enclosing the arena.
  - Strategic concealment placement for 1–3 Deer (Light, Medium, Heavy camouflage).
  - Sun lighting domain randomization (azimuth, elevation, shadow angles).
  - Full seed reproducibility for academic benchmarking (--seed N).
"""

import os
import sys
import math
import random
import argparse
import json

def parse_args():
    parser = argparse.ArgumentParser(description="Procedural World Generator for Wildlife Camouflage")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for repeatable world generation")
    parser.add_argument("--num-deer", type=int, default=3, choices=[1, 2, 3, 4], help="Number of deer to spawn (1-4)")
    parser.add_argument("--density", type=str, default="medium", choices=["low", "medium", "high"], help="Vegetation density")
    parser.add_argument("--arena-size", type=float, default=22.0, help="Arena width and height in meters")
    parser.add_argument("--output", type=str, default=None, help="Output SDF world file path")
    parser.add_argument("--no-perimeter", action="store_true", help="Disable boundary perimeter trees")
    return parser.parse_args()

class ProceduralWorldGenerator:
    def __init__(self, seed=None, num_deer=3, density="medium", arena_size=22.0, perimeter=True):
        self.seed = seed if seed is not None else random.randint(1000, 999999)
        self.rng = random.Random(self.seed)
        self.num_deer = num_deer
        self.density = density
        self.arena_size = arena_size
        self.half_size = arena_size / 2.0
        self.perimeter = perimeter

        # Safety radius around robot spawn (0, 0)
        self.spawn_clearance_radius = 2.0

        # Density configs (trees, rocks)
        density_map = {
            "low": {"trees": 12, "rocks": 8},
            "medium": {"trees": 20, "rocks": 14},
            "high": {"trees": 30, "rocks": 22},
        }
        self.tree_count = density_map[density]["trees"]
        self.rock_count = density_map[density]["rocks"]

        # Track placed models to prevent overlap: list of (x, y, radius, model_type)
        self.placed_objects = []
        self.deer_metadata = []

    def distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def is_valid_position(self, x, y, radius):
        # 1. Check inside arena boundaries
        if abs(x) > (self.half_size - 1.0) or abs(y) > (self.half_size - 1.0):
            return False

        # 2. Check robot spawn clearance
        if self.distance((x, y), (0.0, 0.0)) < (self.spawn_clearance_radius + radius):
            return False

        # 3. Check overlap with existing placed objects
        for ox, oy, oradius, _ in self.placed_objects:
            if self.distance((x, y), (ox, oy)) < (radius + oradius):
                return False

        return True

    def place_object(self, name, model_uri, x, y, yaw, radius=0.8):
        self.placed_objects.append((x, y, radius, name))
        return {
            "name": name,
            "uri": model_uri,
            "x": round(x, 3),
            "y": round(y, 3),
            "z": 0.0,
            "yaw": round(yaw, 4)
        }

    def generate_sun_lighting(self):
        """Randomizes sun position, shadow angle, and golden-hour / midday warmth."""
        sun_azimuth = self.rng.uniform(0, 2 * math.pi)
        sun_elevation = self.rng.uniform(0.6, 1.2)  # 35° to 70° elevation

        dx = round(-math.cos(sun_azimuth) * math.cos(sun_elevation), 3)
        dy = round(-math.sin(sun_azimuth) * math.cos(sun_elevation), 3)
        dz = round(-math.sin(sun_elevation), 3)

        # Subtle lighting warmth variation
        r = round(self.rng.uniform(0.85, 0.95), 2)
        g = round(self.rng.uniform(0.82, 0.90), 2)
        b = round(self.rng.uniform(0.75, 0.85), 2)

        return {
            "dir_x": dx,
            "dir_y": dy,
            "dir_z": dz,
            "diffuse": f"{r} {g} {b} 1.0",
            "specular": "0.15 0.15 0.15 1.0"
        }

    def build_world(self):
        models = []

        # 1. Build Perimeter Trees to visually enclose the sanctuary
        if self.perimeter:
            step = 3.2
            wall_dist = self.half_size
            perimeter_idx = 0
            # North and South walls
            for px in [x * step - self.half_size for x in range(int(self.arena_size / step) + 1)]:
                if abs(px) <= wall_dist:
                    tree_type = "model://pine_tree" if (perimeter_idx % 2 == 0) else "model://oak_tree"
                    models.append(self.place_object(f"perimeter_n_{perimeter_idx}", tree_type, px, wall_dist, self.rng.uniform(-math.pi, math.pi), radius=0.6))
                    models.append(self.place_object(f"perimeter_s_{perimeter_idx}", tree_type, px, -wall_dist, self.rng.uniform(-math.pi, math.pi), radius=0.6))
                    perimeter_idx += 1
            # East and West walls
            for py in [y * step - self.half_size for y in range(1, int(self.arena_size / step))]:
                if abs(py) <= wall_dist:
                    tree_type = "model://oak_tree" if (perimeter_idx % 2 == 0) else "model://pine_tree"
                    models.append(self.place_object(f"perimeter_e_{perimeter_idx}", tree_type, wall_dist, py, self.rng.uniform(-math.pi, math.pi), radius=0.6))
                    models.append(self.place_object(f"perimeter_w_{perimeter_idx}", tree_type, -wall_dist, py, self.rng.uniform(-math.pi, math.pi), radius=0.6))
                    perimeter_idx += 1

        # 2. Procedural Concealment Scenarios for Deer
        # We spawn deer at varying distances: Close (3–4m), Medium (5–7m), Far (7.5–9.5m)
        ranges = [
            ("Close", 2.8, 4.2, "Light Concealment"),
            ("Medium", 4.8, 6.8, "Moderate Concealment"),
            ("Far", 7.2, 9.5, "Heavy Camouflage"),
            ("Flank", 5.0, 8.0, "Deep Shrub Cover")
        ]

        for i in range(self.num_deer):
            label, r_min, r_max, concealment_desc = ranges[i % len(ranges)]
            placed = False
            for attempt in range(100):
                # Sample polar coordinates from spawn
                angle = self.rng.uniform(-math.pi * 0.75, math.pi * 0.75)  # Forward-facing arc
                dist = self.rng.uniform(r_min, r_max)
                dx = dist * math.cos(angle)
                dy = dist * math.sin(angle)

                if self.is_valid_position(dx, dy, radius=1.0):
                    # Place the deer
                    deer_yaw = self.rng.uniform(-math.pi, math.pi)
                    deer_model = self.place_object(f"deer_{label.lower()}_{i+1}", "model://deer", dx, dy, deer_yaw, radius=0.9)
                    models.append(deer_model)

                    # Add strategic camouflage cover near the deer (rock or tree)
                    cover_type = self.rng.choice(["rock", "oak_tree", "pine_tree"])
                    cover_dist = self.rng.uniform(0.6, 1.2)
                    cover_angle = angle + self.rng.uniform(-0.5, 0.5)
                    cx = dx + cover_dist * math.cos(cover_angle)
                    cy = dy + cover_dist * math.sin(cover_angle)

                    if self.is_valid_position(cx, cy, radius=0.8):
                        cover_uri = f"model://{cover_type}"
                        cover_model = self.place_object(f"cover_{label.lower()}_{i+1}", cover_uri, cx, cy, self.rng.uniform(-math.pi, math.pi), radius=0.8)
                        models.append(cover_model)

                    self.deer_metadata.append({
                        "name": deer_model["name"],
                        "tier": label,
                        "distance_m": round(dist, 2),
                        "position": [round(dx, 2), round(dy, 2)],
                        "concealment": concealment_desc
                    })
                    placed = True
                    break

        # 3. Scatter Interior Vegetation (Oak & Pine Trees in organic clusters)
        for i in range(self.tree_count):
            tree_type = self.rng.choice(["model://oak_tree", "model://pine_tree"])
            for _ in range(50):
                x = self.rng.uniform(-self.half_size + 2.0, self.half_size - 2.0)
                y = self.rng.uniform(-self.half_size + 2.0, self.half_size - 2.0)
                if self.is_valid_position(x, y, radius=1.0):
                    models.append(self.place_object(f"tree_{i+1}", tree_type, x, y, self.rng.uniform(-math.pi, math.pi), radius=0.9))
                    break

        # 4. Scatter Interior Rocks & Boulders
        for i in range(self.rock_count):
            for _ in range(50):
                x = self.rng.uniform(-self.half_size + 2.0, self.half_size - 2.0)
                y = self.rng.uniform(-self.half_size + 2.0, self.half_size - 2.0)
                if self.is_valid_position(x, y, radius=0.8):
                    models.append(self.place_object(f"rock_{i+1}", "model://rock", x, y, self.rng.uniform(-math.pi, math.pi), radius=0.7))
                    break

        # Generate sun lighting
        sun = self.generate_sun_lighting()

        return models, sun

    def generate_sdf(self):
        models, sun = self.build_world()

        sdf_lines = [
            '<?xml version="1.0" ?>',
            '<sdf version="1.6">',
            f'  <world name="procedural_forest_seed_{self.seed}">',
            '',
            '    <!-- ===== SUN LIGHTING (Domain Randomized) ===== -->',
            '    <light type="directional" name="procedural_sun">',
            '      <cast_shadows>true</cast_shadows>',
            '      <pose>0 0 15 0 0 0</pose>',
            f'      <diffuse>{sun["diffuse"]}</diffuse>',
            f'      <specular>{sun["specular"]}</specular>',
            '      <attenuation>',
            '        <range>1000</range>',
            '        <constant>0.9</constant>',
            '        <linear>0.01</linear>',
            '        <quadratic>0.001</quadratic>',
            '      </attenuation>',
            f'      <direction>{sun["dir_x"]} {sun["dir_y"]} {sun["dir_z"]}</direction>',
            '    </light>',
            '',
            '    <!-- ===== GROUND PLANE ===== -->',
            '    <include>',
            '      <uri>model://ground_plane</uri>',
            '    </include>',
            '',
            '    <!-- ===== PROCEDURALLY PLACED NATURE & TARGETS ===== -->'
        ]

        for m in models:
            sdf_lines.extend([
                '    <include>',
                f'      <name>{m["name"]}</name>',
                f'      <uri>{m["uri"]}</uri>',
                '      <static>true</static>',
                f'      <pose>{m["x"]} {m["y"]} {m["z"]} 0 0 {m["yaw"]}</pose>',
                '    </include>'
            ])

        sdf_lines.extend([
            '',
            '  </world>',
            '</sdf>',
            ''
        ])

        return "\n".join(sdf_lines)


def main():
    args = parse_args()

    default_output = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "worlds",
        "animal_world.world"
    )
    output_path = args.output if args.output else default_output

    print("============================================================")
    print("🌲 PROCEDURAL WILDLIFE WORLD GENERATOR (Domain Randomization)")
    print("============================================================")

    generator = ProceduralWorldGenerator(
        seed=args.seed,
        num_deer=args.num_deer,
        density=args.density,
        arena_size=args.arena_size,
        perimeter=not args.no_perimeter
    )

    sdf_content = generator.generate_sdf()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(sdf_content)

    print(f"\n[SUCCESS] World generated successfully with Seed: {generator.seed}")
    print(f"Target file: {output_path}")
    print(f"Vegetation Density: {args.density.upper()}")
    print(f"Total Objects Placed: {len(generator.placed_objects)}")
    print(f"\n🦌 Camouflaged Deer Deployment Summary:")
    print("------------------------------------------------------------")
    for d in generator.deer_metadata:
        print(f"  • {d['name']:<18} | Tier: {d['tier']:<8} | Dist: {d['distance_m']:>4}m | Pos: ({d['position'][0]:>5}, {d['position'][1]:>5}) | {d['concealment']}")
    print("============================================================\n")

if __name__ == "__main__":
    main()
