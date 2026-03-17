export default {
    checkAndRoute: () => {
        // 1. Extract the MOID from the URL
        const moid = appsmith.URL.queryParams.vm_moid;

        // 2. Safety catch: Do nothing if the URL is empty
        if (!moid) {
            console.log("No VM selected. Routing aborted.");
            return;
        }

        // 3. Conditional Execution
        if (moid.startsWith("pending-")) {
            console.log("Pending VM detected. Executing Page_Controller...");
            // Trigger your controller to handle the Optimistic UI and polling
            Page_Controller.onPageLoad();
            
        } else {
            console.log("Active VM detected. Executing vCenter queries...");
            // It is a real VM. Safely execute the vCenter API.
            VM_Details.run();
            
            // You should also run your PostgreSQL metadata query here 
            // so the rest of your UI (Owner, Folder, etc.) populates.
            Get_Metadata_Provisioning.run();
        }
    }
}