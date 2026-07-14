const form = document.getElementById("uploadForm");
const loading = document.getElementById("loading");
const result = document.getElementById("result");

form.addEventListener("submit", async function (e) {

    e.preventDefault();

    const fileInput = document.getElementById("file");

    if (fileInput.files.length === 0) {

        alert("Please select a document.");

        return;

    }

    const formData = new FormData();

    formData.append("file", fileInput.files[0]);

    loading.style.display = "block";

    result.innerHTML = "";

    try {

        const response = await fetch("/upload", {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        loading.style.display = "none";

        if (!data.success) {

            result.innerHTML = `
                <div class="alert alert-danger">
                    ${data.message}
                </div>
            `;

            return;

        }

        const doc = data.document;

        let html = `

        <div class="card shadow-lg invoice-card">

            <div class="invoice-header">

                <h3>📄 Document Information</h3>

            </div>

            <div class="invoice-body">

                <table class="table table-bordered">

                    <tr>
                        <th>Document Type</th>
                        <td>${doc.document_type ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Document Number</th>
                        <td>${doc.document_number ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Document Date</th>
                        <td>${doc.document_date ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Currency</th>
                        <td>${doc.currency ?? ""}</td>
                    </tr>

                </table>

                <hr>

                <h4>🏢 Vendor</h4>

                <table class="table table-bordered">

                    <tr>
                        <th>Name</th>
                        <td>${doc.vendor?.name ?? ""}</td>
                    </tr>

                    <tr>
                        <th>GST</th>
                        <td>${doc.vendor?.gst ?? ""}</td>
                    </tr>

                    <tr>
                        <th>PAN</th>
                        <td>${doc.vendor?.pan ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Phone</th>
                        <td>${doc.vendor?.phone ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Email</th>
                        <td>${doc.vendor?.email ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Address</th>
                        <td>${doc.vendor?.address ?? ""}</td>
                    </tr>

                </table>

                <hr>

                <h4>👤 Buyer</h4>

                <table class="table table-bordered">

                    <tr>
                        <th>Name</th>
                        <td>${doc.buyer?.name ?? ""}</td>
                    </tr>

                    <tr>
                        <th>GST</th>
                        <td>${doc.buyer?.gst ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Phone</th>
                        <td>${doc.buyer?.phone ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Email</th>
                        <td>${doc.buyer?.email ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Address</th>
                        <td>${doc.buyer?.address ?? ""}</td>
                    </tr>

                </table>

                <hr>

                <h4>💰 Amount Details</h4>

                <table class="table table-bordered">

                    <tr>
                        <th>Subtotal</th>
                        <td>${doc.amounts?.subtotal ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Discount</th>
                        <td>${doc.amounts?.discount ?? ""}</td>
                    </tr>

                    <tr>
                        <th>CGST</th>
                        <td>${doc.amounts?.cgst ?? ""}</td>
                    </tr>

                    <tr>
                        <th>SGST</th>
                        <td>${doc.amounts?.sgst ?? ""}</td>
                    </tr>

                    <tr>
                        <th>IGST</th>
                        <td>${doc.amounts?.igst ?? ""}</td>
                    </tr>

                    <tr>
                        <th>VAT</th>
                        <td>${doc.amounts?.vat ?? ""}</td>
                    </tr>

                    <tr>
                        <th>Grand Total</th>
                        <td><strong>${doc.amounts?.grand_total ?? ""}</strong></td>
                    </tr>

                    <tr>
                        <th>Amount Paid</th>
                        <td>${doc.amounts?.amount_paid ?? ""}</td>
                    </tr>

                </table>

                <hr>

                <h4>📦 Items</h4>

                <table class="table table-striped table-bordered">

                    <thead>

                        <tr>

                            <th>Description</th>

                            <th>Qty</th>

                            <th>Price</th>

                            <th>Total</th>

                        </tr>

                    </thead>

                    <tbody>

        `;

        if (doc.items && doc.items.length > 0) {

            doc.items.forEach(item => {

                html += `

                    <tr>

                        <td>${item.description || item.title || ""}</td>

                        <td>${item.quantity ?? ""}</td>

                        <td>${item.unit_price ?? ""}</td>

                        <td>${item.total ?? ""}</td>

                    </tr>

                `;

            });

        }

        html += `

                    </tbody>

                </table>

            </div>

        </div>

        `;

        result.innerHTML = html;

    }
    

    catch (error) {

        loading.style.display = "none";

        result.innerHTML = `
            <div class="alert alert-danger">
                ${error}
            </div>
        `;

    }
    html += `

<br>

<a
href="/download-excel"
class="btn btn-success">

Download Excel

</a>

`;

});