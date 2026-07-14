/* ==========================================
   AI Invoice Extractor
========================================== */

const uploadForm = document.getElementById("uploadForm");
const loading = document.getElementById("loading");
const result = document.getElementById("result");

const invoiceCount = document.getElementById("invoiceCount");
const totalAmount = document.getElementById("totalAmount");

const historyTable = document.getElementById("historyTable");
const searchBox = document.getElementById("searchBox");
const refreshBtn = document.getElementById("refreshBtn");

// ======================================
// Upload Invoice
// ======================================

uploadForm.addEventListener("submit", async function (e) {

    e.preventDefault();

    const file = document.getElementById("file").files[0];

    if (!file) {
        alert("Please select a file.");
        return;
    }

    loading.style.display = "block";

    result.textContent = "";

    const formData = new FormData();

    formData.append("file", file);

    try {

        const response = await fetch("/upload", {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        loading.style.display = "none";

        if (!data.success) {

            alert(data.message);

            return;

        }

        result.textContent = JSON.stringify(

            data.document,

            null,

            4

        );

        loadDashboard();

        loadHistory();

    }

    catch (err) {

        loading.style.display = "none";

        alert("Upload Failed");

        console.error(err);

    }

});

// ======================================
// Dashboard
// ======================================

async function loadDashboard() {

    const response = await fetch("/dashboard");

    const data = await response.json();

    invoiceCount.innerHTML = data.total_invoices;

    totalAmount.innerHTML = "₹ " + data.total_amount;

}

// ======================================
// History
// ======================================

async function loadHistory() {

    const response = await fetch("/history");

    const data = await response.json();

    historyTable.innerHTML = "";

    data.data.forEach(invoice => {

        historyTable.innerHTML += `

<tr>

<td>${invoice.id}</td>

<td>${invoice.vendor_name}</td>

<td>${invoice.invoice_number}</td>

<td>${invoice.invoice_date}</td>

<td>${invoice.grand_total}</td>

<td>

<button
class="btn btn-danger btn-sm"
onclick="deleteInvoice(${invoice.id})">

Delete

</button>

</td>

</tr>

`;

    });

}

// ======================================
// Delete
// ======================================

async function deleteInvoice(id){

    if(!confirm("Delete Invoice?"))

        return;

    await fetch("/invoice/"+id,{

        method:"DELETE"

    });

    loadHistory();

    loadDashboard();

}

// ======================================
// Search
// ======================================

searchBox.addEventListener("keyup", async function(){

    const keyword = this.value;

    if(keyword===""){

        loadHistory();

        return;

    }

    const response = await fetch(

        "/search?keyword="+encodeURIComponent(keyword)

    );

    const data = await response.json();

    historyTable.innerHTML="";

    data.data.forEach(invoice=>{

historyTable.innerHTML += `

<tr>

<td>${invoice.id}</td>

<td>${invoice.vendor_name}</td>

<td>${invoice.invoice_number}</td>

<td>${invoice.invoice_date}</td>

<td>${invoice.grand_total}</td>

<td>

<button
class="btn btn-danger btn-sm"
onclick="deleteInvoice(${invoice.id})">

Delete

</button>

</td>

</tr>

`;

    });

});

// ======================================
// Refresh
// ======================================

refreshBtn.addEventListener("click",function(){

    loadDashboard();

    loadHistory();

});

// ======================================
// Initial Load
// ======================================

loadDashboard();

loadHistory();