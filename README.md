# Organic Buoyancy Solver

**Organic Buoyancy Solver** is a Blender addon that calculates and simulates the hydrostatic equilibrium position (buoyancy) of irregular 3D objects. It is ideal for determining how islands, ship hulls, platforms, or any complex organic geometry would float, taking into account their mass distribution and fluid density.

## 🚀 Features

*   **Precise Physics Calculation**: Uses an iterative Archimedes' Principle approach to balance forces (weight vs. buoyancy) and moments (aligning Center of Gravity with Center of Buoyancy).
*   **Irregular Geometry Support**: Calculates exact submerged volumes by slicing the mesh in real-time (using `bmesh`), avoiding bounding box approximations.
*   **Composite Center of Gravity (COG)**: Allows defining a collection of "Extra Objects" that act as additional weights, recalculating the system's total center of mass.
*   **Optimized Solver**: Performs matrix calculations in memory for fast convergence without needing to update the viewport in every iteration.
*   **Visualization**: Quick tool to generate a visual water plane.

## 📦 Installation

1.  Download this repository (as `.zip` or clone it).
2.  Open Blender (Tested on 4.0+).
3.  Go to **Edit > Preferences > Add-ons**.
4.  If using the zip, click **Install...** and select it. If you cloned the folder, ensure it's in your Blender scripts path or install it manually.
5.  Search for **"Organic Buoyancy Solver"** in the list and enable the checkbox.

## 🛠️ Usage

1.  **Prepare your Scene**: Have a main object (your island or boat). Make sure its origin is in a logical position or use the geometry.
2.  **Control Panel**: In the 3D Viewport, press `N` to open the sidebar and go to the **Hydrostatics** tab.
3.  **Configuration**:
    *   **Target Island**: Select your main object.
    *   **Water Density**: 1025 kg/m³ (saltwater) or 1000 kg/m³ (freshwater).
    *   **Object Density**: Average density of your object (e.g., 30 kg/m³ for EPS foam).
    *   **Extra Objects**: (Optional) Select a collection containing other objects that should add weight to the calculation (buildings, ballast, etc.).
4.  **Run**:
    *   Click **"Calculate Equilibrium"**. The object will move and rotate until it finds its stable floating position.
    *   You can see detailed progress by opening the blender system console (`Window > Toggle System Console`).

## ⚙️ Technical Details

The solver works in an iterative loop:
1.  Calculates the total weight and initial COG of the system.
2.  In each step, calculates the submerged volume and Center of Buoyancy (COB) of the mesh in its current position relative to Z=0.
3.  Applies restoring forces (Heave) based on the net vertical force.
4.  Applies restoring moments (Trim/Heel) to vertically align the COB with the COG.
5.  Stops when net forces and alignment distances are below a precision threshold.

---
Developed with AI assistance.
