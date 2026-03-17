export default {
    onPageLoad: () => {
        // 1. Announce execution to the browser console
        console.log("Page_Controller initialized. Checking URL parameters...");
        
        const moid = appsmith.URL.queryParams.vm_moid;
        
        if (!moid) {
            // 2. Expose the Race Condition
            console.error("Execution halted: vm_moid is undefined at page load.");
            showAlert("Warning: URL parameters not ready on load.", "warning");
            return; 
        }

        console.log(`MOID detected: ${moid}`);

        if (moid.startsWith('pending-')) {
            console.log("State: Provisioning. Executing poller...");
            Get_Metadata_Provisioning.run();
            VM_Details.clear(); 
            Provisioning_Poller.start();
        } else {
            console.log("State: Active. Executing live queries...");
            Get_Metadata_Provisioning.run();
            VM_Details.run();
            Provisioning_Poller.stop();
        }
    }
}