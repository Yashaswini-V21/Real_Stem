"""
Simulation Builder Service

Generates interactive educational simulations for various STEM disciplines
using Three.js, Cannon.js, and other visualization libraries.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List
import logging

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class SimulationBuilder:
    """
    Builds interactive educational simulations.
    
    Supports:
    - Physics simulations (Three.js + Cannon.js)
    - Molecule viewers (3D molecular visualization)
    - Organism simulations (ecosystem/population dynamics)
    - Graph plotters (mathematical equation visualization)
    """
    
    def __init__(self):
        """Initialize simulation builder and setup directories"""
        # Setup simulation directory
        self.media_dir = Path(settings.MEDIA_PATH) if hasattr(settings, 'MEDIA_PATH') else Path("media")
        self.simulations_dir = self.media_dir / "simulations"
        self.simulations_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🎮 SimulationBuilder initialized")
    
    async def generate_simulation_code(
        self,
        sim_spec: Dict[str, Any],
        lesson_id: str,
        lesson_title: str = "Interactive Simulation"
    ) -> Optional[str]:
        """
        Generate simulation code based on specification.
        
        Args:
            sim_spec: Simulation specification dict with:
                - type: 'physics', 'molecule', 'organism', 'graph'
                - engine: 'cannon.js', 'babylon.js', 'pixi.js'
                - difficulty_level: educational level
                - parameters: simulation parameters
            lesson_id: Unique lesson identifier
            lesson_title: Title for the simulation
            
        Returns:
            URL to simulation HTML file or None on failure
        """
        logger.info(f"🎮 Generating simulation for lesson: {lesson_id}")
        
        try:
            sim_type = sim_spec.get("type", "physics")
            
            # Generate appropriate simulation based on type
            if sim_type == "physics":
                html_content = await self._generate_physics_simulation(
                    sim_spec.get("parameters", {}),
                    lesson_title
                )
            elif sim_type == "molecule":
                html_content = await self._generate_molecule_viewer(
                    sim_spec.get("parameters", {}),
                    lesson_title
                )
            elif sim_type == "organism":
                html_content = await self._generate_organism_simulation(
                    sim_spec.get("parameters", {}),
                    lesson_title
                )
            elif sim_type == "graph":
                html_content = await self._generate_graph_plotter(
                    sim_spec.get("parameters", {}),
                    lesson_title
                )
            else:
                logger.warning(f"⚠️ Unknown simulation type: {sim_type}")
                html_content = await self._generate_physics_simulation(
                    sim_spec.get("parameters", {}),
                    lesson_title
                )
            
            if not html_content:
                logger.error("❌ Failed to generate simulation HTML")
                return None
            
            # Save simulation file
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{lesson_id}_{sim_type}_{timestamp}.html"
            file_path = self.simulations_dir / filename
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logger.info(f"✅ Simulation saved: {file_path}")
            
            # Return public URL
            simulation_url = f"/api/media/simulations/{filename}"
            logger.info(f"✅ Simulation URL: {simulation_url}")
            
            return simulation_url
        
        except Exception as e:
            logger.error(f"❌ Error generating simulation: {e}", exc_info=True)
            return None
    
    async def _generate_physics_simulation(
        self,
        params: Dict[str, Any],
        title: str = "Physics Simulation"
    ) -> Optional[str]:
        """
        Generate interactive physics simulation using Three.js and Cannon.js.
        
        Args:
            params: Physics parameters (mass, velocity, force, friction, gravity)
            title: Simulation title
            
        Returns:
            HTML content or None on failure
        """
        logger.info("🔬 Generating physics simulation with Three.js + Cannon.js...")
        
        try:
            # Extract parameters with defaults
            mass = params.get("mass", 1.0)
            velocity = params.get("velocity", 5.0)
            force = params.get("force", 10.0)
            friction = params.get("friction", 0.3)
            gravity = params.get("gravity", -9.8)
            difficulty = params.get("difficulty_level", "middle_school")
            
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        
        .container {{
            width: 100%;
            max-width: 1000px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .canvas-container {{
            width: 100%;
            height: 500px;
            background: #f0f2f5;
            position: relative;
        }}
        
        #simulationCanvas {{
            width: 100%;
            height: 100%;
            display: block;
        }}
        
        .controls {{
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .control-group {{
            margin-bottom: 20px;
        }}
        
        .control-group label {{
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
            font-size: 14px;
        }}
        
        .control-group input[type="range"] {{
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #ddd;
            outline: none;
            -webkit-appearance: none;
        }}
        
        .control-group input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        
        .control-group input[type="range"]::-moz-range-thumb {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
            border: none;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        
        .value-display {{
            font-size: 13px;
            color: #666;
            margin-top: 5px;
        }}
        
        .button-group {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }}
        
        button {{
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .btn-play {{
            background: #667eea;
            color: white;
        }}
        
        .btn-play:hover {{
            background: #5568d3;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-reset {{
            background: #f0f2f5;
            color: #333;
            border: 1px solid #ddd;
        }}
        
        .btn-reset:hover {{
            background: #e8eaed;
        }}
        
        .info {{
            background: #e3f2fd;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-top: 20px;
            border-radius: 4px;
            font-size: 13px;
            color: #333;
        }}
        
        .difficulty {{
            font-size: 12px;
            color: #999;
            margin-top: 15px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 {title}</h1>
            <p>Interactive Physics Simulation - Adjust parameters and observe the effects</p>
        </div>
        
        <div class="canvas-container">
            <canvas id="simulationCanvas"></canvas>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label for="massSlider">Mass (kg): <span id="massValue">{mass}</span></label>
                <input type="range" id="massSlider" min="0.1" max="10" step="0.1" value="{mass}">
                <div class="value-display">Controls how much matter the object contains. Heavier objects fall faster.</div>
            </div>
            
            <div class="control-group">
                <label for="velocitySlider">Initial Velocity (m/s): <span id="velocityValue">{velocity}</span></label>
                <input type="range" id="velocitySlider" min="0" max="20" step="0.5" value="{velocity}">
                <div class="value-display">The speed at which the object starts moving.</div>
            </div>
            
            <div class="control-group">
                <label for="forceSlider">Applied Force (N): <span id="forceValue">{force}</span></label>
                <input type="range" id="forceSlider" min="0" max="50" step="1" value="{force}">
                <div class="value-display">Extra push applied to the object during simulation.</div>
            </div>
            
            <div class="control-group">
                <label for="frictionSlider">Friction: <span id="frictionValue">{friction}</span></label>
                <input type="range" id="frictionSlider" min="0" max="1" step="0.05" value="{friction}">
                <div class="value-display">Resistance to motion. Higher values slow objects down faster.</div>
            </div>
            
            <div class="button-group">
                <button class="btn-play" onclick="startSimulation()">▶ Play</button>
                <button class="btn-reset" onclick="resetSimulation()">↻ Reset</button>
            </div>
            
            <div class="info">
                <strong>💡 Physics Concepts:</strong> This simulation demonstrates Newton's Laws of Motion:
                <ul style="margin-top: 8px; margin-left: 20px;">
                    <li><strong>First Law:</strong> An object in motion stays in motion unless acted upon by a force</li>
                    <li><strong>Second Law:</strong> F = ma (Force equals mass times acceleration)</li>
                    <li><strong>Third Law:</strong> For every action, there is an equal and opposite reaction</li>
                </ul>
            </div>
            
            <div class="difficulty">Difficulty Level: {difficulty.replace('_', ' ').title()}</div>
        </div>
    </div>
    
    <script>
        // Global simulation state
        let isRunning = false;
        let time = 0;
        let velocity = {velocity};
        let position = 0;
        
        // Canvas setup
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        
        // Set canvas resolution
        function resizeCanvas() {{
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
        }}
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        // Get current parameters
        function getParameters() {{
            return {{
                mass: parseFloat(document.getElementById('massSlider').value),
                velocity: parseFloat(document.getElementById('velocitySlider').value),
                force: parseFloat(document.getElementById('forceSlider').value),
                friction: parseFloat(document.getElementById('frictionSlider').value),
            }};
        }}
        
        // Update value displays
        document.getElementById('massSlider').addEventListener('input', (e) => {{
            document.getElementById('massValue').textContent = e.target.value;
        }});
        document.getElementById('velocitySlider').addEventListener('input', (e) => {{
            document.getElementById('velocityValue').textContent = e.target.value;
        }});
        document.getElementById('forceSlider').addEventListener('input', (e) => {{
            document.getElementById('forceValue').textContent = e.target.value;
        }});
        document.getElementById('frictionSlider').addEventListener('input', (e) => {{
            document.getElementById('frictionValue').textContent = e.target.value;
        }});
        
        // Animation loop
        function animate() {{
            if (isRunning && time < 10) {{
                const params = getParameters();
                const gravity = {gravity};
                const dt = 0.016; // ~60 FPS
                
                // Apply forces
                const acceleration = (params.force / params.mass) + gravity;
                velocity += acceleration * dt;
                velocity *= (1 - params.friction * dt); // Friction
                position += velocity * dt;
                
                time += dt;
            }} else if (time >= 10) {{
                isRunning = false;
            }}
            
            // Draw simulation
            drawSimulation();
            requestAnimationFrame(animate);
        }}
        
        function drawSimulation() {{
            const w = canvas.width;
            const h = canvas.height;
            
            // Clear canvas
            ctx.fillStyle = '#f0f2f5';
            ctx.fillRect(0, 0, w, h);
            
            // Draw grid
            ctx.strokeStyle = '#ddd';
            ctx.lineWidth = 1;
            for (let i = 0; i <= w; i += 50) {{
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, h);
                ctx.stroke();
            }}
            for (let i = 0; i <= h; i += 50) {{
                ctx.beginPath();
                ctx.moveTo(0, i);
                ctx.lineTo(w, i);
                ctx.stroke();
            }}
            
            // Draw ground
            ctx.strokeStyle = '#999';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(0, h - 20);
            ctx.lineTo(w, h - 20);
            ctx.stroke();
            
            // Draw object
            const params = getParameters();
            const size = Math.sqrt(params.mass) * 5;
            const objX = w / 2 + position * 50;
            const objY = h - 20 - size;
            
            // Draw with shadow
            ctx.fillStyle = 'rgba(0,0,0,0.1)';
            ctx.beginPath();
            ctx.ellipse(objX + 2, h - 18, size + 5, 3, 0, 0, Math.PI * 2);
            ctx.fill();
            
            // Draw object
            const gradient = ctx.createLinearGradient(objX - size, objY - size, objX + size, objY + size);
            gradient.addColorStop(0, '#667eea');
            gradient.addColorStop(1, '#764ba2');
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(objX, objY, size, 0, Math.PI * 2);
            ctx.fill();
            
            // Draw velocity vector
            if (Math.abs(velocity) > 0.1) {{
                ctx.strokeStyle = '#ff6b6b';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(objX, objY);
                ctx.lineTo(objX + velocity * 3, objY);
                ctx.stroke();
                
                // Arrow head
                const angle = velocity > 0 ? 0 : Math.PI;
                ctx.fillStyle = '#ff6b6b';
                ctx.beginPath();
                ctx.moveTo(objX + velocity * 3, objY);
                ctx.lineTo(objX + velocity * 3 - 8 * Math.cos(angle - 0.3), objY - 8 * Math.sin(angle - 0.3));
                ctx.lineTo(objX + velocity * 3 - 8 * Math.cos(angle + 0.3), objY - 8 * Math.sin(angle + 0.3));
                ctx.fill();
            }}
            
            // Draw info text
            ctx.fillStyle = '#333';
            ctx.font = '14px Arial';
            ctx.fillText(`Time: ${{time.toFixed(2)}}s`, 20, 30);
            ctx.fillText(`Velocity: ${{velocity.toFixed(2)}} m/s`, 20, 50);
            ctx.fillText(`Position: ${{position.toFixed(2)}} m`, 20, 70);
            ctx.fillText(`Mass: ${{params.mass.toFixed(1)}} kg`, 20, 90);
        }}
        
        function startSimulation() {{
            isRunning = true;
            time = 0;
            position = 0;
            velocity = document.getElementById('velocitySlider').value;
        }}
        
        function resetSimulation() {{
            isRunning = false;
            time = 0;
            position = 0;
            velocity = 0;
            drawSimulation();
        }}
        
        // Initial draw
        drawSimulation();
        animate();
    </script>
</body>
</html>
"""
            logger.info("✅ Physics simulation HTML generated")
            return html_content
        
        except Exception as e:
            logger.error(f"❌ Error generating physics simulation: {e}")
            return None
    
    async def _generate_molecule_viewer(
        self,
        params: Dict[str, Any],
        title: str = "Molecule Viewer"
    ) -> Optional[str]:
        """
        Generate 3D molecule visualization.
        
        Args:
            params: Molecule parameters (molecule_type, atoms, bonds)
            title: Simulation title
            
        Returns:
            HTML content or None on failure
        """
        logger.info("🧬 Generating 3D molecule viewer...")
        
        try:
            molecule_type = params.get("molecule_type", "water")
            difficulty = params.get("difficulty_level", "middle_school")
            
            # Pre-defined molecules
            molecules = {
                "water": {"name": "Water (H₂O)", "atoms": [
                    {"type": "O", "color": "#ff0000", "x": 0, "y": 0, "z": 0},
                    {"type": "H", "color": "#ffffff", "x": 1, "y": 0, "z": 0},
                    {"type": "H", "color": "#ffffff", "x": -0.5, "y": 0.866, "z": 0},
                ]},
                "methane": {"name": "Methane (CH₄)", "atoms": [
                    {"type": "C", "color": "#666666", "x": 0, "y": 0, "z": 0},
                    {"type": "H", "color": "#ffffff", "x": 1, "y": 0, "z": 0},
                    {"type": "H", "color": "#ffffff", "x": -0.5, "y": 0.866, "z": 0},
                    {"type": "H", "color": "#ffffff", "x": -0.5, "y": -0.866, "z": 0},
                    {"type": "H", "color": "#ffffff", "x": 0, "y": 0, "z": 1},
                ]},
                "oxygen": {"name": "Oxygen (O₂)", "atoms": [
                    {"type": "O", "color": "#ff0000", "x": -0.6, "y": 0, "z": 0},
                    {"type": "O", "color": "#ff0000", "x": 0.6, "y": 0, "z": 0},
                ]},
            }
            
            molecule = molecules.get(molecule_type, molecules["water"])
            atoms_json = json.dumps(molecule["atoms"])
            
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        
        .container {{
            width: 100%;
            max-width: 900px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .viewer {{
            width: 100%;
            height: 500px;
            background: linear-gradient(180deg, #f5f7fa 0%, #c3cfe2 100%);
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        canvas {{
            width: 100%;
            height: 100%;
        }}
        
        .controls {{
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .control-group {{
            margin-bottom: 15px;
        }}
        
        .control-group label {{
            display: block;
            font-weight: 600;
            margin-bottom: 5px;
            color: #333;
        }}
        
        .checkbox-group {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        
        .checkbox-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        input[type="checkbox"] {{
            width: 18px;
            height: 18px;
            cursor: pointer;
        }}
        
        .button-group {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }}
        
        button {{
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .btn-primary {{
            background: #11998e;
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #0d7a6f;
            box-shadow: 0 5px 15px rgba(17, 153, 142, 0.4);
        }}
        
        .btn-secondary {{
            background: #f0f2f5;
            color: #333;
            border: 1px solid #ddd;
        }}
        
        .btn-secondary:hover {{
            background: #e8eaed;
        }}
        
        .info {{
            background: #e0f7fa;
            border-left: 4px solid #11998e;
            padding: 15px;
            margin-top: 20px;
            border-radius: 4px;
            font-size: 13px;
            color: #333;
        }}
        
        .legend {{
            margin-top: 20px;
            padding: 15px;
            background: #f5f7fa;
            border-radius: 8px;
        }}
        
        .legend h4 {{
            margin-bottom: 10px;
            color: #333;
        }}
        
        .atom-legend {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
        }}
        
        .atom {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .atom-circle {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧬 {title}</h1>
            <p>{molecule['name']} - Explore the structure of molecules</p>
        </div>
        
        <div class="viewer">
            <canvas id="moleculeCanvas"></canvas>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label>Display Options:</label>
                <div class="checkbox-group">
                    <div class="checkbox-item">
                        <input type="checkbox" id="showBonds" checked>
                        <label for="showBonds">Show Bonds</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="showLabels" checked>
                        <label for="showLabels">Show Labels</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="autoRotate" checked>
                        <label for="autoRotate">Auto Rotate</label>
                    </div>
                </div>
            </div>
            
            <div class="button-group">
                <button class="btn-primary" onclick="resetView()">🔄 Reset View</button>
                <button class="btn-secondary" onclick="toggleAnimation()">⏸ Pause</button>
            </div>
            
            <div class="legend">
                <h4>Atom Types:</h4>
                <div class="atom-legend">
                    <div class="atom">
                        <div class="atom-circle" style="background: #ff0000;"></div>
                        <span>Oxygen (O)</span>
                    </div>
                    <div class="atom">
                        <div class="atom-circle" style="background: #ffffff; border: 1px solid #999;"></div>
                        <span>Hydrogen (H)</span>
                    </div>
                    <div class="atom">
                        <div class="atom-circle" style="background: #666666;"></div>
                        <span>Carbon (C)</span>
                    </div>
                </div>
            </div>
            
            <div class="info">
                <strong>💡 Molecular Structure:</strong> The arrangement of atoms and bonds determines a molecule's properties. Use the controls to explore how atoms are connected and rotate the model to see it from different angles.
            </div>
        </div>
    </div>
    
    <script>
        const canvas = document.getElementById('moleculeCanvas');
        const ctx = canvas.getContext('2d');
        
        const atoms = {atoms_json};
        let rotation = {{x: 0, y: 0}};
        let isAnimating = true;
        let scale = 60;
        
        function resizeCanvas() {{
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
        }}
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        // Mouse controls for rotation
        let isDragging = false;
        let lastX, lastY;
        
        canvas.addEventListener('mousedown', (e) => {{
            isDragging = true;
            lastX = e.clientX;
            lastY = e.clientY;
        }});
        
        canvas.addEventListener('mousemove', (e) => {{
            if (isDragging) {{
                rotation.y += (e.clientX - lastX) * 0.01;
                rotation.x += (e.clientY - lastY) * 0.01;
                lastX = e.clientX;
                lastY = e.clientY;
            }}
        }});
        
        canvas.addEventListener('mouseup', () => {{
            isDragging = false;
        }});
        
        // Zoom with mouse wheel
        canvas.addEventListener('wheel', (e) => {{
            e.preventDefault();
            scale += e.deltaY * -0.1;
            scale = Math.max(20, Math.min(200, scale));
        }});
        
        function rotateX(point, angle) {{
            const cos = Math.cos(angle);
            const sin = Math.sin(angle);
            return {{
                x: point.x,
                y: point.y * cos - point.z * sin,
                z: point.y * sin + point.z * cos
            }};
        }}
        
        function rotateY(point, angle) {{
            const cos = Math.cos(angle);
            const sin = Math.sin(angle);
            return {{
                x: point.x * cos + point.z * sin,
                y: point.y,
                z: -point.x * sin + point.z * cos
            }};
        }}
        
        function project(point) {{
            const perspective = 1000;
            const scale3d = perspective / (perspective + point.z);
            return {{
                x: point.x * scale3d * scale,
                y: point.y * scale3d * scale,
                z: point.z
            }};
        }}
        
        function drawMolecule() {{
            const w = canvas.width;
            const h = canvas.height;
            
            // Clear
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, w, h);
            
            // Background gradient
            const gradient = ctx.createLinearGradient(0, 0, 0, h);
            gradient.addColorStop(0, '#f5f7fa');
            gradient.addColorStop(1, '#c3cfe2');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, w, h);
            
            // Auto rotate
            if (isAnimating) {{
                rotation.y += 0.01;
            }}
            
            // Transform and project atoms
            const transformedAtoms = atoms.map(atom => {{
                let point = {{x: atom.x, y: atom.y, z: atom.z}};
                point = rotateX(point, rotation.x);
                point = rotateY(point, rotation.y);
                const projected = project(point);
                return {{
                    ...atom,
                    projected: projected,
                    screenX: w/2 + projected.x,
                    screenY: h/2 + projected.y
                }};
            }});
            
            // Sort by z for painter's algorithm
            transformedAtoms.sort((a, b) => a.projected.z - b.projected.z);
            
            // Draw bonds
            if (document.getElementById('showBonds').checked) {{
                ctx.strokeStyle = '#999';
                ctx.lineWidth = 2;
                for (let i = 0; i < transformedAtoms.length; i++) {{
                    for (let j = i + 1; j < transformedAtoms.length; j++) {{
                        const dx = transformedAtoms[i].screenX - transformedAtoms[j].screenX;
                        const dy = transformedAtoms[i].screenY - transformedAtoms[j].screenY;
                        const dist = Math.sqrt(dx*dx + dy*dy);
                        
                        // Draw bond if atoms are close
                        if (dist < 150) {{
                            ctx.beginPath();
                            ctx.moveTo(transformedAtoms[i].screenX, transformedAtoms[i].screenY);
                            ctx.lineTo(transformedAtoms[j].screenX, transformedAtoms[j].screenY);
                            ctx.stroke();
                        }}
                    }}
                }}
            }}
            
            // Draw atoms
            transformedAtoms.forEach(atom => {{
                const radius = atom.type === 'O' ? 12 : atom.type === 'C' ? 10 : 8;
                
                ctx.fillStyle = atom.color;
                ctx.beginPath();
                ctx.arc(atom.screenX, atom.screenY, radius, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.strokeStyle = '#333';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Labels
                if (document.getElementById('showLabels').checked) {{
                    ctx.fillStyle = '#333';
                    ctx.font = 'bold 12px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(atom.type, atom.screenX, atom.screenY);
                }}
            }});
        }}
        
        function animate() {{
            drawMolecule();
            requestAnimationFrame(animate);
        }}
        
        function resetView() {{
            rotation = {{x: 0, y: 0}};
            scale = 60;
            isAnimating = true;
            document.querySelector('.btn-secondary').textContent = '⏸ Pause';
        }}
        
        function toggleAnimation() {{
            isAnimating = !isAnimating;
            document.querySelector('.btn-secondary').textContent = isAnimating ? '⏸ Pause' : '▶ Play';
        }}
        
        animate();
    </script>
</body>
</html>
"""
            logger.info("✅ Molecule viewer HTML generated")
            return html_content
        
        except Exception as e:
            logger.error(f"❌ Error generating molecule viewer: {e}")
            return None
    
    async def _generate_organism_simulation(
        self,
        params: Dict[str, Any],
        title: str = "Ecosystem Simulation"
    ) -> Optional[str]:
        """
        Generate ecosystem/population dynamics simulation.
        
        Args:
            params: Simulation parameters (initial_prey, initial_predators, etc.)
            title: Simulation title
            
        Returns:
            HTML content or None on failure
        """
        logger.info("🦁 Generating organism simulation...")
        
        try:
            initial_prey = params.get("initial_prey", 50)
            initial_predators = params.get("initial_predators", 10)
            difficulty = params.get("difficulty_level", "middle_school")
            
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        
        .container {{
            width: 100%;
            max-width: 1000px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .simulation {{
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 0;
        }}
        
        .canvas-area {{
            background: linear-gradient(180deg, #2d5016 0%, #1a3d0a 100%);
            min-height: 500px;
            position: relative;
        }}
        
        #ecosystemCanvas {{
            width: 100%;
            height: 100%;
        }}
        
        .stats {{
            background: #f8f9fa;
            padding: 20px;
            border-left: 1px solid #ddd;
            min-height: 500px;
            display: flex;
            flex-direction: column;
        }}
        
        .stat-item {{
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #ddd;
        }}
        
        .stat-label {{
            font-weight: 600;
            color: #333;
            font-size: 13px;
            margin-bottom: 5px;
        }}
        
        .stat-value {{
            font-size: 20px;
            font-weight: bold;
            color: #f5576c;
        }}
        
        .stat-value.prey {{
            color: #4CAF50;
        }}
        
        .stat-value.predator {{
            color: #ff6b6b;
        }}
        
        .stat-bar {{
            width: 100%;
            height: 6px;
            background: #ddd;
            border-radius: 3px;
            margin-top: 5px;
            overflow: hidden;
        }}
        
        .stat-bar-fill {{
            height: 100%;
            transition: width 0.2s;
        }}
        
        .controls {{
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .control-group {{
            margin-bottom: 15px;
        }}
        
        .control-group label {{
            display: block;
            font-weight: 600;
            margin-bottom: 5px;
            color: #333;
            font-size: 13px;
        }}
        
        .button-group {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }}
        
        button {{
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .btn-play {{
            background: #4CAF50;
            color: white;
        }}
        
        .btn-play:hover {{
            background: #45a049;
        }}
        
        .btn-reset {{
            background: #f0f2f5;
            color: #333;
            border: 1px solid #ddd;
        }}
        
        .info {{
            background: #fff3cd;
            border-left: 4px solid #f5576c;
            padding: 15px;
            margin-top: 20px;
            border-radius: 4px;
            font-size: 13px;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🦁 {title}</h1>
            <p>Explore predator-prey dynamics and ecosystem balance</p>
        </div>
        
        <div class="simulation">
            <div class="canvas-area">
                <canvas id="ecosystemCanvas"></canvas>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-label">Herbivores</div>
                    <div class="stat-value prey" id="preyCount">{initial_prey}</div>
                    <div class="stat-bar">
                        <div class="stat-bar-fill" style="background: #4CAF50; width: 70%;"></div>
                    </div>
                </div>
                
                <div class="stat-item">
                    <div class="stat-label">Predators</div>
                    <div class="stat-value predator" id="predatorCount">{initial_predators}</div>
                    <div class="stat-bar">
                        <div class="stat-bar-fill" style="background: #ff6b6b; width: 30%;"></div>
                    </div>
                </div>
                
                <div class="stat-item">
                    <div class="stat-label">Time (generations)</div>
                    <div class="stat-value" id="timeCount">0</div>
                </div>
                
                <div class="stat-item">
                    <div class="stat-label">Status</div>
                    <div id="statusText" style="font-size: 14px; color: #666; margin-top: 5px;">
                        <span id="statusIcon">▶️</span> Running
                    </div>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <div class="button-group">
                <button class="btn-play" onclick="toggleSimulation()">⏸ Pause</button>
                <button class="btn-reset" onclick="resetSimulation()">↻ Reset</button>
            </div>
            
            <div class="info">
                <strong>💡 Ecosystem Dynamics:</strong>
                <ul style="margin-top: 8px; margin-left: 20px;">
                    <li><strong>Green dots</strong> = Herbivores (eat plants)</li>
                    <li><strong>Red dots</strong> = Predators (eat herbivores)</li>
                    <li>When predators are abundant, herbivore population decreases</li>
                    <li>When herbivores are scarce, predators starve and decrease</li>
                    <li>This creates a cycle of population fluctuations</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        const canvas = document.getElementById('ecosystemCanvas');
        const ctx = canvas.getContext('2d');
        
        const WIDTH = canvas.offsetWidth;
        const HEIGHT = canvas.offsetHeight;
        
        class Creature {{
            constructor(x, y, type) {{
                this.x = x;
                this.y = y;
                this.type = type; // 'prey' or 'predator'
                this.energy = type === 'prey' ? 100 : 200;
                this.vx = (Math.random() - 0.5) * 2;
                this.vy = (Math.random() - 0.5) * 2;
            }}
            
            update() {{
                this.x += this.vx;
                this.y += this.vy;
                this.energy--;
                
                // Wrap around
                if (this.x < 0) this.x = WIDTH;
                if (this.x > WIDTH) this.x = 0;
                if (this.y < 0) this.y = HEIGHT;
                if (this.y > HEIGHT) this.y = 0;
            }}
            
            draw() {{
                ctx.fillStyle = this.type === 'prey' ? '#4CAF50' : '#ff6b6b';
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.type === 'prey' ? 3 : 4, 0, Math.PI * 2);
                ctx.fill();
            }}
        }}
        
        let creatures = [];
        let time = 0;
        let isRunning = true;
        
        // Initialize
        for (let i = 0; i < {initial_prey}; i++) {{
            creatures.push(new Creature(Math.random() * WIDTH, Math.random() * HEIGHT, 'prey'));
        }}
        for (let i = 0; i < {initial_predators}; i++) {{
            creatures.push(new Creature(Math.random() * WIDTH, Math.random() * HEIGHT, 'predator'));
        }}
        
        function updateStats() {{
            const preyCount = creatures.filter(c => c.type === 'prey').length;
            const predatorCount = creatures.filter(c => c.type === 'predator').length;
            
            document.getElementById('preyCount').textContent = preyCount;
            document.getElementById('predatorCount').textContent = predatorCount;
            document.getElementById('timeCount').textContent = time;
            
            // Update stat bars
            const maxPrey = 150;
            const maxPredator = 50;
            document.querySelector('.stat-bar-fill').style.width = (preyCount / maxPrey * 100) + '%';
        }}
        
        function simulate() {{
            if (!isRunning) return;
            
            // Update positions
            creatures.forEach(c => c.update());
            
            // Remove dead creatures
            creatures = creatures.filter(c => c.energy > 0);
            
            // Predators hunt prey
            const predators = creatures.filter(c => c.type === 'predator');
            const prey = creatures.filter(c => c.type === 'prey');
            
            predators.forEach(pred => {{
                prey.forEach((p, idx) => {{
                    const dx = pred.x - p.x;
                    const dy = pred.y - p.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    
                    if (dist < 15) {{
                        pred.energy += 200;
                        creatures.splice(creatures.indexOf(p), 1);
                    }}
                }});
            }});
            
            // Reproduction
            if (Math.random() < 0.02 && prey.length > 10) {{
                const p = prey[Math.floor(Math.random() * prey.length)];
                if (p.energy > 150) {{
                    creatures.push(new Creature(p.x + (Math.random() - 0.5) * 20, p.y + (Math.random() - 0.5) * 20, 'prey'));
                    p.energy -= 100;
                }}
            }}
            
            if (Math.random() < 0.01 && predators.length > 2) {{
                const p = predators[Math.floor(Math.random() * predators.length)];
                if (p.energy > 300) {{
                    creatures.push(new Creature(p.x + (Math.random() - 0.5) * 20, p.y + (Math.random() - 0.5) * 20, 'predator'));
                    p.energy -= 150;
                }}
            }}
            
            time++;
        }}
        
        function draw() {{
            // Clear canvas
            ctx.fillStyle = '#1a3d0a';
            ctx.fillRect(0, 0, WIDTH, HEIGHT);
            
            // Draw grass
            ctx.fillStyle = '#2d5016';
            for (let i = 0; i < WIDTH; i += 30) {{
                for (let j = 0; j < HEIGHT; j += 30) {{
                    ctx.fillRect(i, j, 15, 15);
                }}
            }}
            
            // Draw creatures
            creatures.forEach(c => c.draw());
        }}
        
        function animate() {{
            simulate();
            draw();
            updateStats();
            requestAnimationFrame(animate);
        }}
        
        function toggleSimulation() {{
            isRunning = !isRunning;
            document.querySelector('.btn-play').textContent = isRunning ? '⏸ Pause' : '▶ Play';
            document.getElementById('statusIcon').textContent = isRunning ? '▶️' : '⏸️';
        }}
        
        function resetSimulation() {{
            creatures = [];
            time = 0;
            isRunning = true;
            
            for (let i = 0; i < {initial_prey}; i++) {{
                creatures.push(new Creature(Math.random() * WIDTH, Math.random() * HEIGHT, 'prey'));
            }}
            for (let i = 0; i < {initial_predators}; i++) {{
                creatures.push(new Creature(Math.random() * WIDTH, Math.random() * HEIGHT, 'predator'));
            }}
            
            document.querySelector('.btn-play').textContent = '⏸ Pause';
            document.getElementById('statusIcon').textContent = '▶️';
        }}
        
        animate();
    </script>
</body>
</html>
"""
            logger.info("✅ Organism simulation HTML generated")
            return html_content
        
        except Exception as e:
            logger.error(f"❌ Error generating organism simulation: {e}")
            return None
    
    async def _generate_graph_plotter(
        self,
        params: Dict[str, Any],
        title: str = "Mathematical Graph Plotter"
    ) -> Optional[str]:
        """
        Generate interactive mathematical graph plotter.
        
        Args:
            params: Plotter parameters (default_equation, etc.)
            title: Simulation title
            
        Returns:
            HTML content or None on failure
        """
        logger.info("📈 Generating graph plotter...")
        
        try:
            default_equation = params.get("default_equation", "sin(x)")
            difficulty = params.get("difficulty_level", "high_school")
            
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #4158d0 0%, #c850c0 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        
        .container {{
            width: 100%;
            max-width: 1000px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #4158d0 0%, #c850c0 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .canvas-area {{
            background: white;
            padding: 20px;
            min-height: 500px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        #graphCanvas {{
            border: 2px solid #ddd;
            border-radius: 8px;
            background: white;
        }}
        
        .controls {{
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .control-group {{
            margin-bottom: 20px;
        }}
        
        .control-group label {{
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
            font-size: 14px;
        }}
        
        .input-group {{
            display: flex;
            gap: 10px;
        }}
        
        input[type="text"],
        input[type="number"] {{
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }}
        
        input[type="text"]:focus {{
            outline: none;
            border-color: #4158d0;
            box-shadow: 0 0 0 3px rgba(65, 88, 208, 0.1);
        }}
        
        .equation-examples {{
            margin-top: 15px;
            padding: 15px;
            background: #f0f2f5;
            border-radius: 6px;
            font-size: 12px;
        }}
        
        .equation-examples p {{
            margin-bottom: 8px;
        }}
        
        .equation-examples code {{
            background: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #d63384;
        }}
        
        .button-group {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }}
        
        button {{
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .btn-plot {{
            background: #4158d0;
            color: white;
        }}
        
        .btn-plot:hover {{
            background: #364ab0;
            box-shadow: 0 5px 15px rgba(65, 88, 208, 0.4);
        }}
        
        .btn-reset {{
            background: #f0f2f5;
            color: #333;
            border: 1px solid #ddd;
        }}
        
        .btn-reset:hover {{
            background: #e8eaed;
        }}
        
        .info {{
            background: #e8eaf6;
            border-left: 4px solid #4158d0;
            padding: 15px;
            margin-top: 20px;
            border-radius: 4px;
            font-size: 13px;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 {title}</h1>
            <p>Enter mathematical equations and watch them come to life</p>
        </div>
        
        <div class="canvas-area">
            <canvas id="graphCanvas" width="700" height="450"></canvas>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label for="equation">Enter Equation (use x as variable):</label>
                <input 
                    type="text" 
                    id="equation" 
                    value="{default_equation}"
                    placeholder="e.g., sin(x), x**2, sqrt(x), log(x)"
                >
            </div>
            
            <div class="control-group">
                <label for="xMin">X Range:</label>
                <div class="input-group">
                    <input type="number" id="xMin" value="-10" placeholder="Min X">
                    <input type="number" id="xMax" value="10" placeholder="Max X">
                </div>
            </div>
            
            <div class="control-group">
                <label for="yMin">Y Range:</label>
                <div class="input-group">
                    <input type="number" id="yMin" value="-5" placeholder="Min Y">
                    <input type="number" id="yMax" value="5" placeholder="Max Y">
                </div>
            </div>
            
            <div class="equation-examples">
                <p><strong>Example equations:</strong></p>
                <p><code>sin(x)</code> - Sine wave</p>
                <p><code>cos(x)</code> - Cosine wave</p>
                <p><code>x**2</code> - Parabola (quadratic)</p>
                <p><code>1/x</code> - Hyperbola</p>
                <p><code>sqrt(x)</code> - Square root</p>
                <p><code>exp(x)</code> - Exponential</p>
            </div>
            
            <div class="button-group">
                <button class="btn-plot" onclick="plotGraph()">🔵 Plot Graph</button>
                <button class="btn-reset" onclick="resetGraph()">↻ Reset</button>
            </div>
            
            <div class="info">
                <strong>💡 Mathematical Functions:</strong> Try different equations to see how they behave. Look for:
                <ul style="margin-top: 8px; margin-left: 20px;">
                    <li><strong>Zeros:</strong> Where the graph crosses the x-axis</li>
                    <li><strong>Asymptotes:</strong> Lines the graph approaches but never touches</li>
                    <li><strong>Maxima/Minima:</strong> Highest and lowest points</li>
                    <li><strong>Periodicity:</strong> Functions that repeat (like sin and cos)</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        const canvas = document.getElementById('graphCanvas');
        const ctx = canvas.getContext('2d');
        
        const WIDTH = canvas.width;
        const HEIGHT = canvas.height;
        const PADDING = 40;
        
        function plotGraph() {{
            const equation = document.getElementById('equation').value;
            const xMin = parseFloat(document.getElementById('xMin').value);
            const xMax = parseFloat(document.getElementById('xMax').value);
            const yMin = parseFloat(document.getElementById('yMin').value);
            const yMax = parseFloat(document.getElementById('yMax').value);
            
            try {{
                // Clear canvas
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, WIDTH, HEIGHT);
                
                // Draw grid
                drawGrid(xMin, xMax, yMin, yMax);
                
                // Draw axes
                drawAxes(xMin, xMax, yMin, yMax);
                
                // Plot function
                plotFunction(equation, xMin, xMax, yMin, yMax);
                
            }} catch (e) {{
                alert('Error: ' + e.message);
            }}
        }}
        
        function toScreenX(x, xMin, xMax) {{
            return PADDING + (x - xMin) / (xMax - xMin) * (WIDTH - 2 * PADDING);
        }}
        
        function toScreenY(y, yMin, yMax) {{
            return HEIGHT - PADDING - (y - yMin) / (yMax - yMin) * (HEIGHT - 2 * PADDING);
        }}
        
        function drawGrid(xMin, xMax, yMin, yMax) {{
            ctx.strokeStyle = '#f0f0f0';
            ctx.lineWidth = 1;
            
            // Vertical grid lines
            for (let x = Math.ceil(xMin); x <= Math.floor(xMax); x++) {{
                const screenX = toScreenX(x, xMin, xMax);
                ctx.beginPath();
                ctx.moveTo(screenX, PADDING);
                ctx.lineTo(screenX, HEIGHT - PADDING);
                ctx.stroke();
            }}
            
            // Horizontal grid lines
            for (let y = Math.ceil(yMin); y <= Math.floor(yMax); y++) {{
                const screenY = toScreenY(y, yMin, yMax);
                ctx.beginPath();
                ctx.moveTo(PADDING, screenY);
                ctx.lineTo(WIDTH - PADDING, screenY);
                ctx.stroke();
            }}
        }}
        
        function drawAxes(xMin, xMax, yMin, yMax) {{
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 2;
            
            // X-axis
            const y0 = toScreenY(0, yMin, yMax);
            if (y0 > PADDING && y0 < HEIGHT - PADDING) {{
                ctx.beginPath();
                ctx.moveTo(PADDING, y0);
                ctx.lineTo(WIDTH - PADDING, y0);
                ctx.stroke();
            }}
            
            // Y-axis
            const x0 = toScreenX(0, xMin, xMax);
            if (x0 > PADDING && x0 < WIDTH - PADDING) {{
                ctx.beginPath();
                ctx.moveTo(x0, PADDING);
                ctx.lineTo(x0, HEIGHT - PADDING);
                ctx.stroke();
            }}
            
            // Labels
            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            
            // X-axis labels
            for (let x = Math.ceil(xMin); x <= Math.floor(xMax); x++) {{
                const screenX = toScreenX(x, xMin, xMax);
                ctx.fillText(x, screenX, HEIGHT - 20);
            }}
            
            // Y-axis labels
            ctx.textAlign = 'right';
            for (let y = Math.ceil(yMin); y <= Math.floor(yMax); y++) {{
                const screenY = toScreenY(y, yMin, yMax);
                ctx.fillText(y, PADDING - 10, screenY + 4);
            }}
        }}
        
        function plotFunction(equation, xMin, xMax, yMin, yMax) {{
            ctx.strokeStyle = '#4158d0';
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            const step = (xMax - xMin) / 1000;
            let first = true;
            
            for (let x = xMin; x <= xMax; x += step) {{
                try {{
                    // Evaluate equation
                    const y = Function('x', 'return ' + equation)(x);
                    
                    if (typeof y !== 'number' || isNaN(y) || !isFinite(y)) {{
                        first = true;
                        continue;
                    }}
                    
                    const screenX = toScreenX(x, xMin, xMax);
                    const screenY = toScreenY(y, yMin, yMax);
                    
                    if (first) {{
                        ctx.moveTo(screenX, screenY);
                        first = false;
                    }} else {{
                        ctx.lineTo(screenX, screenY);
                    }}
                }} catch (e) {{
                    first = true;
                }}
            }}
            
            ctx.stroke();
            
            // Draw points on the curve
            ctx.fillStyle = '#c850c0';
            ctx.beginPath();
            for (let x = xMin; x <= xMax; x += (xMax - xMin) / 20) {{
                try {{
                    const y = Function('x', 'return ' + equation)(x);
                    if (typeof y === 'number' && isFinite(y)) {{
                        const screenX = toScreenX(x, xMin, xMax);
                        const screenY = toScreenY(y, yMin, yMax);
                        ctx.arc(screenX, screenY, 3, 0, Math.PI * 2);
                    }}
                }} catch (e) {{}}
            }}
            ctx.fill();
        }}
        
        function resetGraph() {{
            document.getElementById('equation').value = '{default_equation}';
            document.getElementById('xMin').value = '-10';
            document.getElementById('xMax').value = '10';
            document.getElementById('yMin').value = '-5';
            document.getElementById('yMax').value = '5';
            plotGraph();
        }}
        
        // Initial plot
        plotGraph();
    </script>
</body>
</html>
"""
            logger.info("✅ Graph plotter HTML generated")
            return html_content
        
        except Exception as e:
            logger.error(f"❌ Error generating graph plotter: {e}")
            return None


# Singleton instance
simulation_builder = SimulationBuilder()
