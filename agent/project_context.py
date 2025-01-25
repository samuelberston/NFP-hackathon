import os
import json
import hcl2
from typing import Dict, List, Optional

class TerraformProjectContext:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.tf_files: Dict[str, dict] = {}
        self.providers: List[str] = []
        self.resources: Dict[str, List[str]] = {}
        self.network_topology: Dict[str, dict] = {}
        
    def analyze_project(self) -> None:
        """Analyze the Terraform project directory and extract relevant information."""
        # Scan for .tf files
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.tf'):
                    file_path = os.path.join(root, file)
                    self._parse_tf_file(file_path)
                elif file == '.terraform.lock.hcl':
                    self._parse_lockfile(os.path.join(root, file))

    def _parse_tf_file(self, file_path: str) -> None:
        """Parse a Terraform file and extract resources and network topology."""
        try:
            with open(file_path, 'r') as f:
                content = hcl2.load(f)
                self.tf_files[file_path] = content
                
                print(f"\nDEBUG: Parsing file: {file_path}")
                print(f"DEBUG: Raw content type: {type(content)}")
                print(f"DEBUG: Raw content: {content}")
                
                # Handle provider blocks
                if 'provider' in content:
                    provider_blocks = content['provider']
                    for provider in provider_blocks:
                        for provider_name in provider:
                            if provider_name not in self.providers:
                                self.providers.append(provider_name)
                
                # Handle resource blocks
                if 'resource' in content:
                    resource_blocks = content['resource']
                    for resource in resource_blocks:
                        for resource_type, instances in resource.items():
                            if resource_type not in self.resources:
                                self.resources[resource_type] = []
                            
                            for instance_name in instances:
                                self.resources[resource_type].append(instance_name)
                                # If this is a network component, add it to topology
                                self._analyze_network_components(resource_type, instance_name, instances[instance_name])
                            
        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")
            import traceback
            traceback.print_exc()

    def _parse_lockfile(self, file_path: str) -> None:
        """Parse the .terraform.lock.hcl file to extract provider information."""
        try:
            with open(file_path, 'r') as f:
                content = hcl2.load(f)
                for block in content:
                    if isinstance(block, dict) and 'provider' in block:
                        provider_data = block['provider']
                        if isinstance(provider_data, dict):
                            for provider_name in provider_data.keys():
                                if provider_name not in self.providers:
                                    self.providers.append(provider_name)
        except Exception as e:
            print(f"Error parsing lockfile: {str(e)}")

    def _analyze_network_components(self, resource_type: str, resource_name: str, resource_config: dict) -> None:
        """Analyze and extract network topology from Terraform content."""
        print(f"\nDEBUG: Analyzing network component: {resource_type}.{resource_name}")
        
        network_resources = {
            'google_compute_network': 'vpc',
            'google_compute_subnetwork': 'subnet',
            'google_compute_firewall': 'firewall',
            'google_compute_router': 'router',
            'google_compute_router_nat': 'nat',
            'google_compute_instance': 'instance',
            'google_storage_bucket': 'storage',
            'google_kms_key_ring': 'kms',
            'google_kms_crypto_key': 'kms_key'
        }

        if resource_type in network_resources:
            print(f"DEBUG: Found network resource type: {resource_type}")
            component_type = network_resources[resource_type]
            if component_type not in self.network_topology:
                self.network_topology[component_type] = {}
            
            print(f"DEBUG: Adding to topology: {component_type}.{resource_name}")
            self.network_topology[component_type][resource_name] = resource_config

    def get_project_summary(self) -> dict:
        """Return a summary of the project analysis."""
        return {
            'providers': self.providers,
            'resource_types': list(self.resources.keys()),
            'resource_count': {k: len(v) for k, v in self.resources.items()},
            'network_components': {k: list(v.keys()) for k, v in self.network_topology.items()},
            'files_analyzed': list(self.tf_files.keys())
        }

    def export_context(self, output_file: str) -> None:
        """Export the project context to a JSON file."""
        context = {
            'project_path': self.project_path,
            'providers': self.providers,
            'resources': self.resources,
            'network_topology': self.network_topology,
            'summary': self.get_project_summary()
        }
        
        with open(output_file, 'w') as f:
            json.dump(context, f, indent=2)

if __name__ == "__main__":
    # Add debug print for raw content
    context = TerraformProjectContext("../gcp/")
    
    # Debug print for a specific file
    with open("../gcp/network.tf", 'r') as f:
        content = hcl2.load(f)
        print("\nRaw content from network.tf:")
        print(content)
    
    context.analyze_project()
    summary = context.get_project_summary()
    print("\nProject Summary:")
    print("---------------")
    print(f"Providers: {summary['providers']}")
    print(f"\nResource Types: {summary['resource_types']}")
    print(f"\nResource Counts: {summary['resource_count']}")
    print(f"\nNetwork Components: {summary['network_components']}")
    print(f"\nFiles Analyzed: {summary['files_analyzed']}")
    
    # Debug output
    print("\nDetailed Resources:")
    for resource_type, resources in context.resources.items():
        print(f"\n{resource_type}:")
        for resource in resources:
            print(f"  - {resource}")
            
    print("\nNetwork Topology:")
    for component_type, components in context.network_topology.items():
        print(f"\n{component_type}:")
        for name in components:
            print(f"  - {name}")