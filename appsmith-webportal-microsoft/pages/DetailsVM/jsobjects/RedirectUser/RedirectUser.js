export default {
    tree_vcenter_navonOptionChange: () => {
        const selected = tree_vcenter_nav.selectedOptionValue;
        
        if (!selected) return;

        if (selected.startsWith("FOLDER::")) {
            const folderName = selected.replace("FOLDER::", "");
            storeValue('selectedFolder', folderName);
            removeValue('selectedVM_ID');
        } else {
            // 1. Update the URL for bookmarking/sharing (does not reload the page)
            navigateTo('DetailsVM', { "vm_moid": selected }, 'SAME_WINDOW');

            // 2. Execute the conditional routing logic immediately
            if (selected.startsWith('pending-')) {
                // Optimistic UI state
                Get_Metadata_Provisioning.run();
                VM_Details.clear(); 
            } else {
                // Active VM state
                Get_Metadata_Provisioning.run();
                VM_Details.run();
            }
        }
    }
}