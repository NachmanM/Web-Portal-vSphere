export default {
	ShowModal: async () => {
		try {

			showModal('VM_Details_popup');

		} catch (error) {
			// Handle any errors that occur at any stage in the chain
			showAlert("An error occurred during execution.", "error");
			console.error(error);
		}
	}
}