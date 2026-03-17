export default {
	runMyApisSequentially: async () => {
		const vmName = input_vm_name.text;
		let tempMoid = null;

		try {
			const insertResult = await Insert_Pending_VM.run();
			tempMoid = insertResult[0].vm_moid; 
			storeValue('new_vm_moid', tempMoid);

			const rawUuid = tempMoid.replace('pending-', '');
			await get_vm_cached.run();
			showModal('modal_vm_creation');

			// Because FastAPI now returns 200, this will NOT jump to the catch block automatically on a Terraform failure.
			const apiResponse = await create_vm.run({ transaction_uuid: rawUuid });

			// CRITICAL FIX: Manually check if the 200 OK response contains your custom error payload.
			if (apiResponse && apiResponse.error && apiResponse.error.detail) {
				// Manually throw the Terraform error string to jump to the catch block!
				throw new Error(apiResponse.error.detail);
			}

			closeModal('modal_vm_creation');
			showAlert(`Provisioning complete for VM: ${vmName}.`, "success");

			if (apiResponse?.real_moid) {
				navigateTo('DetailsVM', { "vm_moid": apiResponse.real_moid }, 'SAME_WINDOW');
			}

		} catch (error) {
			// Rollback Procedure
			if (tempMoid) {
				await Delete_Pending_VM.run({ moid: tempMoid });
				await get_vm_cached.run(); 
			}

			closeModal('modal_vm_creation');

			// 'error.message' now contains the exact Terraform string we threw in the try block!
			const backendErrorDetail = error.message || String(error);

			showAlert(`Execution failure for ${vmName}. System state rolled back. Detail: ${backendErrorDetail}`, "error");
			console.error("VM Provisioning True Error:", backendErrorDetail);
		}
	}
}