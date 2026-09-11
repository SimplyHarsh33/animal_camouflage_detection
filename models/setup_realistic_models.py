#!/usr/bin/env python3
"""
Setup Realistic 3D Animal and Environment Nature Models for Gazebo
Downloads high-fidelity 3D meshes (Deer, Fox, Cat, Rabbit, Oak Tree, Pine Tree, Rocks)
and configures Gazebo SDF models with full texture mapping.
"""

import os
import sys
import shutil
import urllib.request
import zipfile

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

def download_file(url, target_path):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    print(f"Downloading {os.path.basename(target_path)} from {url}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response, open(target_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    print(f"Saved to {target_path} ({os.path.getsize(target_path)} bytes)")

def create_obj_model(name, obj_url, tex_url, scale="1.0 1.0 1.0", z_offset="0 0 0 0 0 0"):
    model_dir = os.path.join(MODELS_DIR, name)
    meshes_dir = os.path.join(model_dir, "meshes")
    tex_dir = os.path.join(model_dir, "materials", "textures")
    os.makedirs(meshes_dir, exist_ok=True)
    os.makedirs(tex_dir, exist_ok=True)

    obj_file = os.path.join(meshes_dir, f"{name}.obj")
    mtl_file = os.path.join(meshes_dir, f"{name}.mtl")
    tex_file = os.path.join(tex_dir, f"{name}_basecolor.jpg")

    download_file(obj_url, obj_file)
    download_file(tex_url, tex_file)

    # Write MTL
    with open(mtl_file, "w") as f:
        f.write(f"""newmtl {name}_material
Ka 1.0 1.0 1.0
Kd 1.0 1.0 1.0
Ks 0.1 0.1 0.1
Ns 10.0
map_Kd ../materials/textures/{name}_basecolor.jpg
""")

    # Ensure OBJ links to MTL
    with open(obj_file, "r", encoding="utf-8", errors="ignore") as f:
        obj_content = f.read()
    
    header = f"mtllib {name}.mtl\nusemtl {name}_material\n"
    if "mtllib" not in obj_content:
        with open(obj_file, "w", encoding="utf-8") as f:
            f.write(header + obj_content)

    # Write model.config
    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write(f"""<?xml version="1.0"?>
<model>
  <name>{name}</name>
  <version>1.0</version>
  <sdf version="1.6">model.sdf</sdf>
  <author>
    <name>Wildlife Camouflage System</name>
  </author>
  <description>Realistic 3D model of {name}</description>
</model>
""")

    # Write model.sdf
    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="{name}">
    <static>true</static>
    <link name="body">
      <pose>{z_offset}</pose>
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://{name}/meshes/{name}.obj</uri>
            <scale>{scale}</scale>
          </mesh>
        </geometry>
      </visual>
      <collision name="collision">
        <geometry>
          <mesh>
            <uri>model://{name}/meshes/{name}.obj</uri>
            <scale>{scale}</scale>
          </mesh>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
""")
    print(f"Successfully generated 3D SDF model for {name}")

def setup_rock_from_fuel():
    rock_dir = os.path.join(MODELS_DIR, "rock")
    os.makedirs(rock_dir, exist_ok=True)
    zip_path = "/tmp/rock.zip"
    download_file("https://fuel.gazebosim.org/1.0/OpenRobotics/models/Falling%20Rock%201.zip", zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(rock_dir)
    print("Extracted rock model")

def setup_osrf_model(name):
    target_dir = os.path.join(MODELS_DIR, name)
    os.makedirs(target_dir, exist_ok=True)
    base_url = f"https://raw.githubusercontent.com/osrf/gazebo_models/master/{name}"
    
    # Download config and sdf
    download_file(f"{base_url}/model.config", os.path.join(target_dir, "model.config"))
    download_file(f"{base_url}/model.sdf", os.path.join(target_dir, "model.sdf"))
    
    if name == "oak_tree":
        download_file(f"{base_url}/meshes/oak_tree.dae", os.path.join(target_dir, "meshes", "oak_tree.dae"))
        download_file(f"{base_url}/materials/textures/bark_0021.jpg", os.path.join(target_dir, "materials", "textures", "bark_0021.jpg"))
        download_file(f"{base_url}/materials/textures/branch_0006.png", os.path.join(target_dir, "materials", "textures", "branch_0006.png"))
    elif name == "pine_tree":
        download_file(f"{base_url}/meshes/pine_tree.dae", os.path.join(target_dir, "meshes", "pine_tree.dae"))
        download_file(f"{base_url}/materials/textures/bark_0021.jpg", os.path.join(target_dir, "materials", "textures", "bark_0021.jpg"))
        download_file(f"{base_url}/materials/textures/pine_tree.png", os.path.join(target_dir, "materials", "textures", "pine_tree.png"))

def main():
    print("=== Setting up Realistic 3D Animals & Environment Models ===")
    
    # 1. Realistic Deer
    create_obj_model(
        "deer",
        "https://raw.githubusercontent.com/cyberbotics/webots/master/projects/objects/animals/protos/deer/meshes/deer.obj",
        "https://raw.githubusercontent.com/cyberbotics/webots/master/projects/objects/animals/protos/deer/textures/deer_basecolor.jpg",
        scale="1.0 1.0 1.0"
    )

    # 2. Realistic Fox (Camouflage predator in vegetation)
    create_obj_model(
        "fox",
        "https://raw.githubusercontent.com/cyberbotics/webots/master/projects/objects/animals/protos/fox/meshes/fox.obj",
        "https://raw.githubusercontent.com/cyberbotics/webots/master/projects/objects/animals/protos/fox/textures/fox_basecolor.jpg",
        scale="1.2 1.2 1.2"
    )

    # 3. Realistic Rabbit (Camouflage prey target at ground level)
    create_obj_model(
        "rabbit",
        "https://raw.githubusercontent.com/cyberbotics/webots/master/projects/objects/animals/protos/rabbit/meshes/rabbit.obj",
        "https://raw.githubusercontent.com/cyberbotics/webots/master/projects/objects/animals/protos/rabbit/textures/rabbit_basecolor.jpg",
        scale="1.5 1.5 1.5"
    )

    # 4. Realistic Cat / Big Cat Predator
    create_obj_model(
        "leopard",
        "https://raw.githubusercontent.com/cyberbotics/webots/master/projects/objects/animals/protos/cat/meshes/cat.obj",
        "https://raw.githubusercontent.com/cyberbotics/webots/master/projects/objects/animals/protos/cat/textures/cat_basecolor.jpg",
        scale="2.0 2.0 2.0"
    )

    # 5. Environment Trees & Rocks
    print("\n=== Downloading Nature Props (Trees & Boulders) ===")
    try:
        setup_osrf_model("oak_tree")
    except Exception as e:
        print(f"Error setting up oak_tree: {e}")

    try:
        setup_osrf_model("pine_tree")
    except Exception as e:
        print(f"Error setting up pine_tree: {e}")

    try:
        setup_rock_from_fuel()
    except Exception as e:
        print(f"Error setting up rock: {e}")

    print("\n✅ All 3D Realistic Models successfully set up!")

if __name__ == "__main__":
    main()
