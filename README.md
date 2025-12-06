# Dungeon Crawler

A first-person dungeon crawler using raycasting, inspired by classic games like Dungeon Master and Legend of Grimrock.

## Controls

- **W/↑**: Move forward
- **S/↓**: Move backward
- **A**: Strafe left
- **D**: Strafe right
- **Q/←**: Turn left
- **E/→**: Turn right
- **ESC**: Quit

## Running Locally

```bash
python main.py
```

## Building for Web

```bash
python -m pygbag --PYBUILD 3.12 --ume_block 0 .
```

## Features

- Raycasting 3D rendering
- Grid-based movement
- Minimap
- Distance-based shading
- Web deployment ready

## Next Steps

- Add textures to walls
- Add enemies and combat
- Add items and inventory
- Add multiple levels
- Add lighting effects
