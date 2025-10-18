console.log("🔧 Script loaded successfully");

document.getElementById("simForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    console.log("✅ Form submitted");

    const formData = Object.fromEntries(new FormData(event.target).entries());
    const resultDiv = document.getElementById("result");
    
    console.log("📊 Form data:", formData);
    resultDiv.innerHTML = '<div class="loading">🔄 Running simulation...</div>';

    try {
        console.log("🌐 Sending request to /simulate...");
        
        const response = await fetch("/simulate", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(formData),
        });

        console.log("📨 Response status:", response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("📦 Received data:", data);
        
        if (data.error) {
            resultDiv.innerHTML = `<div class="error">❌ Error: ${data.error}</div>`;
            return;
        }

        const results = data.results;
        if (!Array.isArray(results) || results.length === 0) {
            resultDiv.innerHTML = "<div class='error'>⚠️ No simulation results returned.</div>";
            return;
        }

        displayResults(results, formData, resultDiv);

    } catch (error) {
        console.error("❌ Simulation error:", error);
        resultDiv.innerHTML = `<div class="error">❌ Error: ${error.message}. Check browser console for details.</div>`;
    }
});

function displayResults(results, formData, resultDiv) {
    let html = `<h2>📊 Simulation Results (Discrete-Event Simulation)</h2>`;
    html += `<p><strong>Parameters:</strong> M=${formData.M}, N=${formData.N}, ` +
            `Repair: N(${formData.mean_repair}, ${formData.std_repair}), ` +
            `Breakdown: N(${formData.mean_break}, ${formData.std_break})</p>`;

    results.forEach((r) => {
        const workingAtHalt = r.working_at_halt || r.final_working_machines;
        
        // Debug: check what properties the events actually have
        if (r.events && r.events.length > 0) {
            console.log("🔍 First event structure:", r.events[0]);
        }

        html += `
            <div class="simulation-block">
                <h3>🏭 Simulation #${r.simulation}</h3>

                <div class="result-grid">
                    <div class="result-item">
                        <strong>Time Until Factory Halt:</strong> ${r.time_until_halt ? r.time_until_halt + ' time units' : 'Did not halt'}
                    </div>
                    <div class="result-item">
                        <strong>Working Machines at Halt:</strong> ${workingAtHalt}
                    </div>
                    <div class="result-item">
                        <strong>Broken Machines at Halt:</strong> ${r.final_broken_machines}
                    </div>
                    <div class="result-item">
                        <strong>Utilization at Halt:</strong> ${(r.utilization_at_halt * 100).toFixed(2)}%
                    </div>
                    <div class="result-item">
                        <strong>Total Events Processed:</strong> ${r.total_events}
                    </div>
                </div>

                <div class="explanation">
                    <p><strong>Explanation:</strong> ${getExplanation(r, formData.N, workingAtHalt)}</p>

                    ${r.events && r.events.length > 0 ? `
                    <details>
                        <summary>Show First ${Math.min(10, r.events.length)} Events</summary>
                        <div class="events-log">
                            ${r.events.map(event => {
                                // Flexible property access - try multiple possible property names
                                const working = event.working || event.working_after || event.working_before || 'N/A';
                                const broken = event.broken || event.broken_after || event.broken_before || 'N/A';
                                const machineId = event.machine_id !== undefined ? event.machine_id : 'N/A';

                                return `
                                <div class="event-item">
                                    Time ${event.time}: ${event.type === 'FACTORY_HALT' ? '🏭 FACTORY HALTED' : `Machine ${machineId} ${event.type}`}
                                    → Working: ${working}, Broken: ${broken}
                                </div>
                                `;
                            }).join('')}
                        </div>
                    </details>
                    ` : ''}
                </div>
                <hr>
            </div>
        `;
    });

    // Add summary statistics
    const haltTimes = results.filter(r => r.time_until_halt).map(r => r.time_until_halt);
    if (haltTimes.length > 0) {
        const avgHaltTime = (haltTimes.reduce((a, b) => a + b, 0) / haltTimes.length).toFixed(2);
        const minHaltTime = Math.min(...haltTimes).toFixed(2);
        const maxHaltTime = Math.max(...haltTimes).toFixed(2);
        
        // Count different halt states
        const haltStates = {};
        results.forEach(r => {
            if (r.time_until_halt) {
                const state = r.working_at_halt || r.final_working_machines;
                haltStates[state] = (haltStates[state] || 0) + 1;
            }
        });
        
        const haltStateText = Object.entries(haltStates)
            .map(([state, count]) => `${count}×${state} working`)
            .join(', ');
        
        html += `
            <div class="summary">
                <h3>📈 Summary Statistics</h3>
                <p>Average Time Until Halt: <strong>${avgHaltTime}</strong> time units</p>
                <p>Range: ${minHaltTime} - ${maxHaltTime} time units</p>
                <p>Halt States: ${haltStateText}</p>
                <p>Simulations that halted: ${haltTimes.length}/${results.length}</p>
            </div>
        `;
    }

    resultDiv.innerHTML = html;
}

function getExplanation(result, N, workingAtHalt) {
    if (result.time_until_halt) {
        return `The factory halted at <strong>${result.time_until_halt}</strong> time units with <strong>${workingAtHalt}</strong> working machines (below N=${N}). Processed <strong>${result.total_events}</strong> events.`;
    } else {
        return `The simulation completed without the factory halting. There were <strong>${result.final_working_machines}</strong> working machines at the end.`;
    }
}

// Test if the server is reachable
console.log("🧪 Testing server connection...");
fetch("/health")
    .then(response => response.json())
    .then(data => console.log("✅ Server health check:", data))
    .catch(error => console.error("❌ Server health check failed:", error));