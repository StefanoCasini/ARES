import pytest
from module.dtos.HostDTO import HostDTO
from module.dtos.PortDTO import PortDTO

def test_host_dto_initialization():
    """Test that default factories create the correct empty types."""
    host = HostDTO(ip="192.168.1.100")
    
    assert host.ip == "192.168.1.100"
    assert isinstance(host.ports, dict)
    assert isinstance(host.hostnames, dict)
    assert isinstance(host.os, dict)
    assert isinstance(host.discovery_commands, set)

def test_host_dto_to_dict_conversion():
    """Test that sets are correctly converted to lists for JSON serialization."""
    host = HostDTO(ip="10.0.0.1")
    
    # 1. Add some mock data using our new Set logic
    host.discovery_commands.add("nmap -sV 10.0.0.1")
    
    host.hostnames["example.local"] = set()
    host.hostnames["example.local"].add("nmap -sV 10.0.0.1")
    
    # Add a dummy port to ensure cascading works
    dummy_port = PortDTO(port="80", state="open", banner="", service="http", source="nmap", ttl="", reason="")
    host.ports["80/tcp"] = [dummy_port]

    # 2. Call the method that kept crashing earlier
    result = host.to_dict()

    # 3. Assert the output is perfectly formatted for JSON
    assert result["ip"] == "10.0.0.1"
    assert result["discovery_commands"] == ["nmap -sV 10.0.0.1"]
    
    # The inner set should now be a list!
    assert result["hostnames"] == {"example.local": ["nmap -sV 10.0.0.1"]}
    
    # The port should be converted to a dict
    assert isinstance(result["ports"]["80/tcp"][0], dict)
    assert result["ports"]["80/tcp"][0]["port"] == "80"