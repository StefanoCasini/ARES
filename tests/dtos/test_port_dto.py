import pytest
from module.dtos.PortDTO import PortDTO

def test_port_dto_initialization_defaults():
    """Test that creating a PortDTO without optional fields uses the defaults."""
    port = PortDTO(
        port="80",
        state="open",
        banner="Apache/2.4.41",
        service="http",
        source="nmap",
        ttl="64",
        reason="syn-ack"
    )

    # Required fields should match
    assert port.port == "80"
    assert port.state == "open"
    assert port.service == "http"
    
    # Optional fields should be "unknown"
    assert port.port_type == "unknown"
    assert port.command == "unknown"

def test_port_dto_initialization_overrides():
    """Test that providing optional fields correctly overrides the defaults."""
    port = PortDTO(
        port="443",
        state="closed",
        banner="",
        service="https",
        source="masscan",
        ttl="128",
        reason="rst",
        port_type="tcp",
        command="masscan -p443 192.168.1.100"
    )

    # Our custom values should be saved
    assert port.port_type == "tcp"
    assert port.command == "masscan -p443 192.168.1.100"

def test_port_dto_to_dict():
    """Test that PortDTO serializes into a pure dictionary safely."""
    port = PortDTO(
        port="22",
        state="open",
        banner="SSH-2.0-OpenSSH",
        service="ssh",
        source="nmap",
        ttl="64",
        reason="syn-ack",
        port_type="tcp",
        command="nmap -p22 10.0.0.1"
    )

    result = port.to_dict()

    # It must be a dictionary
    assert isinstance(result, dict)
    
    # The dictionary keys must perfectly match what our final JSON expects
    assert result["port"] == "22"
    assert result["state"] == "open"
    assert result["port_type"] == "tcp"
    assert result["command"] == "nmap -p22 10.0.0.1"