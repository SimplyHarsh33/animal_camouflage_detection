# -*- coding: utf-8 -*-
"""Part 2: Gazebo 3D World, Procedural Forests & Domain Randomization"""

def get_part2():
    return """
<!-- ==================== PART 2 ==================== -->
<div class="page-break">
  <div class="part-header-card border-purple">
    <div class="part-badge badge-purple">MODULE 2 OF 4</div>
    <h1 class="part-title">Part 2: Gazebo 3D World, Procedural Forests & Domain Randomization</h1>
    <p class="part-subtitle">
      Comprehensive technical handbook covering synthetic ecology simulation in Gazebo Classic 11, SDF 1.6 architecture, procedural woodland generation, distance-based obstacle spacing, multi-tier camouflage concealment scenarios, 3D textured mesh engineering, and solar domain randomization.
    </p>
  </div>

  <h2 class="sub-title">2.1 Subsystem Role Distribution & Core Ownership</h2>
  <table class="custom-table">
    <thead>
      <tr>
        <th style="width: 25%;">Engineering Role</th>
        <th style="width: 25%;">Primary Subsystem</th>
        <th style="width: 32%;">Specific Technical Responsibilities</th>
        <th style="width: 18%;">Core Viva Focus</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Procedural Generation Lead</strong></td>
        <td><strong>Procedural World Generator & Spatial Algorithms</strong></td>
        <td>
          &bull; Authoring <code class="inline-code">generate_random_world.py</code>.<br>
          &bull; Distance-based collision checks to prevent overlapping trees.<br>
          &bull; 2.0-meter obstacle-free safety zone around robot spawn.<br>
          &bull; Perimeter barrier wall of alternating oak and pine trees.
        </td>
        <td>Distance spacing math, spatial collision checking, procedural logic.</td>
      </tr>
      <tr>
        <td><strong>3D Assets & Shaders Lead</strong></td>
        <td><strong>3D Models, Textures & Mesh Decoupling</strong></td>
        <td>
          &bull; Integrating realistic 3D meshes (deer, leopard, fox, snake, oak, rock).<br>
          &bull; Writing OGRE <code class="inline-code">.material</code> scripts and MTL texture bindings.<br>
          &bull; Decoupling visual meshes (<code class="inline-code">&lt;visual&gt;</code>) from collision boxes (<code class="inline-code">&lt;collision&gt;</code>).<br>
          &bull; Writing <code class="inline-code">model.config</code> and <code class="inline-code">model.sdf</code> wrappers.
        </td>
        <td>Visual vs collision meshes, OBJ/DAE/MTL formats, OGRE material passes.</td>
      </tr>
      <tr>
        <td><strong>Performance & Lighting Lead</strong></td>
        <td><strong>Domain Randomization & CPU Optimization</strong></td>
        <td>
          &bull; Solar vector formula (Compass angle 0° to 360°, Elevation 35° to 70°).<br>
          &bull; Golden-hour diffuse color shifts for realistic illumination variance.<br>
          &bull; Shadow disabling optimization (<code class="inline-code">&lt;cast_shadows&gt;false&lt;/cast_shadows&gt;</code>).<br>
          &bull; Seed reproducibility (<code class="inline-code">--seed N</code>) for repeatable academic benchmarks.
        </td>
        <td>Domain randomization, Real Time Factor (RTF) optimization, lighting physics.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sub-title">2.2 Gazebo Simulation Engine & SDF 1.6 vs URDF Architecture</h2>
  <p>
    Gazebo Classic 11 relies on the <strong>Open Dynamics Engine (ODE)</strong> as its underlying physics solver. While the mobile robot is defined using URDF, the simulated world and all static environment entities (trees, rocks, animals, lighting) are defined using the <strong>Simulation Description Format (SDF 1.6)</strong>:
  </p>
  <ul>
    <li><strong>Why SDF for Worlds?</strong> URDF is strictly limited to tree-structured kinematic mechanisms with a single root link. It cannot represent multiple independent free-floating models, world physics parameters, ambient lighting, directional sun vectors, or global ground planes. SDF natively models entire multi-body environments.</li>
    <li><strong>The World File (<code class="inline-code">animal_world.world</code>):</strong> Acts as the top-level container, instantiating ODE solver parameters, friction models, sunlight properties, and nested model inclusions using the <code class="inline-code">model://</code> URI schema.</li>
  </ul>

  <h2 class="sub-title">2.3 Procedural Wildlife World Generator (<code class="inline-code">generate_random_world.py</code>)</h2>
  <p>
    A critical limitation of typical student robotics projects is evaluating algorithms in static, manually constructed worlds. If the animal is always placed at the exact same coordinates, the system can easily overfit. The project includes a dedicated procedural generation engine (<code class="inline-code">packages/animal_gazebo/scripts/generate_random_world.py</code>) that synthesizes realistic, organic forest reserves on demand:
  </p>

  <div class="code-header"><span>Spatial Collision Check Algorithm</span><span>generate_random_world.py</span></div>
  <div class="code-block">
def is_valid_position(self, x, y, radius):
    # 1. Boundary check within arena walls (22m x 22m)
    if abs(x) > (self.half_size - 1.0) or abs(y) > (self.half_size - 1.0):
        return False

    # 2. Safety radius: keep 2.0m obstacle-free circle around robot spawn (0, 0)
    if self.distance((x, y), (0.0, 0.0)) < (self.spawn_clearance_radius + radius):
        return False

    # 3. Distance check: ensure no overlap with existing placed objects
    for ox, oy, oradius, _ in self.placed_objects:
        if self.distance((x, y), (ox, oy)) < (radius + oradius):
            return False

    return True
  </div>

  <div class="formula-box">
    <div class="formula-title">Obstacle Spacing Rule (No Overlapping Objects)</div>
    <div class="formula-main">
      Distance Between Objects &ge; Radius of Object 1 + Radius of Object 2
    </div>
    <div class="formula-explanation">
      <strong>What this means in plain words:</strong> Before placing any tree, boulder, or deer into the simulated forest, the code calculates the distance to every already-placed object. If the distance is smaller than the combined size of both objects, the new object is rejected and re-placed elsewhere. It also guarantees a 2.0-meter empty circle around the robot spawn point so the robot never gets stuck inside a tree.
    </div>
  </div>

  <h2 class="sub-title">2.4 Multi-Tier Camouflage Concealment Scenarios</h2>
  <p>
    The generator places 1 to 4 deer at dynamically sampled coordinates relative to the robot's initial forward-facing optical arc. To rigorously test the computer vision engine, targets are categorized into four distinct concealment tiers:
  </p>

  <table class="custom-table">
    <thead>
      <tr>
        <th>Concealment Tier</th>
        <th>Radial Distance</th>
        <th>Concealment Environment</th>
        <th>Perception Challenge Evaluated</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Tier 1: Close</strong></td>
        <td>2.8 meters to 4.2 meters</td>
        <td>Light Concealment; clear line of sight amidst light grass.</td>
        <td>Baseline detection, rapid visual servoing acquisition.</td>
      </tr>
      <tr>
        <td><strong>Tier 2: Medium</strong></td>
        <td>4.8 meters to 6.8 meters</td>
        <td>Moderate Concealment; partially masked behind oak trunks.</td>
        <td>Partial occlusion robustness, micro-texture extraction.</td>
      </tr>
      <tr>
        <td><strong>Tier 3: Far</strong></td>
        <td>7.2 meters to 9.5 meters</td>
        <td>Heavy Camouflage; blending deeply into distant tree clusters.</td>
        <td>Extreme low-resolution bounding box discovery (box height &lt; 65 pixels).</td>
      </tr>
      <tr>
        <td><strong>Tier 4: Flank</strong></td>
        <td>5.0 meters to 8.0 meters</td>
        <td>Deep Shrub & Boulder Cover; situated on lateral flanks.</td>
        <td>Evaluates S-curve sinusoidal exploration sweep efficacy.</td>
      </tr>
    </tbody>
  </table>

  <div class="callout callout-info">
    <div class="callout-title">🌲 Strategic Companion Cover Placement</div>
    In real ecosystems, camouflaged prey animals stand immediately adjacent to trees or boulders to disrupt their physical silhouette. In <code class="inline-code">generate_random_world.py</code>, whenever a deer is placed, the algorithm automatically spawns a <strong>companion natural cover object</strong> (an oak tree, pine tree, or rock boulder) at a randomized distance of 0.6 to 1.2 meters from the deer:
    <br><code class="inline-code">cx = dx + cover_dist * cos(cover_angle) ; cy = dy + cover_dist * sin(cover_angle)</code>
    <br>This forces the AI to detect the animal based on micro-texture rather than relying on an isolated silhouette outline against an empty background!
  </div>

  <h2 class="sub-title">2.5 Solar Lighting Domain Randomization</h2>
  <p>
    Lighting in outdoor environments varies by time of day, cloud cover, and solar zenith. The generator applies <strong>photometric domain randomization</strong> by computing a randomized 3D solar direction vector:
  </p>

  <div class="formula-box">
    <div class="formula-title">Solar Direction Vector Formula</div>
    <div class="formula-main">
      Sun Direction X = &minus;cos(Compass Angle) &times; cos(Elevation Angle)
      <br>Sun Direction Y = &minus;sin(Compass Angle) &times; cos(Elevation Angle)
      <br>Sun Direction Z = &minus;sin(Elevation Angle)
    </div>
    <div class="formula-details">
      Where Compass Angle is randomized between 0° and 360° (azimuth), and Sun Elevation is randomized between 35° and 70° above the ground plane.
    </div>
    <div class="formula-explanation">
      <strong>What this means in plain words:</strong> The sunlight angle changes randomly every time a new world is generated. This creates dynamic shadows and realistic lighting (from golden-hour morning sun to bright midday glare), ensuring the AI learns real animal textures rather than memorizing fixed shadow shapes.
    </div>
  </div>

  <h2 class="sub-title">2.6 3D Asset Modeling, Materials & Physics Decoupling</h2>
  <p>
    The project maintains a realistic library of 3D assets in <code class="inline-code">models/</code>:
  </p>
  <ul>
    <li><strong>Animal Meshes:</strong> <code class="inline-code">deer</code> (high-resolution textured OBJ), <code class="inline-code">leopard</code> (feline mesh scaled by 4.0&times; to 1.36 meters shoulder height with rosette pattern), <code class="inline-code">fox</code>, <code class="inline-code">rabbit</code>, and <code class="inline-code">snake</code> (articulated multi-segment cylinder model).</li>
    <li><strong>Flora & Terrain Clutter:</strong> <code class="inline-code">oak_tree</code> (OSRF textured bark and branch leaf planes), <code class="inline-code">pine_tree</code> (evergreen coniferous needle textures), and <code class="inline-code">rock</code> (falling rock mesh from Gazebo Fuel with high-roughness diffuse mapping).</li>
  </ul>

  <div class="code-header"><span>OGRE Material Script Architecture</span><span>models/deer/materials/scripts/deer.material</span></div>
  <div class="code-block">
material Animal/Deer
{
  technique
  {
    pass
    {
      ambient 0.90 0.90 0.90 1.0
      diffuse 1.0 1.0 1.0 1.0
      specular 0.05 0.05 0.05 1.0 8.0

      texture_unit
      {
        texture deer_basecolor.jpg
      }
    }
  }
}
  </div>

  <div class="callout callout-warning">
    <div class="callout-title">⚡ Physics Performance: Visual vs Collision Mesh Decoupling</div>
    A major breakthrough in our simulation design is the decoupling of visual and collision meshes:
    <ul>
      <li><strong>Visual Geometry (<code class="inline-code">&lt;visual&gt;</code>):</strong> Loaded directly from high-polygon 3D OBJ/DAE files with UV-mapped photorealistic textures to ensure visual fidelity for the camera sensor.</li>
      <li><strong>Collision Geometry (<code class="inline-code">&lt;collision&gt;</code>):</strong> Replaced with simplified geometric bounding boxes (<code class="inline-code">&lt;box size="1.4 0.6 1.4"/&gt;</code>). This slashes contact calculation complexity from heavy multi-triangle calculations down to ultra-fast constant time, preventing simulation freezing when the robot bumps into obstacles!</li>
    </ul>
  </div>

  <h2 class="sub-title">2.7 CPU Optimization: Achieving 1.0 Real Time Factor on Intel i5</h2>
  <p>
    On consumer laptops lacking dedicated NVIDIA GPUs, running a 3D physics simulator alongside deep neural network inference typically degrades Gazebo's <strong>Real Time Factor (RTF)</strong> to an unplayable 0.25 to 0.40. Two critical optimizations were implemented:
  </p>
  <ol>
    <li><strong>Dynamic Shadow Bypass (<code class="inline-code">&lt;cast_shadows&gt;false&lt;/cast_shadows&gt;</code>):</strong> Disabling directional sunlight shadows in the world file completely removes the expensive multi-pass shadow depth buffer rendering pipeline in OGRE, recovering over 60% of CPU cycles!</li>
    <li><strong>Static Entity Flagging (<code class="inline-code">&lt;static&gt;true&lt;/static&gt;</code>):</strong> All trees, rocks, and camouflaged animals are flagged as static bodies. ODE completely excludes them from dynamic inertia and velocity integration, treating them as fixed immovable boundaries.</li>
  </ol>

  <h2 class="sub-title">2.8 Part 2 Dedicated Viva & Oral Exam Defense Guide</h2>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q2.1</span> Why did you use SDF 1.6 for the world instead of defining everything in URDF?</div>
    <div class="viva-concept">Topic Focus: Simulation Description Format (SDF) Architecture</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      URDF was created strictly to describe the kinematics and dynamics of a single robot mechanism formatted as an acyclic directed tree. URDF has no mechanism to define a global coordinate environment, multiple independent free-floating objects, directional lighting parameters, solar shadows, or ground planes.
      <br><br>
      SDF (Simulation Description Format 1.6) is Gazebo's native XML schema designed specifically to represent complete world environments containing dozens of independent models, nested include tags, physics parameters (such as gravity and solver step sizes), and complex OGRE material shading passes.
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q2.2</span> How does your procedural placement algorithm guarantee no overlapping trees or animals?</div>
    <div class="viva-concept">Topic Focus: Procedural Generation & Spatial Collision</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      Our generator maintains a dynamic list of placed objects as tuples of (X, Y, Exclusion Radius, Model Name). For example, a deer has an exclusion radius of 0.9 meters, a tree has 1.0 meter, and a rock has 0.8 meters.
      <br><br>
      Before accepting any randomly sampled coordinate, the algorithm computes the straight-line distance to every already-placed object. If the distance is less than the sum of both objects' radii, the candidate position is rejected and re-sampled. Furthermore, it enforces a 2.0-meter empty clearance circle around the origin (0, 0) to prevent spawning obstacles on top of the robot.
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q2.3</span> Why did you spawn companion rocks and trees within 0.6m–1.2m of each deer?</div>
    <div class="viva-concept">Topic Focus: Ecological Camouflage Scenarios</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      In genuine biological ecosystems, animals do not stand in empty open fields; they exploit natural cover (tree trunks, brush, rock outcroppings) so that their body contours merge with the background texture. 
      <br><br>
      If an animal is placed in an open clearing, even an untrained neural network can detect it simply by identifying the isolated silhouette outline against grass. Spawning companion cover within 0.6 to 1.2 meters creates visual occlusion, dappled shadow casting, and edge disruption, realistically replicating the ecological conditions of cryptic camouflage.
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q2.4</span> Explain how solar domain randomization works and why it is essential for AI evaluation.</div>
    <div class="viva-concept">Topic Focus: Lighting Physics & Domain Randomization</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      Deep neural networks are notorious for overfitting to specific lighting directions and shadow shapes. If the sun is always fixed at noon, the model memorizes downward-cast shadows rather than true animal features.
      <br><br>
      Our procedural generator randomizes the solar vector across an compass angle of 0° to 360° and solar elevation between 35° and 70° above the horizon, while modulating diffuse color channels between 0.75 and 0.95. This exposes the camera to backlighting, direct glare, oblique shadows, and golden-hour warmth, ensuring the perception system generalizes across all daytime outdoor conditions.
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q2.5</span> What was the single biggest optimization that allowed Gazebo to run at 1.0 RTF on an Intel i5 CPU?</div>
    <div class="viva-concept">Topic Focus: CPU Performance & Real Time Factor</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      Disabling dynamic shadows (<code class="inline-code">&lt;cast_shadows&gt;false&lt;/cast_shadows&gt;</code>) in the world SDF light tag. 
      In software rendering mode, calculating real-time shadow maps for dozens of high-polygon tree canopies and complex meshes requires thousands of CPU shader calculations per frame. Removing shadows reduced CPU rasterization overhead by ~65%, immediately elevating the Real Time Factor from an unstable 0.35 up to a smooth, synchronized 1.0.
    </div>
  </div>
</div>
"""
