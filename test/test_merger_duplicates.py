import json
import os
from pathlib import Path
import unittest
from module.merger import _prune_weak_siblings
from module.smap.smap_parser import SmapParser


class TestPruneLogic(unittest.TestCase):

    def test_prune_identical_weak_entry(self):
        """Scenario: Masscan found a weak port, and finds it again. Old one should go."""
        print("\n🧪 Test 1: Deduplicate Identical Weak Entries")
        
        # ARRANGE
        existing = [
            {"source": "masscan", "service": "unknown", "banner": None, "ttl": 50},
            {"source": "nmap", "service": "http", "banner": "Apache"}
        ]
        new_data = {
            "source": "masscan", 
            "service": "http", 
            "banner": "HTTP/1.1 200 OK\r\nServer: example\r\nDate: Thu, 22 Jan 2026 09:53:59 GMT\r\nContent-Type: text/html\r\nContent-Length: 1033\r\nLast-Modified: Sun, 21 Jan 2024 11:17:52 GMT\r\nConnection: close\r\nETag: \"ex123-231\"\r\nAccept-Ranges: bytes\r\n\r", 
            "ttl": 55
            }
        
        # ACT
        _prune_weak_siblings(existing, new_data)
        
        # ASSERT
        print(f"   Result List: {existing}")
        # We expect the 'masscan' entry to be gone (size 1)
        self.assertEqual(len(existing), 1)
        self.assertEqual(existing[0]["source"], "nmap")

    def test_keep_strong_entry(self):
        """Scenario: We have a Strong Masscan entry. New Weak Masscan arrives. Keep Strong."""
        print("\n🧪 Test 2: Protect Strong Entries")
        
        # ARRANGE
        existing = [
            {"source": "masscan", "service": "http", "banner": "nginx"} # STRONG
        ]
        new_data = {"source": "masscan", "service": "unknown", "banner": None} # WEAK
        
        # ACT
        _prune_weak_siblings(existing, new_data)
        
        # ASSERT
        print(f"   Result List: {existing}")
        # Should NOT remove the strong entry
        self.assertEqual(len(existing), 1)
        self.assertEqual(existing[0]["service"], "http")

    def test_ignore_different_source(self):
        """Scenario: Nmap has a weak entry. Masscan brings a weak entry. Don't touch Nmap."""
        print("\n🧪 Test 3: Respect Different Sources")
        
        # ARRANGE
        existing = [
            {"source": "nmap", "service": "unknown", "banner": None}
        ]
        new_data = {"source": "masscan", "service": "unknown", "banner": None}
        
        # ACT
        _prune_weak_siblings(existing, new_data)
        
        # ASSERT
        print(f"   Result List: {existing}")
        # Nmap entry should stay
        self.assertEqual(len(existing), 1)
        self.assertEqual(existing[0]["source"], "nmap")

if __name__ == "__main__":
    unittest.main()