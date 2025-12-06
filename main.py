"""First-person dungeon crawler with raycasting"""

import pygame
import asyncio
from src.game import Game

async def main():
    """Main entry point"""
    pygame.init()
    game = Game()
    await game.run()
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
