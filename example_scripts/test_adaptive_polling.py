#!/usr/bin/env python3
# test_adaptive_polling.py

import asyncio
import sys
import time
from datetime import datetime
from maxsmart import MaxSmartDiscovery, MaxSmartDevice
from maxsmart.exceptions import DiscoveryError, ConnectionError

class TestResults:
    """Store and manage test results data."""
    
    def __init__(self):
        self.polls = []
        self.changes = []
        self.commands = []
        self.start_time = time.time()
        
    def add_poll(self, poll_data):
        """Add poll data."""
        self.polls.append({
            'timestamp': poll_data['timestamp'],
            'mode': poll_data['mode'],
            'poll_count': poll_data['poll_count'],
            'switch': poll_data['device_data'].get('switch', []),
            'watt': poll_data['device_data'].get('watt', [])
        })
        
    def add_change(self, change_type, data):
        """Add change event."""
        self.changes.append({
            'type': change_type,
            'timestamp': data['timestamp'],
            'port': data['port'],
            'data': data
        })
        
    def add_command(self, command, port, original_state):
        """Add command execution."""
        self.commands.append({
            'timestamp': time.time(),
            'command': command,
            'port': port,
            'original_state': original_state
        })
        
    def get_summary(self):
        """Get test results summary."""
        duration = time.time() - self.start_time
        return {
            'duration': duration,
            'total_polls': len(self.polls),
            'total_changes': len(self.changes),
            'total_commands': len(self.commands),
            'normal_polls': len([p for p in self.polls if p['mode'] == 'normal']),
            'burst_polls': len([p for p in self.polls if p['mode'] == 'burst']),
            'avg_poll_interval': duration / len(self.polls) if self.polls else 0
        }

async def discover_devices():
    """Discover MaxSmart devices on the network."""
    print("🔍 Discovering MaxSmart devices...")
    try:
        discovery = MaxSmartDiscovery()
        devices = await discovery.discover_maxsmart()
        return devices
    except Exception as e:
        print(f"❌ Discovery error: {e}")
        return []

def select_device(devices):
    """Allow the user to select a specific device."""
    if not devices:
        print("❌ No devices available.")
        return None

    print("\n📱 Available MaxSmart devices:")
    for i, device in enumerate(devices, start=1):
        print(f"  {i}. {device['name']} ({device['ip']}) - FW: {device.get('ver', 'Unknown')}")

    while True:
        try:
            choice = input("\nSelect device number: ")
            choice = int(choice)
            if 1 <= choice <= len(devices):
                return devices[choice - 1]
            else:
                print("❌ Invalid choice. Try again.")
        except (ValueError, KeyboardInterrupt, EOFError):
            return None

def select_port(device, port_names):
    """Allow user to select a port for testing."""
    print(f"\n🔌 Available ports on {device.name}:")
    print("  0. Master (all ports)")
    for i in range(1, 7):
        port_name = port_names.get(f'Port {i}', f'Port {i}')
        print(f"  {i}. {port_name}")
    
    while True:
        try:
            choice = input("\nSelect port number (0-6): ")
            choice = int(choice)
            if 0 <= choice <= 6:
                return choice
            else:
                print("❌ Invalid port. Choose 0-6.")
        except (ValueError, KeyboardInterrupt, EOFError):
            return None

async def get_port_state(device, port):
    """Get current state of a port safely."""
    try:
        if port == 0:
            states = await device.check_state()
            return states  # Return list for master port
        else:
            return await device.check_state(port)
    except Exception as e:
        print(f"❌ Error getting port {port} state: {e}")
        return None

def show_test_menu():
    """Show available tests."""
    print("\n🧪 Available Tests:")
    print("  1. Basic Polling Observer (just watch)")
    print("  2. Burst Mode Test (safe port toggle)")
    print("  3. Real-time Monitoring (manual changes)")
    print("  4. Polling Statistics")
    print("  5. Back to device selection")
    print("  6. Exit")

async def test_basic_polling(device, results):
    """Test basic polling - just observe."""
    print("\n" + "="*60)
    print("🔍 TEST: Basic Polling Observer")
    print("="*60)
    print("📊 Watching polling behavior (no commands sent)")
    print("⏱️  Observing for 20 seconds...")
    print("⚠️  Press Ctrl+C to stop early")
    
    def poll_observer(poll_data):
        results.add_poll(poll_data)
        timestamp = datetime.fromtimestamp(poll_data['timestamp']).strftime("%H:%M:%S.%f")[:-3]
        mode = poll_data['mode']
        count = poll_data['poll_count']
        
        # Show basic info without overwhelming detail
        print(f"[{timestamp}] Poll #{count:2d} | Mode: {mode:6s}")
    
    try:
        device.register_poll_callback("observer", poll_observer)
        await device.start_adaptive_polling()
        
        await asyncio.sleep(20)
        
    except KeyboardInterrupt:
        print("\n⚠️  Observation interrupted")
    finally:
        device.unregister_poll_callback("observer")
        
    # Show results
    summary = results.get_summary()
    print(f"\n📈 Results:")
    print(f"  Duration: {summary['duration']:.1f}s")
    print(f"  Total polls: {summary['total_polls']}")
    print(f"  Average interval: {summary['avg_poll_interval']:.1f}s")

async def test_burst_mode(device, results):
    """Test burst mode with user-selected port."""
    print("\n" + "="*60)
    print("⚡ TEST: Burst Mode (Safe Toggle)")
    print("="*60)
    
    # Get port names
    try:
        port_names = await device.retrieve_port_names()
    except Exception as e:
        print(f"❌ Error getting port names: {e}")
        return
    
    # User selects port
    port = select_port(device, port_names)
    if port is None:
        return
        
    # Get current state
    original_state = await get_port_state(device, port)
    if original_state is None:
        return
        
    port_name = port_names.get(f'Port {port}', f'Port {port}') if port > 0 else "Master"
    
    if port == 0:
        state_text = "Mixed" if isinstance(original_state, list) else str(original_state)
    else:
        state_text = "ON" if original_state else "OFF"
        
    print(f"\n🎯 Selected: {port_name} (currently {state_text})")
    
    confirm = input("Continue with safe toggle test? (y/N): ")
    if confirm.lower() != 'y':
        return
    
    def poll_observer(poll_data):
        results.add_poll(poll_data)
        timestamp = datetime.fromtimestamp(poll_data['timestamp']).strftime("%H:%M:%S.%f")[:-3]
        mode = poll_data['mode']
        count = poll_data['poll_count']
        
        if poll_data['mode'] == 'burst':
            print(f"🚀 [{timestamp}] BURST Poll #{count} (fast mode)")
        else:
            print(f"⏱️  [{timestamp}] Normal Poll #{count}")
    
    try:
        device.register_poll_callback("burst_observer", poll_observer)
        
        if not device.is_polling:
            await device.start_adaptive_polling()
            
        print(f"\n🔄 Test sequence:")
        
        # First toggle (opposite of current state)
        if port == 0 or (port > 0 and original_state == 0):
            print("  1. Turn ON → should trigger BURST mode")
            results.add_command("turn_on", port, original_state)
            await device.turn_on(port)
        else:
            print("  1. Turn OFF → should trigger BURST mode")
            results.add_command("turn_off", port, original_state)
            await device.turn_off(port)
            
        await asyncio.sleep(10)  # Watch burst
        
        print("  2. Restore original state → another BURST")
        # Restore original state
        if port == 0 or (port > 0 and original_state == 1):
            results.add_command("turn_on", port, None)
            await device.turn_on(port)
        else:
            results.add_command("turn_off", port, None)
            await device.turn_off(port)
            
        await asyncio.sleep(10)  # Watch burst
        
        print("✅ Port restored to original state")
        
    except KeyboardInterrupt:
        print("\n⚠️  Burst test interrupted - restoring state...")
        # Try to restore state
        try:
            if port == 0 or (port > 0 and original_state == 1):
                await device.turn_on(port)
            else:
                await device.turn_off(port)
        except:
            pass
    finally:
        device.unregister_poll_callback("burst_observer")
        
    # Show results
    summary = results.get_summary()
    burst_polls = summary['burst_polls']
    print(f"\n📈 Burst Mode Results:")
    print(f"  Commands executed: {summary['total_commands']}")
    print(f"  Burst polls detected: {burst_polls}")
    print(f"  Total polls: {summary['total_polls']}")

async def test_burst_mode_targeted(device, results, target_port, port_name):
    """Test burst mode with pre-selected port."""
    print("\n" + "="*60)
    print(f"⚡ TEST: Burst Mode on {port_name}")
    print("="*60)
    
    # Get current state
    original_state = await get_port_state(device, target_port)
    if original_state is None:
        return
        
    if target_port == 0:
        state_text = "Mixed" if isinstance(original_state, list) else str(original_state)
    else:
        state_text = "ON" if original_state else "OFF"
        
    print(f"🔍 Current state: {state_text}")
    
    confirm = input("Continue with safe toggle test? (y/N): ")
    if confirm.lower() != 'y':
        return
    
    def poll_observer(poll_data):
        results.add_poll(poll_data)
        timestamp = datetime.fromtimestamp(poll_data['timestamp']).strftime("%H:%M:%S.%f")[:-3]
        mode = poll_data['mode']
        count = poll_data['poll_count']
        
        if poll_data['mode'] == 'burst':
            print(f"🚀 [{timestamp}] BURST Poll #{count} (fast mode)")
        else:
            print(f"⏱️  [{timestamp}] Normal Poll #{count}")
    
    try:
        device.register_poll_callback("burst_observer", poll_observer)
        
        if not device.is_polling:
            await device.start_adaptive_polling()
            
        print(f"\n🔄 Test sequence on {port_name}:")
        
        # First toggle (opposite of current state)
        if target_port == 0 or (target_port > 0 and original_state == 0):
            print("  1. Turn ON → should trigger BURST mode")
            results.add_command("turn_on", target_port, original_state)
            await device.turn_on(target_port)
        else:
            print("  1. Turn OFF → should trigger BURST mode")
            results.add_command("turn_off", target_port, original_state)
            await device.turn_off(target_port)
            
        await asyncio.sleep(10)  # Watch burst
        
        print("  2. Restore original state → another BURST")
        # Restore original state
        if target_port == 0 or (target_port > 0 and original_state == 1):
            results.add_command("turn_on", target_port, None)
            await device.turn_on(target_port)
        else:
            results.add_command("turn_off", target_port, None)
            await device.turn_off(target_port)
            
        await asyncio.sleep(10)  # Watch burst
        
        print(f"✅ {port_name} restored to original state")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Burst test interrupted - restoring {port_name}...")
        # Try to restore state
        try:
            if target_port == 0 or (target_port > 0 and original_state == 1):
                await device.turn_on(target_port)
            else:
                await device.turn_off(target_port)
        except:
            pass
    finally:
        device.unregister_poll_callback("burst_observer")
        
    # Show results
    summary = results.get_summary()
    burst_polls = summary['burst_polls']
    print(f"\n📈 Burst Mode Results for {port_name}:")
    print(f"  Commands executed: {summary['total_commands']}")
    print(f"  Burst polls detected: {burst_polls}")
    print(f"  Total polls: {summary['total_polls']}")

async def test_realtime_monitoring_targeted(device, results, target_port, port_name):
    """Test real-time monitoring with pre-selected port."""
    print("\n" + "="*60)
    print(f"🔥 TEST: Real-time Monitoring on {port_name}")
    print("="*60)
    
    # Get initial state to avoid false positives
    initial_data = await device.get_data()
    initial_watt = initial_data.get('watt', [0] * 6)
    initial_switch = initial_data.get('switch', [0] * 6)
    
    if target_port == 0:
        total_watts = sum(initial_watt)
        on_count = sum(initial_switch)
        print(f"🔍 Initial state: {total_watts:.1f}W total, {on_count}/{device.port_count} ports ON")
    else:
        port_watts = initial_watt[target_port-1] if target_port <= len(initial_watt) else 0
        port_state = initial_switch[target_port-1] if target_port <= len(initial_switch) else 0
        state_text = "ON" if port_state else "OFF"
        print(f"🔍 Initial state: {port_watts:.1f}W ({state_text})")
    
    print("📊 Starting 10 measurement cycles...")
    print(f"💡 You can manually change {port_name} during measurement")
    print("⚠️  Press Ctrl+C to stop early")
    
    measurement_count = 0
    
    async def consumption_callback(data):
        # Only show changes for the target port
        if data['port'] == target_port or target_port == 0:
            results.add_change('consumption', data)
            timestamp = datetime.fromtimestamp(data['timestamp']).strftime("%H:%M:%S.%f")[:-3]
            port_name = data['port_name']
            change = data['change']
            current = data['current_watt']
            print(f"🔥 [{timestamp}] {port_name}: {current:.1f}W ({change:+.1f}W)")
    
    async def state_callback(data):
        # Only show changes for the target port
        if data['port'] == target_port or target_port == 0:
            results.add_change('state', data)
            timestamp = datetime.fromtimestamp(data['timestamp']).strftime("%H:%M:%S.%f")[:-3]
            port_name = data['port_name']
            state = data['state_text']
            print(f"⚡ [{timestamp}] {port_name}: → {state}")
    
    def poll_observer(poll_data):
        nonlocal measurement_count
        measurement_count += 1
        results.add_poll(poll_data)
        
        timestamp = datetime.fromtimestamp(poll_data['timestamp']).strftime("%H:%M:%S.%f")[:-3]
        device_data = poll_data['device_data']
        watt_values = device_data.get('watt', [])
        switch_values = device_data.get('switch', [])
        
        if target_port == 0:
            # Master port - show total
            total_watts = sum(watt_values) if watt_values else 0
            on_count = sum(switch_values) if switch_values else 0
            print(f"📊 [{timestamp}] Measurement #{measurement_count:2d}/10 | "
                  f"Total: {total_watts:.1f}W | Ports ON: {on_count}/{device.port_count}")
        else:
            # Individual port
            port_watts = watt_values[target_port-1] if watt_values and target_port <= len(watt_values) else 0
            port_state = switch_values[target_port-1] if switch_values and target_port <= len(switch_values) else 0
            state_text = "ON" if port_state else "OFF"
            print(f"📊 [{timestamp}] Measurement #{measurement_count:2d}/10 | "
                  f"{port_name}: {port_watts:.1f}W ({state_text})")
        
        if measurement_count >= 10:
            print("✅ 10 measurements completed!")
    
    try:
        # Setup monitoring with initial state
        await device.setup_realtime_monitoring_with_baseline(
            consumption_callback=consumption_callback,
            state_callback=state_callback,
            initial_watt=initial_watt,
            initial_switch=initial_switch
        )
        
        device.register_poll_callback("realtime_observer", poll_observer)
        
        if not device.is_polling:
            await device.start_adaptive_polling()
        
        # Wait for 10 measurements or manual stop
        while measurement_count < 10:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Monitoring stopped (got {measurement_count} measurements)")
    finally:
        device.unregister_poll_callback("realtime_observer")
        device.unregister_poll_callback("change_detector")
        
    # Show results
    summary = results.get_summary()
    consumption_changes = len([c for c in results.changes if c['type'] == 'consumption'])
    state_changes = len([c for c in results.changes if c['type'] == 'state'])
    
    print(f"\n📈 Real-time Monitoring Results for {port_name}:")
    print(f"  Measurements: {measurement_count}/10")
    print(f"  Consumption changes detected: {consumption_changes}")
    print(f"  State changes detected: {state_changes}")
    print(f"  Total changes: {len(results.changes)}")
    
    if results.changes:
        print(f"\n🔍 Change Details:")
        for change in results.changes:
            timestamp = datetime.fromtimestamp(change['timestamp']).strftime("%H:%M:%S")
            change_type = change['type']
            port = change['port']
            print(f"  [{timestamp}] Port {port}: {change_type} change")

# Remove the unused function
async def show_polling_stats(device, results):
    """DEPRECATED - Stats are shown in other tests."""
    print("📊 This test has been removed - stats are shown in other tests.")
    await asyncio.sleep(1)

async def cleanup_device(device):
    """Safely cleanup device resources."""
    if device:
        try:
            print(f"\n🧹 Cleaning up device {device.ip}...")
            await device.stop_adaptive_polling()
            await device.close()
            print(f"✅ Device closed successfully")
        except Exception as e:
            print(f"❌ Cleanup error: {e}")

async def device_test_loop(device):
    """Main device testing loop."""
    results = TestResults()
    
    while True:
        try:
            show_test_menu()
            choice = input("\nSelect test: ")
            
            if choice == "1":
                await test_basic_polling(device, results)
            elif choice == "2":
                await test_burst_mode(device, results)
            elif choice == "3":
                await test_realtime_monitoring(device, results)
            elif choice == "4":
                await show_polling_stats(device, results)
            elif choice == "5":
                return "back"  # Go back to device selection
            elif choice == "6":
                return "exit"
            else:
                print("❌ Invalid choice. Try again.")
                
        except (KeyboardInterrupt, EOFError):
            print("\n⚠️  Test interrupted")
            return "exit"

async def main():
    """Main application loop."""
    print("🧪 MaxSmart Adaptive Polling Test Suite")
    print("========================================")
    print("Safe, intelligent testing with user control")
    print()
    
    while True:
        device = None
        try:
            # Discovery
            devices = await discover_devices()
            if not devices:
                print("❌ No devices found. Exiting.")
                break
                
            # Device selection
            selected_device = select_device(devices)
            if not selected_device:
                break
                
            # Create and initialize device with protocol and serial
            protocol = selected_device.get("protocol", "http")
            serial = selected_device.get("sn", "")
            port_count = selected_device.get("nr_of_ports", 6)

            device = MaxSmartDevice(selected_device['ip'], protocol=protocol, sn=serial)
            device.port_count = port_count  # Set port count from discovery
            await device.initialize_device()

            print(f"\n🔗 Connected to: {device.name} ({device.ip})")
            print(f"📋 Firmware: {device.version}")
            print(f"🔌 Protocol: {protocol}")
            print(f"🌐 MAC: {selected_device.get('mac', 'Unknown')}")
            print(f"🔢 Ports: {port_count}")
            print(f"🆔 Serial: {device.sn}")
            
            # Test loop
            result = await device_test_loop(device)
            
            if result == "exit":
                break
            # If result == "back", continue to device selection
                
        except KeyboardInterrupt:
            print("\n⚠️  Application interrupted")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            await cleanup_device(device)
    
    print("\n👋 Test suite finished. Goodbye!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Program terminated")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
    finally:
        print("🏁 Done.")