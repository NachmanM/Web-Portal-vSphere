export default {
    handleVmClick: async (vmId) => {
        // 1. Store the ID so all widgets on this page can see it
        await storeValue('selectedVmId', vmId);
        
        // 2. Update URL parameters without a full page reload
        await navigateTo('DetailsVM', { "vm_moid": vmId });

        // 3. MANUALLY trigger your VM data query to refresh
        // Replace 'get_vm_details' with the name of your specific query on this page
        await VM_Details.run(); 
    }
}