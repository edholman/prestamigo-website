// Load latest rates from rates.json
async function loadRates() {
    try {
        const response = await fetch('./rates.json?t=' + Date.now()); // Cache bust
        const rates = await response.json();
        return {
            ...rates,
            lastUpdated: new Date(rates.last_updated).toLocaleDateString('es-ES')
        };
    } catch (error) {
        console.error("Using fallback rates:", error);
        return {
            CONV: 6.75,
            FHA: 7.25,
            ITIN: 8.0,
            lastUpdated: "20/06/2024"
        };
    }
}

// Main calculation function
async function calculate() {
    const rates = await loadRates();
    const loanType = document.getElementById("loanType").value;
    const creditScore = parseInt(document.getElementById("credit").value);
    const income = parseFloat(document.getElementById("income").value) || 0;
    const debt = parseFloat(document.getElementById("debt").value) || 0;

    // Rate calculation
    const baseRate = rates[loanType];
    const creditAdjustment = getCreditAdjustment(creditScore);
    const finalRate = baseRate + creditAdjustment;

    // Affordability calculation
    const maxMonthlyPayment = (income * 0.36) - debt;
    const homePrice = calculateHomePrice(maxMonthlyPayment, finalRate);
    const fhaDownPayment = homePrice * 0.035;
    const convDownPayment = homePrice * 0.20;

    // Display results
    updateResults({
        rate: finalRate,
        payment: maxMonthlyPayment,
        price: homePrice,
        fhaDown: fhaDownPayment,
        convDown: convDownPayment,
        loanType: loanType,
        creditScore: creditScore,
        lastUpdated: rates.lastUpdated
    });
}

// Helper functions
function getCreditAdjustment(score) {
    if (score >= 720) return 0.0;
    if (score >= 680) return 0.5;
    if (score >= 620) return 1.0;
    return 1.5;
}

function calculateHomePrice(monthlyPayment, annualRate) {
    const monthlyRate = annualRate / 100 / 12;
    const payments = 30 * 12;
    const loanAmount = monthlyPayment * ((1 - Math.pow(1 + monthlyRate, -payments)) / monthlyRate);
    return loanAmount / 0.965; // Accounting for 3.5% down
}

function updateResults(data) {
    document.getElementById("interestRate").textContent = data.rate.toFixed(2) + "%";
    document.getElementById("monthlyPayment").textContent = "$" + Math.round(data.payment).toLocaleString();
    document.getElementById("homePrice").textContent = "$" + Math.round(data.price).toLocaleString();
    document.getElementById("downPayment").textContent = "$" + 
        Math.round(data.fhaDown).toLocaleString() + " (3.5%) - $" + 
        Math.round(data.convDown).toLocaleString() + " (20%)";
    document.getElementById("rate-source").textContent = 
        `Tasas actualizadas el ${data.lastUpdated} via Freddie Mac PMMS`;
    
    // Update program tags
    const programTagsContainer = document.getElementById("programTags");
    programTagsContainer.innerHTML = '';
    
    const programs = [data.loanType];
    if (data.loanType === "FHA") programs.push("First-Time Buyer");
    if (data.creditScore < 620 || data.loanType === "ITIN") programs.push("Non-QM Options");
    
    programs.forEach(program => {
        const tag = document.createElement("span");
        tag.className = "program-tag";
        tag.textContent = program;
        programTagsContainer.appendChild(tag);
    });
    
    document.getElementById("results").style.display = 'block';
}
