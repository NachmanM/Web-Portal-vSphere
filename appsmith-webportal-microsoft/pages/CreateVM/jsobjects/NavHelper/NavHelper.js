export default {
	handleVmClick: async (vmId) => {
		// 1. Store the ID globally in the app
		await storeValue('selectedVmId', vmId);
		// 2. Navigate to the page
		navigateTo('DetailsVM', { "vm_moid": vmId });
	}
}