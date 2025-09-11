#!/usr/bin/env python3
"""
World System Migration Script

This script helps migrate from the old world system to the new modern system
that fixes the flashing tree issue.

Usage:
    python migrate_world_system.py [--backup] [--test]

Options:
    --backup    Create backup of old files before migration
    --test      Run tests to verify the new system works
"""

import sys
import os
import shutil
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def backup_old_files():
    """Create backup of old world system files."""
    backup_dir = Path("backup_world_system")
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        "systems/world.py",
        "systems/world_backup.py", 
        "systems/world_generator.py"
    ]
    
    for file_path in files_to_backup:
        if Path(file_path).exists():
            backup_path = backup_dir / Path(file_path).name
            shutil.copy2(file_path, backup_path)
            print(f"✅ Backed up {file_path} to {backup_path}")
    
    print(f"📁 Backup created in {backup_dir}/")

def test_new_system():
    """Test the new world system to ensure it works correctly."""
    try:
        print("🧪 Testing new world system...")
        
        # Test imports
        from systems.world_generation_modern import ModernWorldGenerator, TreeData, TreeType
        from systems.tree_renderer import ModernTreeRenderer
        from systems.world_modern import ModernWorld
        
        print("✅ All imports successful")
        
        # Test world generation
        world = ModernWorld(seed=12345)
        print("✅ World generation successful")
        
        # Test tree creation
        tree = world.generator._create_tree(10, 10, is_border=True)
        print(f"✅ Tree creation successful: {tree.tree_type.name} with color {tree.leaf_color}")
        
        # Test chunk generation
        chunk = world.get_chunk(0, 0)
        print(f"✅ Chunk generation successful: {len(chunk.tiles)} tiles, {len(chunk.trees)} trees")
        
        # Test tree renderer
        import pygame
        pygame.init()
        screen = pygame.Surface((100, 100))
        renderer = ModernTreeRenderer()
        renderer.render_tree(screen, tree, (50, 50))
        print("✅ Tree rendering successful")
        
        pygame.quit()
        print("🎉 All tests passed! New world system is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_integration_guide():
    """Create a guide for integrating the new world system."""
    guide_content = """# World System Migration Guide

## Overview
This guide explains how to migrate from the old world system to the new modern system that fixes the flashing tree issue.

## Key Changes

### 1. Fixed Flashing Trees
- **Problem**: Trees used `random.choice()` every frame, causing color changes
- **Solution**: Colors are now stored in tree data during generation
- **Result**: Trees maintain consistent colors, no more flashing

### 2. Better Architecture
- **Separation of Concerns**: Generation, rendering, and world management are separate
- **Type Safety**: Full type hints throughout
- **Error Handling**: Comprehensive error handling and logging
- **Performance**: Optimized rendering with caching

### 3. New Files
- `systems/world_generation_modern.py` - Modern world generation
- `systems/tree_renderer.py` - Optimized tree rendering
- `systems/world_modern.py` - Main world system

## Migration Steps

### Step 1: Update Imports
Replace old imports:
```python
# OLD
from systems.world import World
from systems.world_generator import SynapstexWorldGenerator

# NEW
from systems.world_modern import ModernWorld
from systems.world_generation_modern import ModernWorldGenerator
```

### Step 2: Update World Creation
Replace old world creation:
```python
# OLD
world = World(seed=12345)

# NEW
world = ModernWorld(seed=12345)
```

### Step 3: Update Method Calls
Most methods have the same interface, but some have been improved:
```python
# OLD
world.update(dt, graphics)
world.draw(screen, offset)
world.update_chunks(player_x, player_y)

# NEW (same interface)
world.update(dt, graphics)
world.draw(screen, offset)
world.update_chunks(player_x, player_y)
```

### Step 4: Update Graphics Integration
The new system integrates better with SynapstexGraphics:
```python
# The new system automatically handles particle emission
# and integrates with the graphics engine
```

## Benefits

1. **No More Flashing Trees**: Colors are persistent and consistent
2. **Better Performance**: Optimized rendering and caching
3. **Cleaner Code**: Better separation of concerns
4. **Type Safety**: Full type hints for better IDE support
5. **Error Handling**: Comprehensive error handling prevents crashes
6. **Maintainability**: Modular design makes it easier to modify

## Testing

Run the migration script to test the new system:
```bash
python migrate_world_system.py --test
```

## Rollback

If you need to rollback, the old files are backed up in `backup_world_system/`:
```bash
# Restore old files
cp backup_world_system/world.py systems/
cp backup_world_system/world_generator.py systems/
```

## Support

If you encounter any issues during migration, check the logs for detailed error messages.
The new system includes comprehensive logging to help diagnose problems.
"""
    
    with open("WORLD_MIGRATION_GUIDE.md", "w") as f:
        f.write(guide_content)
    
    print("📖 Created WORLD_MIGRATION_GUIDE.md")

def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description="Migrate world system to fix flashing trees")
    parser.add_argument("--backup", action="store_true", help="Create backup of old files")
    parser.add_argument("--test", action="store_true", help="Test new system")
    
    args = parser.parse_args()
    
    print("🚀 World System Migration Tool")
    print("=" * 50)
    
    if args.backup:
        backup_old_files()
    
    if args.test:
        if test_new_system():
            print("\n✅ Migration test successful!")
        else:
            print("\n❌ Migration test failed!")
            sys.exit(1)
    
    create_integration_guide()
    
    print("\n🎯 Next Steps:")
    print("1. Review WORLD_MIGRATION_GUIDE.md")
    print("2. Update your main.py to use ModernWorld")
    print("3. Test the game to verify trees no longer flash")
    print("4. Remove old world files if everything works")

if __name__ == "__main__":
    main()
