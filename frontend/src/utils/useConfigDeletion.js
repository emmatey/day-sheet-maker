import React from 'react';


function buildUpdateString(segments, value, action = "update") {
  const path = "[" + segments.map(String).join("][") + "]";
  return `${path}^${JSON.stringify(value)}^${action}`;
}

/**
 * Custom hook to handle deletion of a configuration key via the backend.
 * It encapsulates the complex, state-updating, and asynchronous deletion process.
 * * @param {function} setLoading - State setter for the loading status (e.g., from useState).
 * @param {function} setSettings - State setter for the main settings object (e.g., from useState).
 * @returns {{handleDeleteConfigKey: function}} An object containing the deletion function.
 */
export default function useConfigDeletion(setLoading, setSettings) {

  const handleDeleteConfigKey = React.useCallback(async (pathSegments, keyToDelete, confirmMessage) => {
    
    // 1. User Confirmation (only prompt if a message is provided)
    if (confirmMessage) {

        // We expect the nativeAlert to return 0 for "Yes" and 1 for "No".
        const response = await window.electronAPI.nativeAlert({ 
            type: "warning", 
            message: confirmMessage,
            buttons: ["Yes", "No"],
            defaultId: 1, 
            cancelId: 1  
        });

        // Check if the user clicked the 'No' button (which is at index 1)
        if (response === 1) {
            return false; // Stop the deletion process
        }
    }
    
    // Safety check
    if (!keyToDelete) return false;

    // 2. Build the update string using the "delete" action
    // Example: ["ROLE_MAP", "Deli"] -> ["ROLE_MAP"][Deli]^null^delete
    const update = buildUpdateString(pathSegments, null, "delete");

    try {
      setLoading(true);
      
      // 3. Apply config change via Electron IPC
      await window.electronAPI.applyConfig(update);
      
      // 4. Fetch fresh settings to update the main state object
      const fresh = await window.electronAPI.readSettings();
      setSettings(fresh);
      
      setLoading(false);
      return true; // Deletion successful
    } catch (e) {
        console.error("applyConfig (Config Deletion) failed:", e);
        setLoading(false);
        return false; // Deletion failed
    }
  }, [setLoading, setSettings]); // Dependencies for useCallback

  return { handleDeleteConfigKey };
}