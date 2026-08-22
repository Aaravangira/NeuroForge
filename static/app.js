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

        const response = await fetch("/upload/", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        loading.style.display = "none";

        if (!response.ok || !data.success) {

            alert(
                data.detail ||
                data.message ||
                "Invoice upload failed."
            );

            return;
        }

        // Backend currently returns `invoice`
        const document = data.invoice || data.document;

        if (!document) {
            throw new Error(
                "Upload succeeded but invoice data was not returned."
            );
        }

        result.textContent = JSON.stringify(
            document,
            null,
            4
        );

        await loadDashboard();
        await loadHistory();

    } catch (err) {

        loading.style.display = "none";

        console.error(
            "Upload error:",
            err
        );

        alert(
            err.message ||
            "Upload Failed"
        );
    }

});


// ======================================
// Dashboard
// ======================================

async function loadDashboard() {

    try {

        const response = await fetch("/dashboard");

        if (!response.ok) {
            throw new Error(
                "Dashboard request failed."
            );
        }

        const data = await response.json();

        invoiceCount.innerHTML =
            data.total_invoices ??
            data.count ??
            0;

        totalAmount.innerHTML =
            "₹ " +
            (
                data.total_amount ??
                data.totalAmount ??
                0
            );

    } catch (err) {

        console.error(
            "Dashboard error:",
            err
        );

        invoiceCount.innerHTML = "0";
        totalAmount.innerHTML = "₹ 0";
    }
}


// ======================================
// History
// ======================================

async function loadHistory() {

    try {

        const response = await fetch("/history");

        if (!response.ok) {
            throw new Error(
                "History request failed."
            );
        }

        const data = await response.json();

        historyTable.innerHTML = "";

        const invoices =
            Array.isArray(data)
                ? data
                : data.data || [];

        invoices.forEach(invoice => {

            historyTable.innerHTML += `
                <tr>
                    <td>${invoice.id ?? ""}</td>
                    <td>${invoice.vendor_name ?? ""}</td>
                    <td>${invoice.document_number ?? invoice.invoice_number ?? ""}</td>
                    <td>${invoice.document_date ?? invoice.invoice_date ?? ""}</td>
                    <td>${invoice.grand_total ?? ""}</td>
                </tr>
            `;

        });

    } catch (err) {

        console.error(
            "History error:",
            err
        );
    }
}