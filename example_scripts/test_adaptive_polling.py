#!/usr/bin/env python3
# test_adaptive_polling.py

import asyncio
import sys
import time
from datetime import datetime
from maxsmart import MaxSmartDiscovery, MaxSmartDevice
from maxsmart.exceptions import DiscoveryError, ConnectionError

async def discover_devices():
    """Discover MaxSmart devices on the network."""
    print("Discovering MaxSmart devices...")
    try:
        discovery = MaxSmartDiscovery()
        devices = await discovery.discover_maxsmart()
        return devices
    except ConnectionError as ce:
        print(f"Connection error occurred during discovery: {ce}")
        return []
    except DiscoveryError as de:
        print(f"Discovery error occurred: {de}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during discovery: {e}")
        return []

def select_device(devices):
    """Allow the user to select a specific device."""
    if not devices:
        print("No devices available for selection.")
        return None

    print("Available MaxSmart devices:")
    for i, device in enumerate(devices, start=1):
        print(f"{i}. Name: {device['name']}, IP: {device['ip']}, SN: {device['sn']}")

    while True:
        choice = input("Select a device by number: ")
        try:
            choice = int(choice)
            if 1 <= choice <= len(devices):
                return devices[choice - 1]
            else:
                print("Invalid choice. Please select a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def format_timestamp(timestamp):
    """Format timestamp for display."""
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S.%f")[:-3]

async def test_basic_polling(device):
    """Test basic adaptive polling functionality."""
    print("\n" + "="*60)
    print("TEST 1: Basic Adaptive Polling")
    print("="*60)
    
    # Setup polling logger
    poll_count = 0
    
    def poll_logger(poll_data):
        nonlocal poll_count
        poll_count += 1
        
        timestamp = format_timestamp(poll_data['timestamp'])
        mode = poll_data['mode']
        device_data = poll_data.get('device_data', {})
        switch_states = device_data.get('switch', [])
        watt_values = device_data.get('watt', [])
        
        # Format switch states as ON/OFF
        switch_text = [f"P{i+1}:{'ON' if s else 'OFF'}" for i, s in enumerate(switch_states)]
        
        # Format watt values
        watt_text = [f"{w:.1f}W" for w in watt_values]
        
        print(f"[{timestamp}] Poll #{poll_count:2d} | Mode: {mode:6s} | "
              f"States: {' '.join(switch_text)} | Watts: {' '.join(watt_text)}")
    
    try:
        # Register logger and start polling
        device.register_poll_callback("logger", poll_logger)
        await device.start_adaptive_polling()
        
        print(f"Started polling on device {device.name} ({device.ip})")
        print("Observing normal polling (5s intervals)...")
        print("⚠️  Press Ctrl+C to skip to next test")
        
        # Let it poll normally for 15 seconds
        await asyncio.sleep(15)
        
        print(f"\nPolling stats: {device.polling_stats}")
        print(f"Total polls so far: {poll_count}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Basic polling test interrupted (got {poll_count} polls)")
        raise
    finally:
        # Cleanup callback
        device.unregister_poll_callback("logger")

async def test_burst_mode(device):
    """Test burst mode triggering after commands."""
    print("\n" + "="*60)
    print("TEST 2: Burst Mode After Commands")
    print("="*60)
    
    try:
        # Test turning on port 1
        print("Executing: turn_on(port=1)")
        print("This should trigger BURST mode (2s intervals for 4 cycles)")
        print("⚠️  Press Ctrl+C to skip to next test")
        
        await device.turn_on(1)
        
        # Watch burst mode for 12 seconds (should see 4 burst polls + return to normal)
        await asyncio.sleep(12)
        
        print(f"\nPolling stats after turn_on: {device.polling_stats}")
        
        # Test turning off port 1
        print("\nExecuting: turn_off(port=1)")
        print("This should trigger another BURST mode")
        
        await device.turn_off(1)
        
        # Watch another burst cycle
        await asyncio.sleep(12)
        
        print(f"\nPolling stats after turn_off: {device.polling_stats}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Burst mode test interrupted")
        raise

async def test_realtime_monitoring(device):
    """Test real-time change detection."""
    print("\n" + "="*60)
    print("TEST 3: Real-time Change Detection")
    print("="*60)
    
    # Setup change detection callbacks
    def on_consumption_change(data):
        timestamp = format_timestamp(data['timestamp'])
        port_name = data['port_name']
        change = data['change']
        current = data['current_watt']
        
        print(f"🔥 [{timestamp}] CONSUMPTION CHANGE: {port_name} → {current:.1f}W ({change:+.1f}W)")
    
    def on_state_change(data):
        timestamp = format_timestamp(data['timestamp'])
        port_name = data['port_name']
        state = data['state_text']
        
        print(f"⚡ [{timestamp}] STATE CHANGE: {port_name} → {state}")
    
    try:
        # Setup monitoring
        await device.setup_realtime_monitoring(
            consumption_callback=on_consumption_change,
            state_callback=on_state_change
        )
        
        print("Real-time monitoring active!")
        print("Performing operations to trigger changes...")
        print("⚠️  Press Ctrl+C to skip to next test")
        
        # Test multiple operations
        operations = [
            ("turn_on", 1),
            ("turn_off", 1),
            ("turn_on", 2),
            ("turn_off", 2),
            ("turn_on", 0),  # All ports
            ("turn_off", 0)  # All ports
        ]
        
        for operation, port in operations:
            print(f"\nExecuting: {operation}(port={port})")
            
            if operation == "turn_on":
                await device.turn_on(port)
            else:
                await device.turn_off(port)
            
            # Wait to see changes
            await asyncio.sleep(3)
        
        print("\nWaiting for final changes...")
        await asyncio.sleep(5)
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Real-time monitoring test interrupted")
        raise
    finally:
        # Cleanup monitoring callbacks
        device.unregister_poll_callback("change_detector")

async def test_polling_statistics(device):
    """Test polling statistics and management."""
    print("\n" + "="*60)
    print("TEST 4: Polling Statistics & Management")
    print("="*60)
    
    # Get current stats
    stats = device.polling_stats
    print("Current polling statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test force poll
    print("\nTesting force poll...")
    start_time = time.time()
    poll_data = await device.force_poll()
    end_time = time.time()
    
    print(f"Force poll completed in {(end_time - start_time)*1000:.1f}ms")
    print(f"Poll data timestamp: {format_timestamp(poll_data['timestamp'])}")
    
    # Test polling control
    print("\nTesting polling stop/start...")
    await device.stop_adaptive_polling()
    print(f"Polling stopped. Is polling: {device.is_polling}")
    
    await asyncio.sleep(2)
    
    await device.start_adaptive_polling()
    print(f"Polling restarted. Is polling: {device.is_polling}")
    
    # Wait to see some polls
    await asyncio.sleep(8)
    
    # Final stats
    final_stats = device.polling_stats
    print(f"\nFinal polling statistics:")
    for key, value in final_stats.items():
        print(f"  {key}: {value}")

async def test_health_check(device):
    """Test health check functionality."""
    print("\n" + "="*60)
    print("TEST 5: Health Check")
    print("="*60)
    
    health = await device.health_check()
    
    print("Health check results:")
    for key, value in health.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for subkey, subvalue in value.items():
                print(f"    {subkey}: {subvalue}")
        else:
            print(f"  {key}: {value}")

async def cleanup_device(device):
    """Safely cleanup device resources."""
    if device:
        try:
            print(f"\nStopping polling and closing device {device.ip}...")
            await device.stop_adaptive_polling()
            await device.close()
            print(f"✅ Device {device.ip} closed successfully")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

async def main():
    """Main test function with proper interrupt handling."""
    device = None
    
    try:
        # Discover devices
        devices = await discover_devices()
        if not devices:
            print("No MaxSmart devices found. Exiting.")
            return
        
        # Select device
        selected_device = select_device(devices)
        if not selected_device:
            return
        
        # Create device instance
        device = MaxSmartDevice(selected_device['ip'])
        await device.initialize_device()
        
        print(f"\nTesting adaptive polling on device: {device}")
        print(f"Device info: {device.name} - Firmware: {device.version}")
        print("\n⚠️  Press Ctrl+C at any time to stop tests safely")
        
        # Ask user which tests to run
        print("\nAvailable tests:")
        print("1. Basic Polling (normal 5s intervals)")
        print("2. Burst Mode (2s intervals after commands)")
        print("3. Real-time Monitoring (change detection)")
        print("4. Polling Statistics & Management")
        print("5. Health Check")
        print("6. Run All Tests")
        
        try:
            choice = input("\nSelect test to run (1-6): ")
        except (KeyboardInterrupt, EOFError):
            print("\n\n⚠️  Test selection interrupted")
            return
        
        # Run selected test with interrupt handling
        try:
            if choice == "1":
                await test_basic_polling(device)
            elif choice == "2":
                await test_burst_mode(device)
            elif choice == "3":
                await test_realtime_monitoring(device)
            elif choice == "4":
                await test_polling_statistics(device)
            elif choice == "5":
                await test_health_check(device)
            elif choice == "6":
                # Run all tests
                await test_basic_polling(device)
                await test_burst_mode(device)
                await test_realtime_monitoring(device)
                await test_polling_statistics(device)
                await test_health_check(device)
            else:
                print("Invalid choice. Running basic polling test.")
                await test_basic_polling(device)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user (Ctrl+C)")
            print("Cleaning up...")
            return
        except asyncio.CancelledError:
            print("\n\n⚠️  Test cancelled")
            return
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user (Ctrl+C)")
    except EOFError:
        print("\n\n⚠️  Input stream closed")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # ALWAYS cleanup, no matter what happens
        await cleanup_device(device)

def signal_handler():
    """Handle system signals gracefully."""
    print("\n\n🛑 Received interrupt signal, cleaning up...")

if __name__ == "__main__":
    print("MaxSmart Adaptive Polling Test Suite")
    print("=====================================")
    print("This script tests the new adaptive polling functionality")
    print("that mimics the official MaxSmart app behavior.")
    print()
    
    # Setup signal handling for clean shutdown
    import signal
    
    def handle_interrupt(signum, frame):
        print("\n\n🛑 Interrupt received, shutting down gracefully...")
        raise KeyboardInterrupt()
    
    signal.signal(signal.SIGINT, handle_interrupt)
    signal.signal(signal.SIGTERM, handle_interrupt)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Program terminated by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    finally:
        print("\n👋 Goodbye!")