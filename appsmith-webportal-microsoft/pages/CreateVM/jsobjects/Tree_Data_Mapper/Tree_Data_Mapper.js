export default {
    buildTree: () => {
        // 1. Retrieve the folder list from your API
        const folders = list_folders.data?.folders || [];
        
        // 2. Retrieve the full list of VMs from your PostgreSQL query
        const vms = Get_All_VMs.data || [];

        // 3. Map the data into the structure required by the TreeSelect widget
        const treeData = folders.map(folder => {
            
            // Filter the VMs that belong to the current folder
            const folderVMs = vms.filter(vm => vm.name === folder.name);

            // Construct the 'children' array containing the VMs
            const children = folderVMs.map(vm => {
                return {
                    label: vm.vm_name,     // The VM name displayed in the UI
                    value: vm.vcenter_uuid   // The unique ID used when a VM is clicked
                };
            });

            // Return the parent folder object
            return {
                label: folder.name,
                value: folder.code || folder.name, // The unique folder identifier
                children: children
            };
        });

        return treeData;
    }
}