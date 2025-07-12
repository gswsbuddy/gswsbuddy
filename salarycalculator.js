function calculateSalary() {
  const basic = parseFloat(document.getElementById('basic').value);
  const hraRate = parseFloat(document.getElementById('hra').value);
  const apgli = parseFloat(document.getElementById('apgli').value);

  if (isNaN(basic) || isNaN(hraRate) || isNaN(apgli)) {
    alert("Please fill in all fields correctly.");
    return;
  }

  // Earnings
  const hra = (hraRate / 100) * basic;
  const da = (33.67 / 100) * basic;
  const totalEarnings = basic + hra + da;

  // Deductions
  const gis = 15;
  const pt = 200;
  const ehs = 225;
  const cps = 0.10 * (basic + da);
  const totalDeductions = apgli + gis + pt + ehs + cps;

  const netSalary = totalEarnings - totalDeductions;

  // Display Output
  document.getElementById("output").innerHTML = `
    <h3>Salary Summary</h3>
    <p><strong>Basic Pay:</strong> ₹${basic.toFixed(2)}</p>
    <p><strong>HRA (${hraRate}%):</strong> ₹${hra.toFixed(2)}</p>
    <p><strong>DA (33.67%):</strong> ₹${da.toFixed(2)}</p>
    <p><strong>Total Earnings:</strong> ₹${totalEarnings.toFixed(2)}</p>
    <hr>
    <p><strong>APGLI:</strong> ₹${apgli.toFixed(2)}</p>
    <p><strong>GIS Fund:</strong> ₹15.00</p>
    <p><strong>Professional Tax:</strong> ₹200.00</p>
    <p><strong>EHS Subscription:</strong> ₹225.00</p>
    <p><strong>CPS (10% of Basic + DA):</strong> ₹${cps.toFixed(2)}</p>
    <p><strong>Total Deductions:</strong> ₹${totalDeductions.toFixed(2)}</p>
    <hr>
    <h3><strong>Net Salary:</strong> ₹${netSalary.toFixed(2)}</h3>
  `;
}
