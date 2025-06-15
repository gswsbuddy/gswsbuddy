function setIncrementDate() {
    let incrementMonth = document.getElementById("incrementMonth").value;
    if (incrementMonth) {
        let currentYear = new Date().getFullYear();
        document.getElementById("lastIncrementDate").value = `${currentYear}-${getMonthNumber(incrementMonth)}-01`;
    }
}

function getMonthNumber(monthName) {
    const months = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12"
    };
    return months[monthName];
}

function generatePDF() {
    let { jsPDF } = window.jspdf;
    let doc = new jsPDF();

    let employeeName = document.getElementById("employeeName").value;
    let designation = document.getElementById("designation").value;
    let secretariat = document.getElementById("secretariat").value;
    let mandal = document.getElementById("mandal").value;
    let district = document.getElementById("district").value;
    let srMaintainedBy = document.getElementById("srMaintainedBy").value;
    let srLocation = document.getElementById("srLocation").value;
    let joiningDate = document.getElementById("joiningDate").value;
    let incrementMonth = document.getElementById("incrementMonth").value;
    let lastIncrementDate = document.getElementById("lastIncrementDate").value;
    let basicPay = document.getElementById("basicPay").value;

    if (!employeeName || !designation || !secretariat || !mandal || !district || !srMaintainedBy || !srLocation || !joiningDate || !incrementMonth || !lastIncrementDate || !basicPay) {
        alert("Please fill in all fields before generating the PDF.");
        return;
    }

    let letter = `
        Date: ${new Date().toLocaleDateString()}
        
        From:
        ${employeeName}
        ${designation}
        ${secretariat}
        ${mandal}
        ${district}
        
        To: 
        ${srMaintainedBy}
        ${srLocation}

        Respected Sir,

        Subject: Request for sanction of Annual Grade Increment W.E.F ${incrementMonth} - Regarding.

        I, ${employeeName}, working as ${designation} at ${secretariat}, ${mandal}, ${district}, hereby submit my request for the sanction of my Annual Grade Increment effective ${incrementMonth}.
        
        I have been working in the present cadre since ${joiningDate}. My Annual Grade Increment falls in the month of ${incrementMonth}. I have successfully completed 1 year of service from ${lastIncrementDate} without any break. My present basic pay is ₹${basicPay}.

        Hence, I request you to sanction my periodical increment and issue necessary orders at the earliest so as to enable me to present bills to the Sub-Treasury Office (STO).
        
        Thanking you, sir.

        Yours sincerely,
        ${employeeName}
        ${designation}
        ${secretariat}
        ${mandal}
        ${district}
    `;

    doc.setFont("times", "normal");
    doc.setFontSize(12);
    let marginLeft = 15;
    let verticalSpace = 10;
    doc.text(`To:\n${srMaintainedBy}\n${srLocation}`, 140, verticalSpace);
    verticalSpace += 20;
    doc.text(doc.splitTextToSize(letter, 180), marginLeft, verticalSpace);
    doc.save("Increment_Request_Letter.pdf");

    document.getElementById("letterOutput").innerText = letter;
}
