export default {
    // This function takes the selected template name as input
    isWindowsTemplate: (templateName) => {
        // 1. Guard clause: if no name is provided, default to false
        if (!templateName) return "false";

        // 2. Normalize to lowercase and check for "win"
        const containsWin = templateName.toLowerCase().includes("win");

        // 3. Return a literal string for Terraform/FastAPI compatibility
        return containsWin ? "true" : "false";
    }
}