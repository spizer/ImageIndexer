"""
GPU detection logic for determining available hardware and recommended backend.
Adapted from koboldcpp.py by Concedo.
"""
import subprocess
import platform


class GpuDetector:
    """Class for detecting GPU capabilities and appropriate backend"""
    
    def __init__(self):
        self.summary = {
            "cuda_available": False,
            "cuda_version": None,
            "nvidia_devices": [],
            "amd_available": False,
            "amd_devices": [],
            "vulkan_available": False,
            "vulkan_devices": [],
            "opencl_available": False,
            "total_vram_mb": 0,
            "recommended_backend": "CPU"
        }
    
    def detect_nvidia_gpu(self):
        """Detect NVIDIA GPU and CUDA capabilities"""
        try:
            # Check for CUDA version
            output = subprocess.run(
                ['nvidia-smi', '-q', '-d=compute'],
                capture_output=True, text=True, check=True, encoding='utf-8'
            ).stdout

            for line in output.splitlines():
                if line.strip().startswith('CUDA'):
                    self.summary["cuda_version"] = line.split()[3]
                    self.summary["cuda_available"] = True

            # Get detailed GPU information for all cards
            output = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,memory.total', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, check=True, encoding='utf-8'
            ).stdout

            nvidia_devices = []
            total_vram = 0

            for line in output.strip().splitlines():
                parts = line.split(',')
                if len(parts) >= 3:
                    index = int(parts[0].strip())
                    name = parts[1].strip()
                    vram_mb = int(parts[2].strip())

                    nvidia_devices.append({
                        "index": index,
                        "name": name,
                        "vram_mb": vram_mb
                    })
                    total_vram += vram_mb

            self.summary["nvidia_devices"] = nvidia_devices
            self.summary["total_vram_mb"] = total_vram

            return len(nvidia_devices) > 0
        except Exception as e:
            print(f"No NVIDIA GPU detected: {e}")
            return False
    
    def detect_vulkan(self):
        """Detect Vulkan-compatible GPUs and their VRAM"""
        try:
            output = subprocess.run(
                ['vulkaninfo', '--summary'], 
                capture_output=True, text=True, check=True, encoding='utf-8'
            ).stdout
            
            if "deviceName" in output:
                self.summary["vulkan_available"] = True
                
                # Parse device names
                vulkan_devices = []
                device_names = []
                device_types = []
                
                for line in output.splitlines():
                    if "deviceName" in line:
                        name = line.split("=")[1].strip()
                        device_names.append(name)
                    if "deviceType" in line:
                        device_type = line.split("=")[1].strip()
                        is_discrete = "DISCRETE" in device_type
                        device_types.append(is_discrete)
                
                vram_sizes = []
                for line in output.splitlines():
                    if "VkPhysicalDeviceMemoryProperties" in line or "heapSize" in line:
                        # Look for memory heap sizes, typically in bytes
                        if "heapSize" in line and "0x" in line:  # Hex value
                            try:
                                # Extract hex value and convert to bytes
                                hex_value = line.split("0x")[1].split()[0]
                                bytes_value = int(hex_value, 16)
                                mb_value = bytes_value / (1024 * 1024)
                                vram_sizes.append(int(mb_value))
                            except Exception:
                                pass
                
                for i in range(len(device_names)):
                    device = {
                        "name": device_names[i],
                        "is_discrete": device_types[i] if i < len(device_types) else False
                    }
                    
                    if i < len(vram_sizes):
                        device["vram_mb"] = vram_sizes[i]
                        # Update total VRAM if this is larger
                        if vram_sizes[i] > self.summary["total_vram_mb"]:
                            self.summary["total_vram_mb"] = vram_sizes[i]
                    
                    vulkan_devices.append(device)
                
                self.summary["vulkan_devices"] = vulkan_devices
                return True
            return False
        except Exception as e:
            print(f"No Vulkan support detected: {e}")
            return False
    
    def detect_amd_gpu(self):
        """Detect AMD GPUs and their VRAM using ROCm tools"""
        try:
            # Try rocminfo first
            output = subprocess.run(
                ['rocminfo'],
                capture_output=True, text=True, check=True, encoding='utf-8'
            ).stdout

            amd_devices = []
            current_device = None
            device_index = 0

            for line in output.splitlines():
                line = line.strip()
                if "Marketing Name:" in line:
                    name = line.split(":", 1)[1].strip()
                    current_device = {"name": name, "index": device_index}
                elif "Device Type:" in line and "GPU" in line and current_device:
                    # Current device is a GPU, keep it
                    amd_devices.append(current_device)
                    current_device = None
                    device_index += 1
                elif "Device Type:" in line and "GPU" not in line:
                    # Not a GPU, discard
                    current_device = None

            # If we found AMD GPUs, try to get their VRAM
            total_vram = 0
            if amd_devices:
                try:
                    vram_info = subprocess.run(
                        ['rocm-smi', '--showmeminfo', 'vram', '--csv'],
                        capture_output=True, text=True, check=True, encoding='utf-8'
                    ).stdout

                    # Parse CSV output for VRAM values
                    lines = vram_info.splitlines()
                    if len(lines) > 1:  # Skip header
                        for i, line in enumerate(lines[1:]):
                            if i < len(amd_devices) and "," in line:
                                try:
                                    vram_mb = int(line.split(",")[1].strip())
                                    amd_devices[i]["vram_mb"] = vram_mb
                                    total_vram += vram_mb
                                except Exception:
                                    pass
                except Exception as e:
                    print(f"Error getting AMD VRAM: {e}")
                    # Try alternative method using rocm-smi without CSV
                    try:
                        for i in range(len(amd_devices)):
                            vram_info = subprocess.run(
                                ['rocm-smi', '--device', str(i), '--showmeminfo', 'vram'],
                                capture_output=True, text=True, check=True, encoding='utf-8'
                            ).stdout
                            # Parse for VRAM Total
                            for line in vram_info.splitlines():
                                if "VRAM Total Memory" in line or "Total Memory" in line:
                                    # Extract number from line
                                    parts = line.split()
                                    for j, part in enumerate(parts):
                                        if part.replace('.', '').isdigit() and j + 1 < len(parts):
                                            vram_val = float(part)
                                            unit = parts[j + 1].lower()
                                            if 'gb' in unit or 'gib' in unit:
                                                vram_mb = int(vram_val * 1024)
                                            else:
                                                vram_mb = int(vram_val)
                                            amd_devices[i]["vram_mb"] = vram_mb
                                            total_vram += vram_mb
                                            break
                    except Exception as e2:
                        print(f"Error with alternative AMD VRAM detection: {e2}")

            if amd_devices:
                self.summary["amd_available"] = True
                self.summary["amd_devices"] = amd_devices
                if total_vram > 0:
                    self.summary["total_vram_mb"] = max(self.summary["total_vram_mb"], total_vram)
                return True
            return False
        except Exception as e:
            print(f"No AMD GPU detected: {e}")
            return False

    def detect_all(self):
        """Detect all GPU capabilities and determine recommended backend"""

        # Try detecting in order of preference
        nvidia_detected = self.detect_nvidia_gpu()
        amd_detected = self.detect_amd_gpu()
        vulkan_detected = self.detect_vulkan()

        if nvidia_detected and self.summary["total_vram_mb"] >= 3500:
            self.summary["recommended_backend"] = "CUDA"
        elif amd_detected and self.summary["total_vram_mb"] >= 3500:
            self.summary["recommended_backend"] = "Vulkan"
        elif vulkan_detected and self.summary["total_vram_mb"] >= 3500:
            self.summary["recommended_backend"] = "Vulkan"
        else:
            self.summary["recommended_backend"] = "CPU"

        return self.summary

