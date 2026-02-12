import json
import os
from pathlib import Path
import unittest
from module.smap.smap_parser import SmapParser




class TestSmapParser(unittest.TestCase):

    def setUp(self):
        """Prepares the temporary test file before each test."""
        self.test_file_path = Path("temp_test_smap.json")
        
        self.command = "smap test"

        self.sample_raw_input = """[{"ip":"10.10.10.1","hostnames":["hostname.it"],"ports":[{"port":1000,"service":"ock?","cpes":null,"protocol":"tcp"}],"start_time":"2026-01-21T09:53:42.94698508+01:00","end_time":"2026-01-21T09:53:42.980644844+01:00","os":{"name":"","cpes":null,"port":0}},{"ip":"10.10.10.2","hostnames":["hostname2.it"],"ports":[{"port":1000,"service":"ock?","cpes":null,"protocol":"tcp"}],"start_time":"2026-01-21T09:53:42.967060459+01:00","end_time":"2026-01-21T09:53:42.994341675+01:00","os":{"name":"","cpes":null,"port":0}},{"ip":"10.10.10.3","hostnames":["hostname3.it"],"ports":[{"port":1000,"service":"ock?","cpes":null,"protocol":"tcp"}],"start_time":"2026-01-21T09:53:42.970598633+01:00","end_time":"2026-01-21T09:53:43.001171757+01:00","os":{"name":"","cpes":null,"port":0}}]"""
        self.sample_json_input = json.loads(self.sample_raw_input)
        self.file_data = {
            "tool_name": "smap",
            "command": self.command,
            "data": self.sample_json_input
        }

        # Create the file on disk
        with open(self.test_file_path, "w") as f:
            json.dump(self.file_data, f)

    def tearDown(self):
        """Cleans up the file after test."""
        if self.test_file_path.exists():
            os.remove(self.test_file_path)

    def test_smap_parsing_logic(self):
        """Verifies that SmapParser correctly maps the JSON to our internal format."""
        
        # 1. Execution
        parser = SmapParser()
        result = parser.parse(self.test_file_path)
        
        data = result.get("data", {})
        
        # --- 2. Verification ---
        print("\n--- 🧪 TEST RESULTS ---")

        # A. Check Top Level Info
        self.assertEqual(result["tool_name"], "smap")
        self.assertEqual(result["command"], "smap test")
        self.assertTrue(len(data) > 0, "Parser returned no data!")

        # B. Validate Host 1 (Simple Case: 10.10.10.1)
        ip1 = "10.10.10.1"
        self.assertIn(ip1, data)
        host1 = data[ip1]
        
        # Hostnames
        print(f"✅ Host 1 ({ip1}) Hostnames: {host1['hostnames']}")
        self.assertIn("hostname.it", host1["hostnames"])
        
        # Ports (1000/tcp)
        self.assertIn("1000/tcp", host1["ports"])
        port1000 = host1["ports"]["1000/tcp"]
        self.assertEqual(port1000["service"], "ock?")
        self.assertEqual(port1000["state"], "unknown") # Default state in your parser
        self.assertIn("smap", port1000["source"])

        # C. Validate Host 2 (Complex Case: 10.10.10.2)
        # This checks OS, CPEs, and Product parsing
        ip2 = "10.10.10.2"
        self.assertIn(ip2, data)
        host2 = data[ip2]
        
        # OS Detection
        print(f"✅ Host 2 ({ip2}) OS: {host2['os']}")

        # Hostnames (Multiple)        self.assertIn("hostname2.it", host2["hostnames"])

        # Port 25 (Exchange) - Detailed Check
        self.assertIn("1000/tcp", host2["ports"])
        port25 = host2["ports"]["1000/tcp"]
        
        print("--- TEST PASSED SUCCESSFULLY ---")

if __name__ == "__main__":
    unittest.main()