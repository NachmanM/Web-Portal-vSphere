export default {
	tree_vcenter_navonOptionChange () {
		//	write code here
 {
    const selected = tree_vcenter_nav.selectedOptionValue;
    
    if (selected.startsWith("FOLDER::")) {
        const folderName = selected.replace("FOLDER::", "");
        storeValue('selectedFolder', folderName);
        removeValue('selectedVM_ID');
    } else {
        // User clicked a VM. Navigate to the new page and pass the ID in the URL.
        navigateTo('DetailsVM', { vm_moid: selected });
 
    }
  }
	}
}