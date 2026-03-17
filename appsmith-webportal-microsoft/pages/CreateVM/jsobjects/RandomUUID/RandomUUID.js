export default {
    generateDeployId: () => {
        // Generates a standard RFC4122 UUID
        return crypto.randomUUID(); 
    }
}