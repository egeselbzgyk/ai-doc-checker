#!/usr/bin/env python3
"""
Fast Metadata Generation Script
Generate metadata database for all reference solutions without test system overhead
"""

import time
from datetime import datetime
from metadata_generator import MetadataGenerator

def generate_metadata_standalone():
    """Generate metadata database standalone"""
    print("=" * 60)
    print("🧠 METADATA DATABASE GENERATOR")
    print("=" * 60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    start_time = time.time()
    
    try:
        # Initialize generator
        print("🔄 Initializing metadata generator...")
        generator = MetadataGenerator()
        print("✅ Generator initialized")
        print()
        
        # Generate database
        print("🔄 Processing all reference images...")
        print("   💡 Note: ALL images will be processed (no confidence filtering)")
        print("   ⏱️  Estimated time: ~2-3 hours for 515 images")
        print()
        
        database_path = generator.save_database()
        
        elapsed_time = time.time() - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        
        print()
        print("=" * 60)
        print("🎉 METADATA GENERATION COMPLETE!")
        print("=" * 60)
        print(f"📁 Database saved to: {database_path}")
        print(f"⏱️  Total time: {hours:02d}:{minutes:02d}:{seconds:02d}")
        print(f"📊 Ready for evaluation system!")
        print()
        print("🔧 Next steps:")
        print("   1. Run: python quick_test.py")
        print("   2. Should show: 6/6 components passed ✅")
        print("   3. System ready for student evaluations!")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  Generation interrupted by user")
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        print(f"   Partial progress saved after {minutes:02d}:{seconds:02d}")
        return False
        
    except Exception as e:
        print(f"\n❌ Generation failed: {str(e)}")
        print("🔧 Troubleshooting:")
        print("   - Check SSH tunnel is active: curl http://localhost:5000/health")
        print("   - Verify reference images exist: ../dataset/mapped_train/")
        print("   - Check Qwen server status")
        return False

if __name__ == "__main__":
    print("🚀 Starting metadata generation...")
    print("💡 You can interrupt anytime with Ctrl+C")
    print()
    
    success = generate_metadata_standalone()
    
    if success:
        print("🎯 Ready to evaluate student submissions!")
    else:
        print("⚠️  Generation incomplete - check errors above") 