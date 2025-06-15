function generatePDF() {
    let { jsPDF } = window.jspdf;
    let doc = new jsPDF();

    let name = document.getElementById("name").value;
    let designation = document.getElementById("designation").value;
    let location = document.getElementById("location").value;

    if (!name || !designation || !location) {
        alert("Please fill in all fields before generating the PDF.");
        return;
    }

    let letter = `
        Me, I ${name}, working as ${designation} at ${location} Grama Sachivalayam.
    `;

    doc.text(letter, 20, 20);
    doc.save("Generated_Letter.pdf");

    // Display the preview on the page
    document.getElementById("letterOutput").innerText = letter;
}
