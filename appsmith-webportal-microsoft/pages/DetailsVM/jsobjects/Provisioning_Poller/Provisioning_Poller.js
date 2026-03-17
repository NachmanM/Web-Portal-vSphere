export default {
    start: () => {
        const moid = appsmith.URL.queryParams.vm_moid;
        
        if (moid && moid.startsWith('pending-')) {
            clearInterval("vm_poll_timer");
            
            // Explicitly define the callback as an 'async' function
            setInterval(async () => {
                try {
                    // 1. TEMPORARY HEARTBEAT: This proves the timer is running.
                    // (Delete this line once you confirm it works so it doesn't spam your screen)
                    showAlert('Checking VM Status...', 'info'); 
                    
                    // 2. Await the database query directly
                    const data = await Check_VM_Status.run();
                    
                   
									const realMoid = data[0].vcenter_uuid;
									const status = data[0].status;

									// 3. Evaluate completion
									if (status === 'active' && realMoid && !realMoid.startsWith('pending-')) {

										clearInterval("vm_poll_timer");
										showAlert('Provisioning complete! Loading live vCenter details...', 'success');

										// Route user to the final URL
										navigateTo('DetailsVM', { "vm_moid": realMoid }, 'SAME_WINDOW');

										// Refresh all UI components
										await get_vm_cached.run(); 
										await Get_Metadata_Provisioning.run(); 
										await VM_Details.run(); 
									}
                    
                } catch (error) {
                    console.error("Poller execution error:", error);
                }
            }, 5000, "vm_poll_timer"); 
            
        } else {
            clearInterval("vm_poll_timer");
        }
    },
    
    stop: () => {
        clearInterval("vm_poll_timer");
    }
}