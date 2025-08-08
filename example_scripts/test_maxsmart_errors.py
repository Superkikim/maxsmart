#!/usr/bin/env python3
"""
example_scripts/test_maxsmart_errors.py

MaxSmart Error Testing Script for version 2.0.3

This script tests various error conditions to verify improved error messages.
Run this to validate that errors are properly formatted and logged.

Usage:
    python example_scripts/test_maxsmart_errors.py [device_ip]
    
If no device_ip is provided, will test with fake IPs to trigger network errors.
"""

import asyncio
import logging
import sys
import time
from typing import Optional

# Configure detailed logging to see all error messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('maxsmart_error_test.log')
    ]
)

try:
    from maxsmart import MaxSmartDevice, MaxSmartDiscovery
    from maxsmart.exceptions import (
        DiscoveryError, ConnectionError, CommandError, 
        DeviceTimeoutError, FirmwareError, StateError
    )
except ImportError as e:
    print(f"Error importing maxsmart module: {e}")
    print("Make sure maxsmart 2.0.3+ is installed: pip install maxsmart>=2.0.3")
    sys.exit(1)

class ErrorTester:
    """Test various error conditions and validate error messages."""
    
    def __init__(self, real_device_ip: Optional[str] = None):
        self.real_device_ip = real_device_ip
        self.test_results = []
        
    async def run_all_tests(self):
        """Run all error tests."""
        print("🧪 Starting MaxSmart Error Testing Suite")
        print("=" * 60)
        
        # Test 1: Discovery errors
        await self.test_discovery_errors()
        
        # Test 2: Connection timeout errors  
        await self.test_connection_timeouts()
        
        # Test 3: Invalid device IP errors
        await self.test_invalid_device_errors()
        
        # Test 4: Command errors (if real device available)
        if self.real_device_ip:
            await self.test_command_errors()
        else:
            print("⚠️  Skipping command error tests (no real device IP provided)")
            
        # Test 5: JSON/Response errors
        await self.test_response_errors()
        
        # Test 6: Rapid polling stress test
        if self.real_device_ip:
            await self.test_rapid_polling_stress()
        
        # Print summary
        self.print_test_summary()
        
    async def test_discovery_errors(self):
        """Test discovery-related errors."""
        print("\n🔍 Testing Discovery Errors")
        print("-" * 40)
        
        # Test 1: Discovery timeout
        try:
            print("Test 1.1: Discovery with short timeout...")
            devices = await MaxSmartDiscovery.discover_maxsmart(
                ip="192.168.255.254",  # Non-existent IP
                timeout=0.1,  # Very short timeout
                max_attempts=1
            )
            self.test_results.append(("Discovery timeout", "❌ Should have failed"))
        except Exception as e:
            self.test_results.append(("Discovery timeout", f"✅ Error: {type(e).__name__}: {e}"))
            
        # Test 2: Invalid IP format
        try:
            print("Test 1.2: Discovery with invalid IP...")
            devices = await MaxSmartDiscovery.discover_maxsmart(ip="invalid.ip.address")
            self.test_results.append(("Invalid IP discovery", "❌ Should have failed"))
        except Exception as e:
            self.test_results.append(("Invalid IP discovery", f"✅ Error: {type(e).__name__}: {e}"))
            
        # Test 3: Network unreachable
        try:
            print("Test 1.3: Discovery to unreachable network...")
            devices = await MaxSmartDiscovery.discover_maxsmart(
                ip="10.255.255.255",  # Likely unreachable
                timeout=2.0,
                max_attempts=1
            )
            self.test_results.append(("Unreachable network", "❌ Should have failed"))
        except Exception as e:
            self.test_results.append(("Unreachable network", f"✅ Error: {type(e).__name__}: {e}"))
            
    async def test_connection_timeouts(self):
        """Test various connection timeout scenarios."""
        print("\n⏱️  Testing Connection Timeouts")
        print("-" * 40)
        
        fake_ips = [
            "192.168.255.1",   # Likely non-existent
            "169.254.1.1",     # Link-local (may timeout)
            "10.254.254.254",  # Private range endpoint
        ]
        
        for i, ip in enumerate(fake_ips, 1):
            try:
                print(f"Test 2.{i}: Timeout test with {ip}...")
                device = MaxSmartDevice(ip)
                # Short timeout to force timeout error
                device.DEFAULT_TIMEOUT = 2.0
                device.RETRY_COUNT = 1
                
                await device.initialize_device()
                data = await device.get_data()
                self.test_results.append((f"Timeout {ip}", "❌ Should have timed out"))
            except Exception as e:
                self.test_results.append((f"Timeout {ip}", f"✅ Error: {type(e).__name__}: {e}"))
            finally:
                try:
                    await device.close()
                except:
                    pass
                    
    async def test_invalid_device_errors(self):
        """Test errors with invalid device configurations."""
        print("\n❌ Testing Invalid Device Errors")
        print("-" * 40)
        
        # Test 1: Invalid IP format
        try:
            print("Test 3.1: Invalid IP format...")
            device = MaxSmartDevice("not.an.ip.address")
            self.test_results.append(("Invalid IP format", "❌ Should have failed at creation"))
        except Exception as e:
            self.test_results.append(("Invalid IP format", f"✅ Error: {type(e).__name__}: {e}"))
            
        # Test 2: Empty IP
        try:
            print("Test 3.2: Empty IP...")
            device = MaxSmartDevice("")
            self.test_results.append(("Empty IP", "❌ Should have failed"))
        except Exception as e:
            self.test_results.append(("Empty IP", f"✅ Error: {type(e).__name__}: {e}"))
            
        # Test 3: Localhost (should fail as no MaxSmart device)
        try:
            print("Test 3.3: Localhost connection...")
            device = MaxSmartDevice("127.0.0.1")
            device.DEFAULT_TIMEOUT = 3.0
            device.RETRY_COUNT = 1
            await device.initialize_device()
            data = await device.get_data()
            self.test_results.append(("Localhost connection", "❌ Should have failed"))
        except Exception as e:
            self.test_results.append(("Localhost connection", f"✅ Error: {type(e).__name__}: {e}"))
        finally:
            try:
                await device.close()
            except:
                pass
                
    async def test_command_errors(self):
        """Test command errors with a real device."""
        print(f"\n⚡ Testing Command Errors with real device {self.real_device_ip}")
        print("-" * 40)
        
        device = None
        try:
            # Use protocol from discovery if available
            protocol = getattr(self, 'real_device_protocol', 'http')
            serial = getattr(self, 'real_device_serial', '')
            device = MaxSmartDevice(self.real_device_ip, protocol=protocol, sn=serial)
            await device.initialize_device()
            
            # Test 1: Invalid port number
            try:
                print("Test 4.1: Invalid port number...")
                await device.turn_on(99)  # Invalid port
                self.test_results.append(("Invalid port", "❌ Should have failed"))
            except Exception as e:
                self.test_results.append(("Invalid port", f"✅ Error: {type(e).__name__}: {e}"))
                
            # Test 2: Get power data for invalid port
            try:
                print("Test 4.2: Power data for invalid port...")
                power = await device.get_power_data(10)
                self.test_results.append(("Invalid port power", "❌ Should have failed"))
            except Exception as e:
                self.test_results.append(("Invalid port power", f"✅ Error: {type(e).__name__}: {e}"))
                
        except Exception as e:
            self.test_results.append(("Real device setup", f"❌ Failed to setup: {e}"))
        finally:
            if device:
                await device.close()
                
    async def test_response_errors(self):
        """Test response parsing and JSON errors."""
        print("\n📄 Testing Response Format Errors")
        print("-" * 40)
        
        # These tests check the error handling when device returns invalid responses
        # We simulate this by trying to connect to non-MaxSmart HTTP services
        
        http_services = [
            ("httpbin.org", 80),      # Returns different JSON format
            ("example.com", 80),      # Returns HTML, not JSON
            ("google.com", 80),       # Returns HTML with redirects
        ]
        
        for i, (host, port) in enumerate(http_services, 1):
            try:
                print(f"Test 5.{i}: Non-MaxSmart HTTP service {host}...")
                device = MaxSmartDevice(f"{host}")  # This will likely fail with DNS or wrong format
                device.DEFAULT_TIMEOUT = 3.0
                device.RETRY_COUNT = 1
                await device.initialize_device()
                self.test_results.append((f"HTTP service {host}", "❌ Should have failed"))
            except Exception as e:
                self.test_results.append((f"HTTP service {host}", f"✅ Error: {type(e).__name__}: {e}"))
            finally:
                try:
                    await device.close()
                except:
                    pass
                    
    async def test_rapid_polling_stress(self):
        """Stress test with rapid polling to trigger various errors."""
        print(f"\n🚀 Stress Testing with rapid polling on {self.real_device_ip}")
        print("-" * 40)
        
        device = None
        try:
            # Use protocol from discovery if available
            protocol = getattr(self, 'real_device_protocol', 'http')
            serial = getattr(self, 'real_device_serial', '')
            device = MaxSmartDevice(self.real_device_ip, protocol=protocol, sn=serial)
            device.DEFAULT_TIMEOUT = 1.0  # Short timeout to force some failures
            await device.initialize_device()
            
            print("Starting rapid polling for 30 seconds...")
            start_time = time.time()
            success_count = 0
            error_count = 0
            
            while time.time() - start_time < 30:
                try:
                    data = await device.get_data()
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Rapid poll error: {type(e).__name__}: {e}")
                    
                await asyncio.sleep(0.1)  # Very rapid polling
                
            self.test_results.append((
                "Rapid polling stress", 
                f"✅ Completed: {success_count} success, {error_count} errors"
            ))
            
        except Exception as e:
            self.test_results.append(("Rapid polling setup", f"❌ Failed: {e}"))
        finally:
            if device:
                await device.close()
                
    def print_test_summary(self):
        """Print a summary of all test results."""
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        
        for test_name, result in self.test_results:
            print(f"{test_name:.<40} {result}")
            
        success_count = sum(1 for _, result in self.test_results if result.startswith("✅"))
        total_count = len(self.test_results)
        
        print("-" * 60)
        print(f"Total tests: {total_count}")
        print(f"Successful error handling: {success_count}")
        print(f"Unexpected results: {total_count - success_count}")
        
        if success_count == total_count:
            print("\n🎉 All error conditions properly handled!")
        else:
            print("\n⚠️  Some tests had unexpected results - check logs for details")
            
        print(f"\nDetailed logs saved to: maxsmart_error_test.log")
        print("Check the log file for full error messages and stack traces.")
        
        # Also test error message improvements
        self.test_error_message_quality()
        
    def test_error_message_quality(self):
        """Test that error messages contain useful information."""
        print("\n📝 Testing Error Message Quality")
        print("-" * 40)
        
        quality_checks = []
        
        for test_name, result in self.test_results:
            if result.startswith("✅ Error:"):
                error_msg = result[10:]  # Remove "✅ Error: "
                
                # Check for useful information in error messages
                has_ip = any(ip_part in error_msg for ip_part in [
                    "192.168.", "10.", "172.", "127.0.0.1", "169.254."
                ])
                has_timeout = "timeout" in error_msg.lower()
                has_attempt = "attempt" in error_msg.lower()
                has_detail = len(error_msg) > 50  # Reasonable detail length
                
                quality_score = sum([has_ip, has_timeout, has_attempt, has_detail])
                quality_checks.append((test_name, quality_score, error_msg))
                
        if quality_checks:
            avg_quality = sum(score for _, score, _ in quality_checks) / len(quality_checks)
            print(f"Average error message quality: {avg_quality:.1f}/4.0")
            
            print("\nError message samples:")
            for test_name, score, msg in quality_checks[:3]:  # Show first 3
                print(f"  {test_name}: {msg[:80]}...")
                print(f"    Quality: {score}/4 {'✅' if score >= 2 else '⚠️'}")
        else:
            print("No error messages to analyze")

async def main():
    """Main function to run error tests."""
    print("MaxSmart Error Testing Suite v2.0.3")
    print("====================================")
    print("This script tests error handling improvements in maxsmart 2.0.3+")
    print()
    
    device_ip = None
    
    if len(sys.argv) > 1:
        device_ip = sys.argv[1]
        print(f"✅ Using real device IP: {device_ip}")
        print("   Will test both network errors AND command errors")
    else:
        print("ℹ️  No device IP provided")
        print("   Will test network errors only")
        print("   Usage: python example_scripts/test_maxsmart_errors.py [device_ip]")
        print()
        
    print("Starting tests in 3 seconds...")
    await asyncio.sleep(3)
    
    tester = ErrorTester(device_ip)
    await tester.run_all_tests()
    
    print("\n" + "=" * 60)
    print("✅ Error testing completed!")
    print("📋 Check maxsmart_error_test.log for detailed error traces")
    print("🔧 Use these results to verify maxsmart 2.0.3 improvements")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        print("Partial results may be available in maxsmart_error_test.log")
    except Exception as e:
        print(f"\n\n❌ Test script failed: {e}")
        import traceback
        traceback.print_exc()
        print("\nThis error suggests a problem with the test script itself.")
        print("Please check that maxsmart 2.0.3+ is properly installed.")
    finally:
        print(f"\n👋 Error testing session ended at {time.strftime('%Y-%m-%d %H:%M:%S')}")